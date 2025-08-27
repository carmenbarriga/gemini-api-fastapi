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
├─ app.py               # FastAPI app
├─ requirements.txt     # Python dependencies
├─ requirements-dev.txt # Dev dependencies (linting, formatting)
├─ Dockerfile           # Container definition
├─ docker-compose.yml   # Compose setup
├─ Makefile             # Task runner
├─ pyproject.toml       # Configuration for black, isort, mypy
├─ .flake8              # Flake8 configuration
├─ .dockerignore        # Files/folders to ignore in Docker build
├─ .env                 # Environment variables (not committed)
└─ .gitignore
```

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/carmenbarriga/gemini-api-fastapi.git
cd gemini-api
```

### 2. Create a `.env` file

```env
# Google Gemini API key (get from AI Studio)
GEMINI_API_KEY=your_google_api_key

# Custom API key to secure this service
APP_API_KEY=my_secret_key
```

### 3. Install dependencies (development)

```bash
python -m venv .venv
source .venv/bin/activate
make install
```

## Run the API

### 1. Local development

```bash
make run
```

### 2. Using Docker Compose

```bash
make up
```

To run in detached mode:

```bash
make up-d
```

The API will be available at:
👉 http://localhost:8000

Interactive docs (Swagger UI):
👉 http://localhost:8000/docs

Stop and clean up:

```bash
make down
```

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

## Formatting & Linting

To keep the code consistent and clean, you can use the Makefile commands.

### Format the code

```bash
make format
```

This command runs black to automatically format Python code and isort to sort and organize imports according to the configured style.

### Run linters and type checks

```bash
make lint
```

This command runs flake8 to check for code style issues and potential bugs, and mypy to perform static type checking based on type hints.

## Endpoints

| Method | Endpoint  | Description                        | Auth Required |
| ------ | --------- | ---------------------------------- | ------------- |
| GET    | `/health` | Health check                       | ❌            |
| POST   | `/ask`    | Ask Gemini a question (JSON input) | ✅            |

## Development Notes

- **Default model:** `gemini-2.5-flash`
- **Exposed port:** `8000` (can be mapped to any host port in `docker-compose.yml`)
- **Error handling:** returns `502` if Gemini API fails upstream
