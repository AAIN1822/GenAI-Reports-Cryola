# ================
#  Dockerfile
# ================
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
&& rm -rf /var/lib/apt/lists/*

# Prevent python from writing pyc files & enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy only necessary app files into image
COPY . .

EXPOSE 80

# Start server (no reload in prod)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
