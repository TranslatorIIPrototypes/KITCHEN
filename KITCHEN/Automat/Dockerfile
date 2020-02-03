FROM python:3.8.1-buster

RUN mkdir /code
RUN mkdir -p /code/automat
COPY ./ /code/automat
WORKDIR /code/automat

RUN pip install -r /code/automat/requirements.txt

EXPOSE 8080

ENV PYTHONPATH=/code
ENTRYPOINT ["python", "main.py"]