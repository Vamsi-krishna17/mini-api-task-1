
import httpx

from config import settings
from exceptions import CountryNotFoundError, ExternalAPIError


class CountriesClient:
    """Adapter for the CountriesNow API."""

    def __init__(self):
        self.base_url = settings.countries_api
        self.timeout = settings.timeout

    async def _fetch_country_data(self, endpoint: str, country: str) -> dict:
        url = f"{self.base_url}/{endpoint}/q"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params={"country": country},
                )

            response.raise_for_status()
            result = response.json()

            if result.get("error"):
                raise CountryNotFoundError(
                    f"Country '{country}' was not found."
                )

            data = result.get("data")

            if not isinstance(data, dict):
                raise CountryNotFoundError(
                    "Country details are incomplete or unavailable."
                )

            return data

        except (CountryNotFoundError, ExternalAPIError):
            raise

        except httpx.TimeoutException as exc:
            raise ExternalAPIError(
                "External API request timed out. Please try again."
            ) from exc

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (400, 404, 422):
                raise CountryNotFoundError(
                    "Requested information was not found."
                ) from exc

            raise ExternalAPIError(
                "External API is currently unavailable."
            ) from exc

        except (httpx.RequestError, ValueError) as exc:
            raise ExternalAPIError(
                "Could not connect to the external API or read its response."
            ) from exc

    async def get_currency_details(self, country: str) -> tuple[str, str]:
        data = await self._fetch_country_data("currency", country)

        currency = data.get("currency")
        country_name = data.get("name")

        if not currency or not country_name:
            raise CountryNotFoundError(
                "Country details are incomplete or unavailable."
            )

        return country_name, currency

    async def get_capital(self, country: str) -> str:
        data = await self._fetch_country_data("capital", country)

        capital = data.get("capital")

        if not capital:
            raise CountryNotFoundError(
                "Country details are incomplete or unavailable."
            )

        return capital
