FROM python:3.6-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt && pip install --upgrade --ignore-installed ./tensorflow-1.14.1-cp36-cp36m-linux_x86_64.whl && rm ./tensorflow-1.14.1-cp36-cp36m-linux_x86_64.whl

CMD ["gunicorn", "-b", "0.0.0.0:80", "api:api"]
