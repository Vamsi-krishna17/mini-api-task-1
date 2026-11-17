
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import Trip

class TripRepository:
    """Handles all database operations for trips."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_dict(trip: Trip) -> dict:
        """Convert a database model into a plain Python dictionary."""

        return {
            "id": trip.id,
            "traveller": trip.traveller,
            "country": trip.country,
            "currency_code": trip.currency_code,
            "budget_inr": Decimal(trip.budget_inr),
            "travel_date": trip.travel_date,
            "created_at": trip.created_at,
        }

    def add(
        self,
        traveller: str,
        country: str,
        currency_code: str,
        budget_inr: Decimal,
        travel_date: date,
    ) -> dict:
        """Insert a new trip into the database."""

        trip = Trip(
            traveller=traveller,
            country=country,
            currency_code=currency_code,
            budget_inr=budget_inr,
            travel_date=travel_date,
        )

        try:
            self.db.add(trip)
            self.db.commit()
            self.db.refresh(trip)

            return self._to_dict(trip)

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def get(self, trip_id: int) -> dict | None:
        """Retrieve one trip using its ID."""

        trip = self.db.get(Trip, trip_id)

        if trip is None:
            return None

        return self._to_dict(trip)

    def list(self) -> list[dict]:
        """Retrieve all trips."""

        statement = select(Trip).order_by(Trip.id)
        trips = self.db.scalars(statement).all()

        return [self._to_dict(trip) for trip in trips]

    def update(self, trip_id: int, data: dict) -> dict | None:
        """Update only the supplied trip fields."""

        trip = self.db.get(Trip, trip_id)

        if trip is None:
            return None

        try:
            for field, value in data.items():
                setattr(trip, field, value)

            self.db.commit()
            self.db.refresh(trip)

            return self._to_dict(trip)

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete(self, trip_id: int) -> bool:
        """Delete a trip using its ID."""

        trip = self.db.get(Trip, trip_id)

        if trip is None:
            return False

        try:
            self.db.delete(trip)
            self.db.commit()

            return True

        except SQLAlchemyError:
            self.db.rollback()
            raise