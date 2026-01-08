FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY cleanse_library_data.py .

CMD ["python", "cleanse_library_data.py", "--help"]
