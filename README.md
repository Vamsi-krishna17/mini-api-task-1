# Country Mini Budget Planner API

A simple REST API built using **FastAPI** that retrieves country information and converts an INR budget into the local currency of a selected country.

The application integrates two external APIs: **CountriesNow** for retrieving country currency and capital information, and **Frankfurter** for exchange-rate data.

This project focuses on structuring the application using the Adapter and Facade design patterns, managing configuration through environment variables, handling external API errors, and running the application inside Docker.

## Tech Stack

- **Python 3.12** – Programming language
- **FastAPI** – REST API framework
- **HTTPX** – Asynchronous HTTP requests
- **python-dotenv** – Environment variable management
- **Uvicorn** – ASGI server
- **Docker** – Application containerization
- **Postman** – API testing

## Project Structure

```text
mini-api-project/
│
├── clients/
│   ├── countries_client.py
│   └── rates_client.py
│
├── services/
│   └── travel_service.py
│
├── postman/
│   └── [Exported Postman collection]
│
├── main.py
├── config.py
├── exceptions.py
├── requirements.txt
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
└── README.md
```

### File and Folder Responsibilities

| File / Folder         | Responsibility                                                                                                 |
| --------------------- | -------------------------------------------------------------------------------------------------------------- |
| `main.py`             | Defines FastAPI application and API routes. Handles HTTP responses and maps custom exceptions to status codes. |
| `config.py`           | Loads and validates application settings from environment variables.                                           |
| `exceptions.py`       | Defines custom exceptions for country-not-found and external API failures.                                     |
| `clients/`            | Contains individual client classes for communicating with external APIs.                                       |
| `countries_client.py` | Retrieves country currency and capital information from CountriesNow.                                          |
| `rates_client.py`     | Retrieves exchange rates from Frankfurter.                                                                     |
| `services/`           | Contains application-level business logic.                                                                     |
| `travel_service.py`   | Combines both clients and handles country information and budget conversion.                                   |
| `postman/`            | Contains the exported Postman collection used for API testing.                                                 |
| `requirements.txt`    | Lists project dependencies with pinned versions.                                                               |
| `.env.example`        | Provides an example of the required environment variables.                                                     |
| `.gitignore`          | Prevents unnecessary and sensitive files from being tracked by Git.                                            |
| `.dockerignore`       | Excludes unnecessary files from the Docker build context.                                                      |
| `Dockerfile`          | Defines how to build and run the application inside a Docker container.                                        |

## Design Patterns

This project uses two design patterns to separate responsibilities and keep the application organized.

### 1. Adapter Pattern

The Adapter pattern allows the application to communicate with external APIs through a consistent interface without exposing their implementation details to the rest of the application.

In this project, two client classes act as adapters:

**CountriesClient**

- Communicates with the CountriesNow API.
- Retrieves a country's currency and capital.
- Processes the external API response and returns the required Python values.

**RatesClient**

- Communicates with the Frankfurter API.
- Retrieves the exchange rate between two currencies.
- Returns the exchange rate in a format that the application can use.

Both clients handle HTTP communication and external API errors internally.

This keeps the service layer independent of external API request details.

### 2. Facade Pattern

The Facade pattern provides a simplified interface over multiple components.

In this project, `TravelService` acts as the Facade.

It coordinates the two client classes and exposes higher-level operations to the API routes.

For example, when a user requests a budget conversion:

1. The service retrieves the country's currency and capital through `CountriesClient`.
2. It obtains the exchange rate through `RatesClient`.
3. It calculates the equivalent local currency amount.
4. It returns the combined result to the API route.

Instead of calling multiple clients directly, `main.py` only needs to interact with `TravelService`.

### How They Work Together

```text
             API Request
                  |
                  v
              main.py
             API Routes
                  |
                  v
            TravelService
               Facade
              /      \
             v        v
    CountriesClient  RatesClient
       Adapter        Adapter
          |              |
          v              v
      CountriesNow   Frankfurter
          API            API
```

### Why This Structure?

- Each class has a specific responsibility.
- External API communication is separated from business logic.
- The service provides a single interface for the API routes.
- External clients can be replaced independently.
- Dependency injection makes the service easier to test and maintain.

The service receives its client instances through dependency injection instead of creating them internally.

## Configuration Management

Application settings are managed centrally in `config.py` using environment variables loaded through `python-dotenv`.

This avoids hardcoding API URLs and timeout values throughout the application.

Create a `.env` file in the project root using the following configuration:

```env
COUNTRIES_API=https://countriesnow.space/api/v0.1/countries
FRANKFURTER_API=https://api.frankfurter.dev/v2
REQUEST_TIMEOUT=10
```

### Configuration Variables

