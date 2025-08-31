# Visual Product Matcher

A web application for image-based product similarity search using AI.

## Overview

This project uses OpenAI's CLIP model to find visually similar products by analyzing uploaded images or URLs. Users can upload a product image and get recommendations for similar items from a database.

## Approach

The system works by converting images into high-dimensional vector embeddings using CLIP, then performing similarity search in vector space:

1. **Image Processing**: CLIP model converts product images into 512-dimensional embeddings
2. **Vector Storage**: Qdrant database stores embeddings with cosine similarity indexing  
3. **Similarity Search**: User uploads trigger real-time vector similarity queries
4. **Results Ranking**: Most similar products returned based on embedding distance

## Technology Stack

- **Backend**: Flask (Python) with CLIP model integration
- **Vector Database**: Qdrant for similarity search
- **Frontend**: Next.js with modern UI components
- **AI Model**: OpenAI CLIP for image embeddings

## Quick Start

### Automated Setup
1. **Setup Environment**: `python setup.py`
2. **Start Services**: `python startup.py start`
3. **Access App**: Open `http://localhost:3000`

### Manual Setup
1. **Install Dependencies**: `pip install -r backend/requirements.txt` and `cd frontend && npm install`
2. **Start Qdrant**: `docker-compose up -d qdrant`
3. **Start Backend**: `cd backend && python app.py`
4. **Start Frontend**: `cd frontend && npm run dev`
5. **Access App**: Open `http://localhost:3000`

## Features

- Upload images or provide URLs for product matching
- Real-time similarity search with visual results
- Modern responsive web interface
- Docker-based deployment ready

## Deployment Options

### 🚀 **Production Deployment (Recommended)**

**Frontend**: Vercel (Edge-optimized, global CDN)
**Backend**: Google Cloud Run (Serverless, auto-scaling)
**Database**: Qdrant Cloud (Managed vector search)

```bash
# Quick deployment
cd backend
./deploy-cloudrun.ps1  # Windows
./deploy-cloudrun.sh   # Linux/macOS
```

📚 **See**: [`GOOGLE_CLOUD_RUN_GUIDE.md`](GOOGLE_CLOUD_RUN_GUIDE.md) for complete instructions

### 🔧 **Alternative Deployment Options**

- **Railway**: [`RAILWAY_DEPLOYMENT_GUIDE.md`](RAILWAY_DEPLOYMENT_GUIDE.md)
- **Heroku**: [`HEROKU_DEPLOYMENT_GUIDE.md`](HEROKU_DEPLOYMENT_GUIDE.md) (size limitations)
- **Local Docker**: `docker-compose up`

## Project Structure

- `frontend/` - Next.js web application with modern UI
- `backend/` - Flask API with CLIP model and vector search
- `docker-compose.yml` - Local container orchestration
- `GOOGLE_CLOUD_RUN_GUIDE.md` - Production deployment guide


