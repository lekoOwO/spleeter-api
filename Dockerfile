FROM python:3.7-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:80", "api:api"]