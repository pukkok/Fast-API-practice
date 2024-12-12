from pydantic import BaseModel

# MongoDB Models
class HolidayModel(BaseModel):
    base_year: int
    item: dict