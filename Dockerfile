FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
ADD requirements-dev.txt /code/
RUN pip install -r requirements.txt && pip install -r requirements-dev.txt
