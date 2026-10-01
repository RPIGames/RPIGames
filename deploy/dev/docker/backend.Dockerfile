# Build context should be from project root folder

FROM python:latest
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=src/backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=src/backend/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --link-mode=copy

# Copy the code into the image, excluding dotfolders
COPY --exclude=**/.*/** \
    src/backend /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --link-mode=copy

# Set database
VOLUME ["/db"]
ENV DATABASE_PATH="/db/database.db"

# The command to actually run
CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0", "--port", "9000", "--forwarded-allow-ips=\"*\"", "--root-path", "/api"]
