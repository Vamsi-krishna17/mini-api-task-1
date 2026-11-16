
from fastapi import FastAPI, HTTPException, Query

from clients.countries_client import CountriesClient
from clients.rates_client import RatesClient
from exceptions import CountryNotFoundError, ExternalAPIError
from services.travel_service import TravelService


app = FastAPI(
    title="Country Mini Budget Planner API",
    description=(
        "An API to retrieve country details and "
        "convert an INR budget into local currency."
    ),
    version="1.0.0",
)


# Initialize clients and inject them into the service.
countries_client = CountriesClient()
rates_client = RatesClient()

travel_service = TravelService(
    countries_client=countries_client,
    rates_client=rates_client,
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Mini API Project is running successfully.",
    }


@app.get("/countries/{name}")
async def get_country(name: str):
    try:
        return await travel_service.get_country_details(name)

    except CountryNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ExternalAPIError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


@app.get("/roam/{name}")
async def roam(
    name: str,
    budget_inr: float = Query(..., gt=0),
):
    try:
        return await travel_service.convert_budget(
            country=name,
            budget_inr=budget_inr,
        )

    except CountryNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ExternalAPIError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc
