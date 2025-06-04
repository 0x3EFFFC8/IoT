FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sensors.proto 


EXPOSE 5000 8765 50051

CMD ["python", "gateway.py"]
