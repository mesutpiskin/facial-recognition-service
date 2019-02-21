FROM ubuntu:16.04

MAINTAINER mpiskin
RUN apt-get install -y python3 python3-dev python3-pip nginx
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt
COPY . /app
ENTRYPOINT ["python"]
CMD ["app.py"]