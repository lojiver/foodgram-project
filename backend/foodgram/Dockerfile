FROM python:3.7-slim
COPY ./ /app
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt
WORKDIR /app/
CMD python manage.py runserver 0:5000