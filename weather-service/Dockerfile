# Use the official Python image as the base image
FROM python:3.9

# Install PostgreSQL
RUN apt-get update && apt-get install -y postgresql

# Install Poetry
RUN pip install poetry

# Set the working directory inside the container
WORKDIR /app

# Copy the project files to the working directory
COPY . .

# Install project dependencies
RUN poetry install

# start the postgres process first
CMD ["poetry", "run", "python3", "main.py", "--db"]

# run the python service
CMD ["poetry", "run", "python3", "main.py", "--dev"]