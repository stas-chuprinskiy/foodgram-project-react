FROM python:3.10-slim
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN mkdir /app
COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY ./ /app
WORKDIR /app

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
