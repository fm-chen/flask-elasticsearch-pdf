FROM python:3.8

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

ENV SCRIPT_NAME=/cpi

COPY . .

EXPOSE 5001

CMD ["gunicorn", "--conf", "gunicorn_conf.py", "--bind", "0.0.0.0:5001", "app:app"]