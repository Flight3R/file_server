FROM python:3.12

WORKDIR /server
COPY src /server

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "wsgi:app"]
