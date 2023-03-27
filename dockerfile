FROM python:3

WORKDIR /app


COPY . .

CMD [ "python", "./your_script.py" ]
