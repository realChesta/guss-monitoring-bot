from pydantic import BaseModel
from typing import List
from pydantic import HttpUrl


class Apartment(BaseModel):
    apartment_rentalgross: float
    apartment_area: float
    building_adress: str
    apartment_status: str
    apartment_rooms: float
    apartment_id: int
    apartment_floor: str
    apartment_balcony: float
    apartment_title: str
    url: HttpUrl
    pdf: HttpUrl
    image: HttpUrl
    colony: str
    parking: bool

class ApartmentsPayload(BaseModel):
    colony: List[str]
    apartment_rooms: List[float]
    min_apartment_area: float
    max_apartment_area: float
    min_price: float
    max_price: float
    list: List[Apartment]

class ApartmentFilter(BaseModel):
    colony: List[str]
    apartment_rooms: List[float]
    min_apartment_area: float
    max_apartment_area: float
    min_price: float
    max_price: float