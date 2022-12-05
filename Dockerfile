FROM python:3.7-slim

ARG SPLEETER_VERSION=1.5.3

RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install spleeter==${SPLEETER_VERSION}

CMD ["gunicorn", "-b", "0.0.0.0:80", "api:api"]