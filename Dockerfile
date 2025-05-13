FROM python:3.10-bullseye

# Install CA certificates
RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates

RUN mkdir /app

COPY *.py /app/
COPY requirements.txt /app/
COPY .env /app/

WORKDIR /app

RUN pip3 install -r requirements.txt

# Fix for Python SSL verification
ENV SSL_CERT_DIR=/etc/ssl/certs
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV PYTHONHTTPSVERIFY=1

EXPOSE 8765 8000

CMD ["python3", "bot.py"]