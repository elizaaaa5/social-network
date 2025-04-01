FROM python:3.9-slim

WORKDIR /app

# Install build dependencies for grpcio and tools for protobuf
RUN apt-get update && apt-get install -y \
  build-essential \
  python3-dev \
  gcc \
  build-essential \ 
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the proto file and generate the gRPC code
COPY app/proto /app/app/proto
RUN python -m grpc_tools.protoc \
  -I/app \
  --python_out=/app \
  --grpc_python_out=/app \
  app/proto/post_service.proto

# Copy the rest of the application
COPY . .

# Run the application
CMD ["python", "-m", "app.main"]
