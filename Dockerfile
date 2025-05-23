
FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

FROM backend AS production


#COPY --from=frontend-builder /app/app/static/build ./app/static/

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.main:app"]