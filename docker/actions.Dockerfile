FROM rasa/rasa-sdk:2.8.8

USER root
RUN pip install mysql-connector-python
RUN apt update && apt install make

WORKDIR /bot
COPY ./bot /bot

ENTRYPOINT []
CMD "python -m rasa_sdk -p 5055"
