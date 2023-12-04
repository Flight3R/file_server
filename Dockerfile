FROM python:3.8-slim

WORKDIR /http_server
COPY src /http_server

RUN mkdir -p content
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "wsgi:app"]
