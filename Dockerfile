# Light Ubuntu + Python distro.
FROM python:3.12-slim

# Avoid .pyc and buffer issues.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed for OpenCV / EasyOCR
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependencies for better cache usage
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Run the bot
CMD ["python", "bot_main.py"]
