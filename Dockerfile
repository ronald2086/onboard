FROM python:3.10.4-slim-bullseye

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt


RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

EXPOSE 8050
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8050"]
