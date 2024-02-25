FROM python:3.11-slim-bookworm

WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /backend/
RUN pip install --no-cache -r requirements.txt
COPY . /backend

RUN chmod +x /backend/entrypoint.sh
RUN chmod -R 777 /backend/media
RUN chmod -R 777 /backend/static

CMD "/backend/entrypoint.sh"
EXPOSE 8000
