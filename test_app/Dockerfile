# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# load args
ARG ENV

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ENV $ENV
ENV DJANGO_SETTINGS_MODULE test_app.settings

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

EXPOSE 8080

# Install dependencies.
RUN pip install --no-cache-dir -r requirements.txt


# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 60 test_app.wsgi:application