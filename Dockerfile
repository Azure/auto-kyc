# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Set work directory
WORKDIR /code

# Install system dependencies
RUN apt-get clean && apt-get update \
    && apt-get install -y --no-install-recommends gcc --allow-unauthenticated 

# Install CV2 dependencies
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

# Install python dependencies
COPY ./requirements.txt /code/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy project
COPY . .

# Expose the port FastAPI will run on
EXPOSE 80

# Run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]
