FROM python:3.8.1-buster

RUN mkdir /code
RUN mkdir -p /code/PLATER
COPY ./ /code/PLATER
WORKDIR /code/PLATER

RUN pip install -r /code/PLATER/requirements.txt

EXPOSE 8080

ENV PYTHONPATH=/code
ENTRYPOINT ["python", "main.py"]