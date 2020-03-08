FROM python:3.7-alpine

RUN apk add --no-cache ffmpeg libsndfile

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:80", "api:api"]