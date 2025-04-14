FROM python:3.11.2

# Set the working directory
WORKDIR /app

# Update the package list and upgrade installed packages
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

COPY  .env .
COPY  setup-postgres.sh .
RUN sh ./setup-postgres.sh

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

EXPOSE 80

# Set the default command to run the application
CMD ["python3", "-m", "uvicorn", "main:app", "--port", "0.0.0.0"]