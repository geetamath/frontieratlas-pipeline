# Deployment Guide — FrontierAtlas Intelligence Graph Service

This guide explains how to deploy the **FrontierAtlas Ingestion & Intelligence Graph** locally via Docker, or deploy it live to the cloud for free with a public HTTPS URL (Render, Railway, or Hugging Face Spaces).

---

## Option 1: Run Locally via Docker (Easiest & Fastest)

Since Docker is installed on your machine, you can run the entire service with one command:

### Using Docker Compose:
```bash
docker compose up -d --build
```

### Using Docker CLI:
```bash
docker build -t frontieratlas-service .
docker run -d -p 8000:8000 --name frontieratlas frontieratlas-service
```

### Access Local Dashboard & API:
- **Web Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Stats Endpoint**: [http://localhost:8000/api/stats](http://localhost:8000/api/stats)

---

## Option 2: 1-Click Free Cloud Deployment (Public HTTPS URL)

Deploying to a public cloud allows evaluators to interact directly with your live service!

### A. Deploy on Render (Free Tier — 2 Minutes)
1. Go to [render.com](https://render.com) and sign in with your GitHub account.
2. Click **New +** $\rightarrow$ **Web Service**.
3. Select your pushed `frontieratlas-pipeline` repository.
4. Settings:
   - **Name**: `frontieratlas-pipeline`
   - **Environment**: `Docker`
   - **Plan**: `Free`
5. Click **Create Web Service**.
6. Render builds the Docker container automatically and gives you a live public link:
   `https://frontieratlas-pipeline.onrender.com`

---

### B. Deploy on Hugging Face Spaces (100% Free Forever)
1. Go to [huggingface.co/new-space](https://huggingface.co/new-space).
2. Space Name: `frontieratlas-intelligence-graph`.
3. Space SDK: Select **Docker** (Blank template).
4. Clone and push your repository to the Hugging Face Space git remote:
   ```bash
   git remote add space https://huggingface.co/spaces/<YOUR_HF_USERNAME>/frontieratlas-intelligence-graph
   git push space main
   ```
5. Hugging Face will build the container and provide a live public URL.

---

### C. Deploy on Railway (Fast Serverless Deployment)
1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. Click **New Project** $\rightarrow$ **Deploy from GitHub repo**.
3. Select your `frontieratlas-pipeline` repo.
4. Railway automatically detects the `Dockerfile` and deploys it within 60 seconds.
5. In the service settings, click **Generate Domain** to get a public URL:
   `https://frontieratlas-pipeline.up.railway.app`

---

## Option 3: Run Locally Without Docker (Python Virtual Environment)

If you just want to run the web server on your local Python environment:
```bash
# Run the FastAPI server directly with uvicorn
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser at `http://localhost:8000`.

---

## Bonus: Adding Your Live Deployment to the Submission

Having a **live, hosted, working demo link** in your submission makes your project stand out:
1. In your **Loom video**, you can show the live cloud dashboard running in your browser!
2. In the Google Form (under the comments or Loom description), paste:
   `Live API & Dashboard Demo: https://your-app.onrender.com`
