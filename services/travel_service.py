
import re

from clients.countries_client import CountriesClient
from clients.rates_client import RatesClient
from exceptions import CountryNotFoundError, ExternalAPIError


class TravelService:
    """Combines country information and exchange-rate operations."""

    def __init__(
        self,
        countries_client: CountriesClient,
        rates_client: RatesClient,
    ):
        self.countries_client = countries_client
        self.rates_client = rates_client

    async def get_country_details(self, country: str) -> dict:
        """Retrieve country name, currency and capital."""

        country = country.strip()

        if not country:
            raise CountryNotFoundError(
                "Country name cannot be empty."
            )

        country_name, currency = (
            await self.countries_client.get_currency_details(country)
        )

        capital = await self.countries_client.get_capital(country)

        return {
            "country": country_name,
            "currency": currency,
            "capital": capital,
        }

    async def convert_budget(
        self,
        country: str,
        budget_inr: float,
    ) -> dict:
        """Convert an INR budget into the country's local currency."""

        country_details = await self.get_country_details(country)

        currency = country_details["currency"]

        # Validate the currency code returned by CountriesNow.
        if (
            not isinstance(currency, str)
            or not re.fullmatch(r"[A-Za-z]{3}", currency)
        ):
            raise ExternalAPIError(
                "The country API returned an invalid currency code."
            )

        currency = currency.upper()

        # Fetch the exchange rate from INR to the country's currency.
        rate = await self.rates_client.get_exchange_rate(
            from_currency="INR",
            to_currency=currency,
        )

        # Calculate the converted budget.
        budget_local = round(budget_inr * rate, 2)

        return {
            "country": country_details["country"],
            "capital": country_details["capital"],
            "currency": currency,
            "rate": rate,
            "budget_inr": budget_inr,
            "budget_local": budget_local,
        }
