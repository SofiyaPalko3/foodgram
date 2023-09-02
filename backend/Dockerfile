FROM python:3.9
 
WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip
RUN pip install gunicorn==20.0.4
RUN pip install -r requirements.txt --no-cache-dir
 
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "foodgram_backend.wsgi:application"]