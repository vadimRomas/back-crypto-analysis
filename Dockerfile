FROM python:3.8.10

ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt
RUN rm -rf ~/.local/lib/python3.8
RUN apt-get update && apt-get install -y make automake gcc g++ subversion libzbar-dev


RUN pip install --upgrade pip
#RUN pip install pyOpenSSL --upgrade
RUN pip install --default-timeout=100 -r /requirements.txt

RUN mkdir /app
COPY ./ /app
WORKDIR /app
