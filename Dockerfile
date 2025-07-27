FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .

RUN apt-get update && apt-get install -y curl \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .
COPY ./wait-for-it.sh /
RUN chmod +x /wait-for-it.sh

CMD [ "sh", "-c", "/wait-for-it.sh guardian-db:5432 --timeout=60 --strict -- flask db upgrade && python run.py" ]