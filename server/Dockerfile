# The runtime the server is developed and tested against
FROM python:3.13-slim

WORKDIR /app

# Install the runtime dependencies first, so the layer is cached across source changes
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# The modules in src/ import each other by bare name, so the server runs from that directory
WORKDIR /app/src

# 127.0.0.1 would only be reachable from inside the container, so the container binds every interface
ENV HOST=0.0.0.0
ENV PORT=8080

EXPOSE 8080

CMD ["python", "server.py"]
