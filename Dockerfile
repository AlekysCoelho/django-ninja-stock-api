FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /src

# Install Poetry
RUN pip install poetry

# Copy Poetry files first to optimize cache
COPY pyproject.toml /src/
COPY poetry.lock /src/

# Install dependencies without creating virtual environment
RUN poetry config virtualenvs.create false && poetry install --no-root --with dev && poetry sync

# Copy the rest of the code to maintain the correct structure
COPY app /src/app/
COPY tests /src/tests/
COPY manage.py /src/
COPY entrypoint.sh /src/

# Give execution permission to entrypoint
RUN chmod +x /src/entrypoint.sh

# Adjust permissions for the non-root user
RUN chown -R appuser:appuser /src

# Switch to the non-root user
USER appuser

# Expose Django port
EXPOSE 8000

CMD ["./entrypoint.sh"]