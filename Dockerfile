FROM python:3.12-slim

# Set up working directory
WORKDIR /app

# Copy requirements.txt and set up dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files of project to working directory
COPY . /app/

# Open port for the application
EXPOSE 8000

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]