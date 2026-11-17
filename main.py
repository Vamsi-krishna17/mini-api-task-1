
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Depends, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from clients.countries_client import CountriesClient
from clients.rates_client import RatesClient

from db import create_tables, get_db
from exceptions import (
    CountryNotFoundError,
    ExternalAPIError,
    TripNotFoundError,
)
from logging_setup import configure_logging, request_logging_middleware
from repositories.trip_repository import TripRepository
from schemas import TripCreate, TripUpdate, TripOut
from services.travel_service import TravelService
from services.trip_service import TripService


# --------------------------------------------------
# Application startup and database initialization
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


configure_logging()

app = FastAPI(
    title="Country Mini Budget Planner API",
    description=(
        "An API to retrieve country details, convert INR budgets "
        "into local currencies, and manage travel plans."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# Request logging middleware
app.middleware("http")(request_logging_middleware)


# --------------------------------------------------
# Initialize shared external API clients
# --------------------------------------------------

countries_client = CountriesClient()
rates_client = RatesClient()

travel_service = TravelService(
    countries_client=countries_client,
    rates_client=rates_client,
)


# --------------------------------------------------
# Trip service dependency
# Each request receives its own database session
# --------------------------------------------------

def get_trip_service(db: Session = Depends(get_db)) -> TripService:
    repository = TripRepository(db)

    return TripService(
        repository=repository,
        countries_client=countries_client,
        rates_client=rates_client,
    )


# --------------------------------------------------
# Custom exception handlers
# --------------------------------------------------

@app.exception_handler(TripNotFoundError)
async def trip_not_found_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(CountryNotFoundError)
async def country_not_found_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(ExternalAPIError)
async def external_api_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc)},
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


# trip endpoints 

# 1. CREATE A TRIP
@app.post(
    "/trips",
    response_model=TripOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Trips"],
)
async def create_trip(
    payload: TripCreate,
    service: TripService = Depends(get_trip_service),
):
    return await service.create_trip(payload.model_dump())


# 2. GET ALL TRIPS
@app.get(
    "/trips",
    response_model=list[TripOut],
    tags=["Trips"],
)
async def get_all_trips(
    service: TripService = Depends(get_trip_service),
):
    return await service.list_trips()


# 3. GET A SINGLE TRIP BY ID
@app.get(
    "/trips/{trip_id}",
    response_model=TripOut,
    tags=["Trips"],
)
async def get_trip(
    trip_id: int,
    service: TripService = Depends(get_trip_service),
):
    return await service.get_trip(trip_id)


# 4. UPDATE AN EXISTING TRIP
@app.patch(
    "/trips/{trip_id}",
    response_model=TripOut,
    tags=["Trips"],
)
async def update_trip(
    trip_id: int,
    payload: TripUpdate,
    service: TripService = Depends(get_trip_service),
):
    update_data = payload.model_dump(exclude_unset=True)

    return await service.update_trip(
        trip_id=trip_id,
        data=update_data,
    )


# 5. DELETE A TRIP
@app.delete(
    "/trips/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Trips"],
)
async def delete_trip(
    trip_id: int,
    service: TripService = Depends(get_trip_service),
):
    await service.delete_trip(trip_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
