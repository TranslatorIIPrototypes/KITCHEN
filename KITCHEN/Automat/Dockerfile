FROM python:3.8.1-buster

ARG UID=1000
ARG GID=1000
RUN groupadd -o -g $GID automat
RUN useradd -m -u $UID -g $GID -s /bin/bash automat
WORKDIR /home/plater
RUN git clone https://github.com/TranslatorIIPrototypes/KITCHEN.git
WORKDIR /home/plater/KITCHEN/KITCHEN/Automat

RUN pip install -r requirements.txt

EXPOSE 8081
RUN mkdir -p /home/plater/KITCHEN/KITCHEN/Automat/logs
RUN chown automat:automat logs
USER automat

ENV PYTHONPATH=/home/plater/KITCHEN/KITCHEN/Automat
ENTRYPOINT ["python", "main.py"]