FROM python:3.13-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY main.py ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

