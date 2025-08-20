# Gemini API Wrapper with FastAPI

A minimal **FastAPI** wrapper around Google’s **Gemini API**, containerized with Docker.  
This project exposes a single `/ask` endpoint that forwards user questions to Gemini and returns the model response.  
It also includes **API key authentication** so only authorized clients can use your endpoint.

---

## Features

- 🔑 API key authentication (`Authorization: Bearer ...`)
- ⚡ Powered by [FastAPI](https://fastapi.tiangolo.com/)
- 🤖 Integrated with [Google Gemini](https://aistudio.google.com/)
- 🐳 Runs fully containerized via **Docker Compose**

---

## Project Structure

```bash
gemini-api/
├─ app.py              # FastAPI app
├─ requirements.txt    # Python dependencies
├─ Dockerfile          # Container definition
├─ docker-compose.yml  # Compose setup
├─ .env                # Environment variables (not committed)
└─ .gitignore
```

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/gemini-api.git
cd gemini-api
```

### 2. Create a `.env` file

```env
# Google Gemini API key (get from AI Studio)
GEMINI_API_KEY=your_google_api_key

# Custom API key to secure this service
APP_API_KEY=my_secret_key
```

## Run with Docker Compose

Build and start the container:

```bash
docker compose up --build
```

The API will be available at:
👉 http://localhost:8000

Interactive docs (Swagger UI):
👉 http://localhost:8000/docs

## Usage

### Example request

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer my_secret_key" \
  -d '{"question": "Explain FastAPI in one sentence."}'
```

### Example response

```json
{
  "answer": "FastAPI is a modern Python web framework for building APIs quickly and efficiently."
}
```

## Endpoints

| Method | Endpoint  | Description                        | Auth Required |
| ------ | --------- | ---------------------------------- | ------------- |
| GET    | `/health` | Health check                       | ❌            |
| POST   | `/ask`    | Ask Gemini a question (JSON input) | ✅            |

## Development Notes

- **Default model:** `gemini-1.5-flash`
- **Exposed port:** `8000` (can be mapped to any host port in `docker-compose.yml`)
- **Error handling:** returns `502` if Gemini API fails upstream

## Stop & Clean Up

```bash
docker compose down
```
