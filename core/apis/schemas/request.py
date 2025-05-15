from pydantic import BaseModel, Field
from typing import List

class ContactDetails(BaseModel):
    mobile_number: str = Field(min_length=10, max_length=15)
    full_name: str = Field(min_length=3)

class RequestCall(BaseModel):
    call_list: List[ContactDetails] = Field(min_items=1)