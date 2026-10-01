# Build context: project root

FROM docker.io/node:22-alpine AS ts-compile

WORKDIR /app

# Install typescript
RUN npm install typescript

# Copy TypeScript source/config
COPY src/frontend/ ./

# Compile TypeScript
RUN npx tsc -p tsconfig.json --outDir /app/dist

FROM docker.io/nginx:stable-alpine-slim

COPY deploy/dev/docker/nginx_config.conf /etc/nginx/nginx.conf

# Only compiled frontend files make it into the final image
COPY --from=ts-compile /app/dist /app/dist/
COPY src/frontend/static /app/static/
COPY src/frontend/templates /app/templates/
COPY src/frontend/index.html /app/index.html

EXPOSE 80

# CMD is the default from the docker.io/nginx repo
