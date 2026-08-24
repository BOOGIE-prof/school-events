FROM python:3.12-slim

WORKDIR /app
COPY . .

ENV PORT=8000 \
    DATABASE_PATH=/data/school.db \
    SECURE_COOKIES=1
VOLUME ["/data"]
EXPOSE 8000

CMD ["python", "app.py"]
