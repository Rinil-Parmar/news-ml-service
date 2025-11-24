# News ML Service

FastAPI microservice for article summarization and personalized recommendations.

---

## 🚀 Features

- **Summarization**: BART model for article condensation
- **Recommendations**: TF-IDF + User behavior personalization
- **Real-time**: Fresh rankings with MongoDB integration

---

## 📋 Prerequisites

- Python 3.8+
- MongoDB Atlas account
- 2GB+ RAM

---

## ⚙️ Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd news-ml-service
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create `.env` file in root:
```env
MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/<database>?retryWrites=true&w=majority
DB_NAME=ai-news
```

### 5. Run Service
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Service runs at: **http://localhost:8000**

---

## 📡 API Endpoints

### Health Check
```
GET http://localhost:8000/health
```

### Summarize Article
```
POST http://localhost:8000/summarize
Content-Type: application/json

{
  "content": "Your full article text here..."
}
```

**Response:**
```json
{
  "summary": "Condensed summary text...",
  "original_length": 150,
  "summary_length": 45
}
```

### Get Recommendations
```
POST http://localhost:8000/recommend
Content-Type: application/json

{
  "preferences": ["technology", "AI", "machine learning"],
  "userId": "optional-user-id",
  "limit": 20
}
```

**Response:**
```json
{
  "articles": [
    {
      "id": "article-id",
      "title": "Article Title",
      "description": "Article description...",
      "url": "https://...",
      "score": 0.89
    }
  ],
  "total": 20
}
```

## 🗂️ Project Structure
```
news-ml-service/
├── app/
│   ├── main.py              # API endpoints
│   ├── config.py            # Configuration
│   ├── database.py          # MongoDB connection
│   ├── models.py            # Request/Response models
│   └── services/
│       ├── summarization.py # BART model
│       └── recommendation.py # TF-IDF ranking
├── requirements.txt
├── .env
└── README.md
```

---

## 🔍 How It Works

### Summarization
- Uses BART (facebook/bart-large-cnn)
- Condenses long articles into concise summaries

### Recommendations
- Calculates TF-IDF similarity with user preferences
- Personalizes based on user events:
  - **Hidden articles**: Filtered out
  - **Liked articles**: Score × 1.5
  - **Read articles**: Score × 1.2
- Returns top N ranked articles

---

## 📊 MongoDB Collections

| Collection | Usage |
|------------|-------|
| `news` | Article data |
| `user_events` | User interactions (read/like/hide) |
| `user` | user data |

---
---

## 📦 Key Dependencies
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
motor==3.3.2
pymongo==4.6.1
transformers==4.36.2
torch==2.1.2
scikit-learn==1.4.0
numpy==1.26.3
pydantic==2.5.3
python-dotenv==1.0.0
pydantic-settings==2.1.0
```

---

## 🚀 Quick Start
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Create .env with MongoDB URI
uvicorn app.main:app --reload --port 8000
```

**Service ready at http://localhost:8000** ✅

## 👥 Contributors

- **Rinil Parmar** 
- **Aditi Parmar**

