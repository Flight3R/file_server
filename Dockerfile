FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/repositories:/repositories/apptools/src

WORKDIR /server

COPY src/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "wsgi:app"]
