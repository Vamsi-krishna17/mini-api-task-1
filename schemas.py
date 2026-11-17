
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TripCreate(BaseModel):
    """Schema for creating a new trip."""

    traveller: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=1, max_length=100)
    budget_inr: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    travel_date: date

    @field_validator("traveller", "country")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value

    @field_validator("travel_date")
    @classmethod
    def validate_travel_date(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Travel date cannot be in the past.")

        return value


class TripUpdate(BaseModel):
    """Schema for partially updating an existing trip."""

    traveller: str | None = Field(default=None, min_length=1, max_length=100)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    budget_inr: Decimal | None = Field(
        default=None, gt=0, max_digits=12, decimal_places=2
    )
    travel_date: date | None = None

    @field_validator("traveller", "country")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("This field cannot be null.")

        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value

    @field_validator("budget_inr")
    @classmethod
    def validate_optional_budget(
        cls, value: Decimal | None
    ) -> Decimal | None:
        if value is None:
            raise ValueError("Budget cannot be null.")

        return value

    @field_validator("travel_date")
    @classmethod
    def validate_optional_date(cls, value: date | None) -> date | None:
        if value is None:
            raise ValueError("Travel date cannot be null.")

        if value < date.today():
            raise ValueError("Travel date cannot be in the past.")

        return value

    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")

        return self


class TripOut(BaseModel):
    """Schema for returning trip information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    traveller: str
    country: str
    currency_code: str
    budget_inr: Decimal
    travel_date: date
    created_at: datetime

    rate: float
    budget_local: Decimal
