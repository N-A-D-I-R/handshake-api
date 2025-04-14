# Use the official Python 3.12 image based on Debian Bookworm
FROM python:3.12-bookworm

# Set the working directory
WORKDIR /app

RUN sh ./setup-postgres.sh

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the default command to run the application
CMD ["python3", "-m", "uvicorn", "main:app", "--port", "0.0.0.0"]