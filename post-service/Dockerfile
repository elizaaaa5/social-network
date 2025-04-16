FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir protobuf==6.30.1

COPY app/proto /app/app/proto


COPY . .

# Run the application
CMD ["python", "-m", "app.main"]
