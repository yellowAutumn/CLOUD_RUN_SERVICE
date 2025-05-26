# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port that the application will run on
EXPOSE 8080

# Set the command to run the application
CMD ["functions-framework", "--target", "test_internal_lb", "--port", "8080"]