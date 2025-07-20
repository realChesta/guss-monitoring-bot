import os
from pydantic import BaseModel

from gussbot.types import Apartment, ApartmentFilter


class Settings(BaseModel):
    chat_id: int | None = None
    apartments: list[Apartment]
    apartment_filter: ApartmentFilter

    @classmethod
    def get_file_path(cls) -> str:
        return os.path.join(os.environ.get("SETTINGS_DIR", "settings"), "settings.json")

    
    @classmethod
    def load(cls) -> "Settings":
        try:
            return Settings.model_validate_json(open(cls.get_file_path()).read())
        except FileNotFoundError:
            return Settings(apartments=[], apartment_filter=ApartmentFilter(colony=[], apartment_rooms=[], min_apartment_area=0, max_apartment_area=0, min_price=0, max_price=0))
    
    def save(self) -> None:
        open(self.get_file_path(), "w").write(self.model_dump_json())
        
        
      