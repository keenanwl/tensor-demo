# Use the TensorFlow GPU image as the base
FROM tensorflow/tensorflow:latest-gpu

# Update package lists and install nano
RUN apt-get update && apt-get install -y nano

# Set the working directory inside the container
WORKDIR /app

# Copy the nn.py script and data directory into the container
COPY nn.py /app/nn.py
COPY data /app/data
