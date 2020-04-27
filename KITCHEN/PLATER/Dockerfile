FROM python:3.8.1-buster

ARG UID=1000
ARG GID=1000
RUN groupadd -o -g $GID plater
RUN useradd -m -u $UID -g $GID -s /bin/bash plater
WORKDIR /home/plater
RUN git clone https://github.com/TranslatorIIPrototypes/KITCHEN.git
WORKDIR /home/plater/KITCHEN/KITCHEN/PLATER
ENV PYTHONPATH=/home/plater/KITCHEN/KITCHEN/

RUN pip install -r requirements.txt
EXPOSE 8080
VOLUME logs
RUN chown plater:plater logs
USER plater
ENTRYPOINT ["python", "main.py"]