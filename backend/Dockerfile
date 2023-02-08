FROM python:3.10-slim
RUN /usr/local/bin/python -m pip install --upgrade pip

RUN apt-get update
RUN apt-get install -y wget
RUN apt-get install -y xz-utils
RUN apt-get install -y libfontconfig1 libxrender1 libxext6
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN tar xvJf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN cp wkhtmltox/bin/wkhtmlto* /usr/bin/

RUN mkdir /app
COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY ./ /app
WORKDIR /app

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
