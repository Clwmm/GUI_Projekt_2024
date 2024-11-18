## Prepare project

1. Run ```python3 -m venv .venv```
2. Run ```source .venv/bin/activate```
3. Run ```pip install -r requirements.txt```
4. Create ```.env``` file in the project root folder with the following template:

```
GOOGLE_CLIENT_ID=<google client id api key console.cloud.google.com>
GOOGLE_CLIENT_SECRET=<google client secret api key console.cloud.google.com>
```

### Lightweight-Chart preparation

1. Run ```npm install lightweight-charts```
2. Run ```cp node_modules/lightweight-charts/dist/lightweight-charts.standalone.production.js frontend/static/scripts/```

### Tailwind

1. Run ```npx tailwindcss -i ./frontend/static/css/input.css -o ./frontend/static/css/output.css --watch```

### FastApi

1. Run ```uvicorn backend.main:app --reload```