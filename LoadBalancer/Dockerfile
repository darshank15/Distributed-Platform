FROM ubuntu

MAINTAINER Bhavin Kotak <bhavinkotak07@gmail.com>
RUN apt-get update

RUN apt-get install python -y
RUN apt-get install python-pip -y


WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/


