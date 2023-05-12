# Use an official Python runtime as a parent images
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN apt update
RUN python3 -m pip install -r requirements.txt

# Expose port 8000 for the Flask application
EXPOSE 8000

# Run the command to start the Flask application
CMD ["python", "app.py"]