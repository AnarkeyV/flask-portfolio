FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/instance && chmod 777 /app/instance

ENV FLASK_APP=flask_app.py
ENV FLASK_ENV=production
ENV DATABASE_URL=sqlite:////app/instance/comments.db

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
