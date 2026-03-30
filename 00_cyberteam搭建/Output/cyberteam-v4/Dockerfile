# CyberTeam V4 - Core Engine Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir toml pyyaml

# Copy application files
COPY engine/ ./engine/
COPY config/ ./config/
COPY agents/ ./agents/
COPY skills/ ./skills/

# Set environment
ENV PYTHONPATH=/app
ENV ENV=development

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "engine.main"]