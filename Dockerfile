# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Install dev apt packages
RUN apt update && apt install -y git libasound-dev libportaudio2 \
    libportaudiocpp0 portaudio19-dev build-essential git \
    libsqlite3-dev libopus0 ffmpeg

# Set the working directory in the container to /app
WORKDIR /app

COPY requirements.txt /app

# Install any needed packages specified in requirements.txt etc
RUN pip3 install --upgrade pip
RUN pip3 install -r ./requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

RUN git submodule update --init --recursive
RUN python3 -m pip install -e ext/tinygrad

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
# CMD ["python", "main.py"]
