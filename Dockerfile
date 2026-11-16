
# 1. Use an official Python image
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy requirements first
COPY requirements.txt .

# 4. Install Python dependencies inside Docker
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the project files into the container
COPY . .

# 6. Document the port used by FastAPI
EXPOSE 8000

# 7. Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
