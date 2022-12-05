FROM python:3.7-slim

ARG SPLEETER_VERSION=1.5.3
ARG NUMPY_VERSION=1.19.5

RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install numpy==${NUMPY_VERSION} spleeter==${SPLEETER_VERSION}

CMD ["gunicorn", "-b", "0.0.0.0:80", "api:api"]