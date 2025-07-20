import sys
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from loguru import logger

from .apartments import filter_apartments, get_apartments, send_apartment
from .storage import Settings


def main():
    logger.add(sys.stdout, level="DEBUG", colorize=sys.stdout.isatty(), backtrace=True, diagnose=False)

    settings = Settings.load()
    
    token = os.environ.get("TELEGRAM_TOKEN")
    admin_user_id = os.environ.get("ADMIN_USER_ID")
    if not token:
        logger.error("Error: TELEGRAM_TOKEN environment variable not set.")
        return
    if not admin_user_id: 
        logger.error("Error: ADMIN_USER_ID environment variable not set.")
        return

    application = ApplicationBuilder().token(token).build()

    async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        sender = update.effective_user
        if not chat or not sender:
            return
        
        if sender.id != int(admin_user_id):
            await context.bot.send_message(
                chat_id=chat.id,
                text="⚠️ <b>Unauthorized:</b> You are not authorized to use this command.",
                parse_mode=ParseMode.HTML
            )
            return

        settings.chat_id = chat.id
        settings.save()
        await context.bot.send_message(
            chat_id=chat.id,
            text="✅ <b>Chat ID Updated!</b>\nChat ID has been set for future notifications.",
            parse_mode=ParseMode.HTML
        )

    

    async def set_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        sender = update.effective_user
        if not chat or not sender:
            return
        logger.info(f"/filter command received from user {sender.id} with args: {context.args}")
        if sender.id != int(admin_user_id):
            logger.warning(f"Unauthorized /filter attempt by user {sender.id}")
            await context.bot.send_message(
                chat_id=chat.id,
                text="⚠️ <b>Unauthorized:</b> You are not authorized to use this command.",
                parse_mode=ParseMode.HTML
            )
            return
        if not context.args or len(context.args) == 0:
            # Display current filter settings
            filters = settings.apartment_filter
            colonies = filters.colony
            rooms = filters.apartment_rooms
            min_area = filters.min_apartment_area
            max_area = filters.max_apartment_area
            min_price = filters.min_price
            max_price = filters.max_price

            message_lines = [
                "<b>Current Filters:</b>\n",
                f"<b>Colonies:</b> {', '.join(colonies) if colonies else 'None'}",
                (f"<b>Rooms:</b> {rooms[0]}–{rooms[1]}" if len(rooms) == 2 else "<b>Rooms:</b> None"),
                f"<b>Area:</b> {min_area}–{max_area} m²",
                f"<b>Price:</b> {min_price}–{max_price} CHF"
            ]
            await context.bot.send_message(
                chat_id=chat.id,
                text='\n'.join(message_lines),
                parse_mode=ParseMode.HTML
            )
            return
        subcommand = context.args[0].lower()
        if subcommand == "colonies":
            raw_args = context.args[1:]
            new_list: list[str] = []
            for arg in raw_args:
                for c in arg.split(","):
                    c = c.strip()
                    if c:
                        new_list.append(c)
            logger.info(f"Setting colonies filter to: {new_list}")
            settings.apartment_filter.colony = new_list
            settings.save()
            new_list_str = ", ".join(new_list) if new_list else "None"
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"✅ <b>Colonies filter set to:</b> {new_list_str}",
                parse_mode=ParseMode.HTML
            )
        elif subcommand == "rooms":
            if len(context.args) < 2:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text="⚠️ <b>Usage:</b> /filter rooms <min>-<max>\ne.g. <code>/filter rooms 2-3.5</code>",
                    parse_mode=ParseMode.HTML
                )
                return
            try:
                min_str, max_str = context.args[1].split("-", 1)
                min_rooms = float(min_str)
                max_rooms = float(max_str)
            except ValueError:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text="⚠️ <b>Invalid format:</b> Use <code>/filter rooms min-max</code>, e.g. <code>2-3.5</code>",
                    parse_mode=ParseMode.HTML
                )
                return
            settings.apartment_filter.apartment_rooms = [min_rooms, max_rooms]
            logger.info(f"Setting rooms filter range to: {min_rooms}-{max_rooms}")
            settings.save()
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"✅ <b>Rooms filter set to:</b> {min_rooms}-{max_rooms}",
                parse_mode=ParseMode.HTML
            )
        elif subcommand == "area":
            if len(context.args) < 2:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text="⚠️ <b>Usage:</b> /filter area <min>-<max>\ne.g. <code>/filter area 0-80</code>",
                    parse_mode=ParseMode.HTML
                )
                return
            try:
                min_str, max_str = context.args[1].split("-", 1)
                min_area = float(min_str)
                max_area = float(max_str)
            except ValueError:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text="⚠️ <b>Invalid format:</b> Use <code>/filter area min-max</code>, e.g. <code>0-80</code>",
                    parse_mode=ParseMode.HTML
                )
                return
            settings.apartment_filter.min_apartment_area = min_area
            settings.apartment_filter.max_apartment_area = max_area
            logger.info(f"Setting area filter range to: {min_area}-{max_area}")
            settings.save()
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"✅ <b>Area filter set to:</b> {min_area}-{max_area} m²",
                parse_mode=ParseMode.HTML
            )
        elif subcommand == "price":
            if len(context.args) < 2:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text="⚠️ <b>Usage:</b> /filter price <min>-<max>\ne.g. <code>/filter price 0-2000</code>",
                    parse_mode=ParseMode.HTML
                )
                return
            try:
                min_str, max_str = context.args[1].split("-", 1)
                min_price = float(min_str)
                max_price = float(max_str)
            except ValueError:
                await context.bot.send_message(
                    chat_id=chat.id,
                    text="⚠️ <b>Invalid format:</b> Use <code>/filter price min-max</code>, e.g. <code>0-2000</code>",
                    parse_mode=ParseMode.HTML
                )
                return
            settings.apartment_filter.min_price = min_price
            settings.apartment_filter.max_price = max_price
            logger.info(f"Setting price filter range to: {min_price}-{max_price}")
            settings.save()
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"✅ <b>Price filter set to:</b> {min_price}-{max_price} CHF",
                parse_mode=ParseMode.HTML
            )
        else:
            logger.warning(f"Unknown filter type '{subcommand}' in /filter command by {sender.id}")
            await context.bot.send_message(
                chat_id=chat.id,
                text="❓ <b>Unknown filter type:</b> Available types: <code>colonies</code>, <code>rooms</code>, <code>area</code>, <code>price</code>",
                parse_mode=ParseMode.HTML
            )

    async def list_apartments(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        sender = update.effective_user
        if not chat or not sender:
            return
        logger.info(f"/list command received from user {sender.id}")

        apartments = await get_apartments()
        logger.info(f"Found {len(apartments)} apartments")

        filtered_apartments = [a for a in apartments if a.apartment_status != "assigned"]
        await context.bot.send_message(
            chat_id=chat.id,
            text=f"🔍 <b>Found {len(filtered_apartments)}/{len(apartments)}</b> available apartments",
            parse_mode=ParseMode.HTML
        )
        for apartment in filtered_apartments:
            await send_apartment(context.bot, chat.id, apartment)

    async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        sender = update.effective_user
        if not chat or not sender:
            return
        logger.info(f"/check command received from user {sender.id}")

        new_apartments = await get_apartments()
        logger.info(f"Found {len(new_apartments)} apartments")

        new_filtered_apartments = filter_apartments(new_apartments, settings.apartment_filter)
        settings.apartments = new_apartments
        settings.save()

        await context.bot.send_message(
            chat_id=chat.id,
            text=f"🔍 <b>Found {len(new_filtered_apartments)}/{len(new_apartments)}</b> apartments matching your filters",
            parse_mode=ParseMode.HTML
        )
        for apartment in new_filtered_apartments:
            await send_apartment(context.bot, chat.id, apartment)

    async def reset_apartments(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        sender = update.effective_user
        if not chat or not sender:
            return
        logger.info(f"/resetapartments command received from user {sender.id}")
        settings.apartments = []
        settings.save()

    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        sender = update.effective_user
        if not chat or not sender:
            return
        if sender.id != int(admin_user_id):
            await context.bot.send_message(
                chat_id=chat.id,
                text="⚠️ <b>Unauthorized:</b> You are not authorized to use this command.",
                parse_mode=ParseMode.HTML
            )
            return
        help_text = (
            "<b>🤖 Bot Commands Help</b>\n\n"
            "<b>/subscribe</b> - Register this chat for apartment notifications.\n"
            "<b>/filter</b> - View or set filters:\n"
            "<code>/filter</code> - Show current filters\n"
            "<code>/filter colonies A,B,C</code> - Set colonies filter\n"
            "<code>/filter rooms min-max</code> - Set rooms range\n"
            "<code>/filter area min-max</code> - Set area range\n"
            "<code>/filter price min-max</code> - Set price range\n"
            "<b>/check</b> - Manually trigger an apartment check.\n"
            "<b>/list</b> - List all available apartments.\n"
            "<b>/resetapartments</b> - Reset the saved list of apartments - this will trigger a notification for all matching apartments on the next check.\n"
            "<b>/help</b> - Show this help message."
        )
        await context.bot.send_message(
            chat_id=chat.id,
            text=help_text,
            parse_mode=ParseMode.HTML
        )


    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("filter", set_filter))
    application.add_handler(CommandHandler("list", list_apartments))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CommandHandler("resetapartments", reset_apartments))
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling()