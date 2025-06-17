# 🕸️ Technical Knowledge Scraper

A modular web scraper that extracts technical content from multiple sources (blogs, guides, PDFs) and makes it available via a FastAPI backend and React frontend.

## 🚀 Features

- Modular architecture for easy source integration
- PDF parsing with `PyPDF2`
- HTML scraping with `BeautifulSoup`
- Dynamic + static blog crawling
- Clean API design with FastAPI
- Frontend integration-ready

---

## 🛠️ Tech Stack

**Backend:**
- Python
- FastAPI
- BeautifulSoup
- PyPDF2
- Requests

**Frontend:**
- React
- TypeScript
- Tailwind CSS (or your current styling setup)

---

## 📦 Installation & Usage

Make sure you have **Python 3.10+** and **Node.js 18+** installed.

### 🔙 Backend Setup

```bash
# Install required Python libraries
pip install -r requirements.txt

# Navigate to backend directory
cd backend

# Start FastAPI server with hot reload
python -m uvicorn main:app --reload
```

###  Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

