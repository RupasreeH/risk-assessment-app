FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    && apt-get clean

WORKDIR /app

# Upgrade pip and install requirements
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
    BLIS_ARCH="generic" pip install --no-binary=blis -r requirements.txt

COPY . .

CMD ["python3", "run.py"]