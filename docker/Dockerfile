FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY ../src/scraper.py .
COPY ../src/email_monitor.py .
COPY ../src/display_manager.py .
COPY ../src/server.py .
COPY ../src/updater.py .
COPY ../config/config.json.template .

# Create data directory for quotes
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Run the server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "server:app"]
