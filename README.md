# Mini API Project – Country Budget Planner

## Overview

This project is a simple REST API built using **FastAPI**. It provides country information and budget-based travel information using external APIs.

## Technologies Used

- Python
- FastAPI
- Uvicorn
- REST APIs
- Postman

## Project Structure

```text
mini-api-task-1/
│
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
│
└── postman/
    └── My API/
        └── YAML request files
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Vamsi-krishna17/mini-api-task-1.git
cd mini-api-task-1
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows:**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
python -m uvicorn main:app --reload
```

The API will run locally at:

`http://127.0.0.1:8000`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks API health |
| GET | `/countries/{name}` | Retrieves information about a country |
| GET | `/roam/{name}?budget_inr={amount}` | Retrieves budget-based travel information |

### Example Requests

**Health Check**

```http
GET /health
```

**Country Information**

```http
GET /countries/Japan
```

**Budget-Based Travel Information**

```http
GET /roam/Japan?budget_inr=150000
```

## API Documentation

After starting the application, access the interactive Swagger documentation:

`http://127.0.0.1:8000/docs`

You can also access the ReDoc documentation:

`http://127.0.0.1:8000/redoc`

## Error Handling

The API handles invalid requests and errors, including:

- **400 Bad Request:** Invalid request, where applicable.
- **404 Not Found:** Country not found.
- **422 Unprocessable Entity:** Invalid input or budget validation.
- **503 Service Unavailable:** External API service failure, where handled by the application.

## Postman Testing

The `postman/` directory contains the exported YAML request collection.

It includes requests for:
- API health check
- Country information
- Budget-based travel information
- Error scenarios such as 404 and 422

Use the Postman collection to execute and verify the API endpoints.

## Author

**Vamsi Krishna**

GitHub: https://github.com/Vamsi-krishna17