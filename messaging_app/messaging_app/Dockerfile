FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update \
    && apt-get install -y default-libmysqlclient-dev gcc \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get clean

COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# sudo docker run -p 8000:8000 messaging-app

RUN apt-get update \
    && apt-get install -y default-libmysqlclient-dev gcc \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get clean

