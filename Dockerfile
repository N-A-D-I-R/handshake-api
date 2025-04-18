FROM python:3.11.2

# Set the working directory
WORKDIR /app

# Update the package list and upgrade installed packages
RUN apt-get update && apt-get upgrade -y && apt-get install -y redis-server && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

EXPOSE 8000
EXPOSE 6379

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]