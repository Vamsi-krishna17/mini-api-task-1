
import re
from decimal import Decimal, ROUND_HALF_UP

from loguru import logger

from clients.countries_client import CountriesClient
from clients.rates_client import RatesClient
from exceptions import (
    CountryNotFoundError,
    ExternalAPIError,
    TripNotFoundError,
)
from repositories.trip_repository import TripRepository


class TripService:
    """Handles trip creation, retrieval, updating and deletion."""

    def __init__(
        self,
        repository: TripRepository,
        countries_client: CountriesClient,
        rates_client: RatesClient,
    ):
        self.repository = repository
        self.countries_client = countries_client
        self.rates_client = rates_client

    async def _get_currency_code(self, country: str) -> str:
        """Retrieve and validate a country's currency code."""

        _, currency = await self.countries_client.get_currency_details(
            country
        )

        if (
            not isinstance(currency, str)
            or not re.fullmatch(r"[A-Za-z]{3}", currency)
        ):
            raise ExternalAPIError(
                "The country API returned an invalid currency code."
            )

        return currency.upper()

    async def _get_exchange_rate(self, currency_code: str) -> float:
        """Get the exchange rate from INR to the target currency."""

        if currency_code == "INR":
            return 1.0

        return await self.rates_client.get_exchange_rate(
            from_currency="INR",
            to_currency=currency_code,
        )

    @staticmethod
    def _add_conversion(trip: dict, rate: float) -> dict:
        """Add exchange rate and converted budget to a trip."""

        local_budget = (
            Decimal(str(trip["budget_inr"])) * Decimal(str(rate))
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            **trip,
            "rate": rate,
            "budget_local": local_budget,
        }

    async def create_trip(self, data: dict) -> dict:
        """Look up currency and save a new trip."""

        currency_code = await self._get_currency_code(data["country"])

        trip = self.repository.add(
            traveller=data["traveller"],
            country=data["country"],
            currency_code=currency_code,
            budget_inr=data["budget_inr"],
            travel_date=data["travel_date"],
        )

        rate = await self._get_exchange_rate(currency_code)

        logger.info(
            "Trip created | ID: {} | Country: {}",
            trip["id"],
            trip["country"],
        )

        return self._add_conversion(trip, rate)

    async def get_trip(self, trip_id: int) -> dict:
        """Retrieve one trip with its converted budget."""

        trip = self.repository.get(trip_id)

        if trip is None:
            raise TripNotFoundError(
                f"Trip with ID {trip_id} was not found."
            )

        rate = await self._get_exchange_rate(trip["currency_code"])

        return self._add_conversion(trip, rate)

    async def list_trips(self) -> list[dict]:
        """Retrieve all trips and convert budgets efficiently."""

        trips = self.repository.list()

        # Cache rates so each distinct currency is requested only once.
        rate_cache = {}

        for trip in trips:
            currency_code = trip["currency_code"]

            if currency_code not in rate_cache:
                rate_cache[currency_code] = (
                    await self._get_exchange_rate(currency_code)
                )

        return [
            self._add_conversion(
                trip,
                rate_cache[trip["currency_code"]],
            )
            for trip in trips
        ]

    async def update_trip(self, trip_id: int, data: dict) -> dict:
        """Update a trip and refresh its currency if country changes."""

        existing_trip = self.repository.get(trip_id)

        if existing_trip is None:
            raise TripNotFoundError(
                f"Trip with ID {trip_id} was not found."
            )

        if "country" in data:
            data["currency_code"] = await self._get_currency_code(
                data["country"]
            )

        updated_trip = self.repository.update(trip_id, data)

        if updated_trip is None:
            raise TripNotFoundError(
                f"Trip with ID {trip_id} was not found."
            )

        rate = await self._get_exchange_rate(
            updated_trip["currency_code"]
        )

        logger.info("Trip updated | ID: {}", trip_id)

        return self._add_conversion(updated_trip, rate)

    async def delete_trip(self, trip_id: int) -> None:
        """Delete a trip by its ID."""

        deleted = self.repository.delete(trip_id)

        if not deleted:
            raise TripNotFoundError(
                f"Trip with ID {trip_id} was not found."
            )

        logger.info("Trip deleted | ID: {}", trip_id)
