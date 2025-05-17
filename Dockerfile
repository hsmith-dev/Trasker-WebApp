# Dockerfile

# 1. Use an official Python runtime as a parent image
# Choose a Python version that matches your needs
FROM python:3.12-slim

# 2. Set environment variables
# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
 # Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory in the container
WORKDIR /app

# 4. Install system dependencies (if any)
# For psycopg2, sometimes build essentials are needed if using a non-binary version or a very minimal base image.
# With psycopg2-binary, this is often not needed, but if you encounter issues:
# RUN apt-get update && apt-get install -y build-essential libpq-dev

# 5. Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy your project code into the container
COPY . /app/

# 7. Expose the port the app runs on (Django default is 8000)
EXPOSE 8000

# 8. Define the command to run your application
# For development, this will be the Django development server.
# For production, you'd typically use Gunicorn or uWSGI.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]