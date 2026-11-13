
import os
import re

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query

# Load environment variables from .env
load_dotenv()

COUNTRIES_API = os.getenv(
    "COUNTRIES_API",
    "https://countriesnow.space/api/v0.1/countries"
)

FRANKFURTER_API = os.getenv(
    "FRANKFURTER_API",
    "https://api.frankfurter.dev/v2"
)

TIMEOUT = 10.0

app = FastAPI(
    title="Country Mini Budget Planner API",
    description="An API to retrieve country details and convert an INR budget into local currency.",
    version="1.0.0"
)


# Helper function to communicate with external APIs
async def fetch_json(url: str):
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=503,
            detail="External API request timed out. Please try again."
        )

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in (400, 404, 422):
            raise HTTPException(
                status_code=404,
                detail="Requested information was not found."
            )

        raise HTTPException(
            status_code=503,
            detail="External API is currently unavailable."
        )

    except (httpx.RequestError, ValueError):
        raise HTTPException(
            status_code=503,
            detail="Could not connect to the external API or read its response."
        )


# Helper function to get country details
async def get_country_details(country: str):
    country = country.strip()

    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country name cannot be empty."
        )

    currency_url = (
        f"{COUNTRIES_API}/currency/q"
    )

    capital_url = (
        f"{COUNTRIES_API}/capital/q"
    )

    currency_data = await fetch_json(
        f"{currency_url}?country={country}"
    )

    capital_data = await fetch_json(
        f"{capital_url}?country={country}"
    )

    # Check whether CountriesNow returned an error
    if currency_data.get("error") or capital_data.get("error"):
        raise HTTPException(
            status_code=404,
            detail=f"Country '{country}' was not found."
        )

    currency = currency_data.get("data", {}).get("currency")
    capital = capital_data.get("data", {}).get("capital")
    country_name = currency_data.get("data", {}).get("name")

    if not currency or not capital or not country_name:
        raise HTTPException(
            status_code=404,
            detail="Country details are incomplete or unavailable."
        )

    return {
        "country": country_name,
        "currency": currency,
        "capital": capital
    }


# Endpoint 1: Health check of apis
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Mini API Project is running successfully."
    }


# Endpoint 2: country and capital details
@app.get("/countries/{name}")
async def get_country(name: str):
    return await get_country_details(name)


# Endpoint 3: Convert INR budget into local currency of that country
@app.get("/roam/{name}")
async def roam(
    name: str,
    budget_inr: float = Query(..., gt=0)
):

    country_details = await get_country_details(name)

    currency = country_details["currency"]

    # Validate the currency code before calling Frankfurter
    if not re.fullmatch(r"[A-Za-z]{3}", currency):
        raise HTTPException(
            status_code=503,
            detail="The country API returned an invalid currency code."
        )

    currency = currency.upper()

    # INR to local currency exchange rate
    rate_url = (
        f"{FRANKFURTER_API}/rate/INR/{currency}"
    )

    rate_data = await fetch_json(rate_url)

    rate = rate_data.get("rate")

    if not isinstance(rate, (int, float)) or rate <= 0:
        raise HTTPException(
            status_code=503,
            detail="Exchange rate is currently unavailable."
        )

    # Calculate the converted budget
    budget_local = round(budget_inr * rate, 2)

    return {
        "country": country_details["country"],
        "capital": country_details["capital"],
        "currency": currency,
        "rate": rate,
        "budget_inr": budget_inr,
        "budget_local": budget_local
    }
