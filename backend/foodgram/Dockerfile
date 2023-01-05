FROM python:3.7-slim
COPY ./ /app
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt --no-cache-dir
WORKDIR /app/
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000