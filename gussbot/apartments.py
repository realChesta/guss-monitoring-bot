import re
import httpx
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from .types import Apartment, ApartmentFilter, ApartmentsPayload


async def get_apartments() -> list[Apartment]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://imguss.ch/wohnen/wohnungen/wohnungsfinder/")
        resp.raise_for_status()

        # the response is a html page with a list of apartments,
        # but the apartments are conveniently hidden in a json object
        json_obj = re.search(r':apartments=\'(.*?)\'', resp.text)
        if not json_obj or not json_obj.group(1):
            raise ValueError("Could not find json object in response")
        
        apartment_payload = ApartmentsPayload.model_validate_json(json_obj.group(1))

        return apartment_payload.list

def filter_apartments(apartments: list[Apartment], filter: ApartmentFilter) -> list[Apartment]:
    filtered_apartments = [a for a in apartments if a.apartment_status != "assigned"]
    
    # filter colony
    if len(filter.colony) > 0:
        filtered_apartments = [a for a in filtered_apartments if a.colony in filter.colony]
    
    # filter rooms
    if len(filter.apartment_rooms) > 0:
        filtered_apartments = [a for a in filtered_apartments if a.apartment_rooms >= filter.apartment_rooms[0] and a.apartment_rooms <= filter.apartment_rooms[1]]

    # filter area
    if filter.min_apartment_area and filter.max_apartment_area:
        filtered_apartments = [a for a in filtered_apartments if a.apartment_area >= filter.min_apartment_area and a.apartment_area <= filter.max_apartment_area]

    # filter price
    if filter.min_price and filter.max_price:
        filtered_apartments = [a for a in filtered_apartments if a.apartment_rentalgross >= filter.min_price and a.apartment_rentalgross <= filter.max_price]

    return filtered_apartments

async def send_apartment(bot: Bot, chat_id: int, apartment: Apartment):
    buttons = [
        [InlineKeyboardButton("View PDF", url=str(apartment.pdf))],
        [InlineKeyboardButton("Listings Page", url="https://imguss.ch/wohnen/wohnungen/wohnungsfinder/")],
    ]
    markup = InlineKeyboardMarkup(buttons)
    rent_value = apartment.apartment_rentalgross
    try:
        rent_int = int(rent_value)
        rent_formatted = f"{rent_int:,}".replace(",", "'")
    except (TypeError, ValueError):
        rent_formatted = str(rent_value)
    caption = (
        f"<b>{apartment.apartment_title} // {apartment.apartment_status}</b>\n\n"
        f"<b>🛏 Rooms:</b> {apartment.apartment_rooms}\n"
        f"<b>📐 Area:</b> {apartment.apartment_area}m²\n"
        f"<b>🌅 Balcony:</b> {apartment.apartment_balcony} m²\n"
        f"<b>💰 Rent:</b> {rent_formatted}.-\n"
        f"<b>📍 Address:</b> {apartment.building_adress}\n"
        f"<b>🚪 Floor:</b> {apartment.apartment_floor}\n"
        f"<b>🏠 Colony:</b> {apartment.colony}\n"
        f"<b>🚗 Parking:</b> {'Yes' if apartment.parking else 'No'}\n"
    )
    await bot.send_photo(chat_id=chat_id, photo=str(apartment.image), caption=caption, parse_mode=ParseMode.HTML, reply_markup=markup)