from typing import Optional
from pydantic import BaseModel

class Address(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None  # Make 'country' optional

class Student(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[Address] = None