| Variable          | Description                                                 | Example / Default    |
| ----------------- | ----------------------------------------------------------- | -------------------- |
| `COUNTRIES_API`   | Base URL for the CountriesNow API.                          | CountriesNow API URL |
| `FRANKFURTER_API` | Base URL for the Frankfurter API.                           | Frankfurter API URL  |
| `REQUEST_TIMEOUT` | Maximum time allowed for external API requests, in seconds. | `10` seconds         |

The two API base URLs are required. If either is missing, the application raises a configuration error during startup. The request timeout has a default value.

**Important:** The `.env` file contains local configuration and should not be committed to GitHub. Use `.env.example` as the configuration template.

## Installation and Local Execution

### Prerequisites

- Python 3.12
- Git
- VS Code or another code editor
- Postman (optional, for API testing)

### 1. Clone the Repository

```bash
git clone https://github.com/Vamsi-krishna17/mini-api-task-1.git
```

Navigate into the project directory:

```bash
cd mini-api-task-1
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example configuration:

```powershell
Copy-Item .env.example .env
```

Make sure the values in `.env` are correct.

### 5. Start the Application

```bash
uvicorn main:app --reload
```

The application will be available at:

- API: [http://localhost:8000](http://localhost:8000)
- Swagger documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Running with Docker

The application can also run inside a Docker container without requiring a separate local Python environment for execution.

### 1. Build the Docker Image

Run this command from the project root:

```bash
docker build -t mini-api-project .
```

### 2. Run the Container

```bash
docker run --rm -p 8000:8000 --env-file .env mini-api-project
```

**Command explanation:**

- `--rm` removes the container after it stops.
- `-p 8000:8000` maps the host port to the container port.
- `--env-file .env` passes the application configuration to the container.
- `mini-api-project` is the Docker image name.

### 3. Access the Application

Open:

[http://localhost:8000/docs](http://localhost:8000/docs)

You can test the API endpoints through Swagger UI or use the exported Postman collection.

To stop the running container, press `Ctrl + C` in the terminal.

## API Endpoints

The application provides three endpoints.

### 1. Health Check

**Endpoint:** `GET /health`

Checks whether the application is running.

**Example request:**

```http
GET http://localhost:8000/health
```

**Response:**

```json
{
    "status": "healthy",
    "message": "Mini API Project is running successfully."
}
```

### 2. Get Country Information

**Endpoint:** `GET /countries/{name}`

Retrieves the currency and capital of the requested country.

**Example request:**

```http
GET http://localhost:8000/countries/Japan
```

**Example response:**

```json
{
    "country": "Japan",
    "currency": "JPY",
    "capital": "Tokyo"
}
```

### 3. Convert INR Budget into Local Currency

**Endpoint:** `GET /roam/{name}?budget_inr={amount}`

Retrieves the country's information, obtains the INR-to-local-currency exchange rate, and calculates the equivalent budget.

**Example request:**

```http
GET http://localhost:8000/roam/Japan?budget_inr=150000
```

**Example response:**

```json
{
    "country": "Japan",
    "capital": "Tokyo",
    "currency": "JPY",
    "rate": 1.75,
    "budget_inr": 150000.0,
    "budget_local": 262500.0
}
```

*Note: The exchange rate and converted budget above are illustrative. Actual values depend on the exchange rate returned by Frankfurter when the request is made.*

## Error Handling

The application uses custom exceptions to handle errors from external services and maps them to appropriate HTTP responses in `main.py`.

| Status Code                | Description                                                                       |
| -------------------------- | --------------------------------------------------------------------------------- |
| `200 OK`                   | Request completed successfully.                                                   |
| `404 Not Found`            | Requested country or required country information could not be found.             |
| `422 Unprocessable Entity` | Invalid request parameters, including a missing, invalid, or non-positive budget. |
| `503 Service Unavailable`  | An external API is unavailable, times out, or returns an unexpected failure.      |

### Custom Exceptions

- `CountryNotFoundError`: Raised when the requested country or required information cannot be found.
- `ExternalAPIError`: Raised when an external API fails, times out, or returns an invalid response.

The client classes raise these exceptions, while `main.py` converts them into HTTP 404 and 503 responses.

FastAPI handles request validation errors such as an invalid budget and returns 422.

## Testing

The application was tested using:

- Swagger UI for endpoint testing.
- Postman for testing the API collection.
- Docker for building and running the application in a container.
- Error scenarios for request validation and external API failures.

The Dockerized application was tested through Swagger and the Postman collection to verify that the endpoints continued to work after refactoring.

## Future Improvements

- Add automated unit and integration tests.
- Introduce database integration.
- Improve logging and monitoring.
- Extend the application with additional country and currency-related features.
