FROM python:3.14-slim

# Prevent Python buffering issues
ENV PYTHONUNBUFFERED=1

# Markdown folder location

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy the rest of the app
COPY HeadstrongWebsite .

# Expose whatever port the app uses (guess 5000 or 8000)
EXPOSE 5000

# Default command (adjust depending on repo)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "Home:app"]
