FROM python:3.12-slim

WORKDIR /app

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project code (app.py, controllers, models, utils, etc.)
COPY . .

EXPOSE 3000

# Start the Flask app
CMD ["python", "app.py"]