FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN chmod +x /wait-for-it.sh

COPY . .

CMD [ "sh", "-c", "/wait-for-it.sh postgres_db:5432 --timeout=60 --strict -- flask db upgrade && python run.py" ]