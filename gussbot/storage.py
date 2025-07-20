from pydantic import BaseModel

from gussbot.types import Apartment, ApartmentFilter


class Settings(BaseModel):
    chat_id: int | None = None
    apartments: list[Apartment]
    apartment_filter: ApartmentFilter

    
    @classmethod
    def load(cls) -> "Settings":
        try:
            return Settings.model_validate_json(open("settings.json").read())
        except FileNotFoundError:
            return Settings(apartments=[], apartment_filter=ApartmentFilter(colony=[], apartment_rooms=[], min_apartment_area=0, max_apartment_area=0, min_price=0, max_price=0))
    
    def save(self) -> None:
        open("settings.json", "w").write(self.model_dump_json())
        
        
      