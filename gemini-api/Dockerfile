# docker build -t gemini-api .
# docker run -p 8000:8000 --env-file .env gemini-api
# docker run -p 8000:8000 -e GEMINI_API_KEY=my_gemini_api_key -e APP_API_KEY=my_api_key gemini-api

FROM python:3.12

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
