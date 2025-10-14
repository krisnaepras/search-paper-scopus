# 🔍 Scopus Search - Web Application

Complete web application untuk mencari dan menganalisis paper ilmiah dari database Scopus dengan tampilan web yang modern dan mudah digunakan.

## 📦 Package Contents

```
web-search-scopus/
├── api_scopus.py              # FastAPI backend server
├── requirements_api.txt       # Python dependencies
├── static/
│   └── index.html            # Web interface (HTML/CSS/JS)
├── README.md                 # This file
├── README_API.md             # API documentation
├── README_WEB.md             # Web interface guide
└── README_DOWNLOAD.md        # PDF download feature docs
```

## ⚡ Quick Start

### 1️⃣ Install Dependencies

```bash
cd web-search-scopus
pip install -r requirements_api.txt
```

atau

```bash
pip install fastapi uvicorn requests pandas pydantic openpyxl
```

### 2️⃣ Run Server

```bash
python api_scopus.py
```

Server akan berjalan di: **http://localhost:8000**

### 3️⃣ Open Web Interface

Buka browser dan akses:
```
http://localhost:8000
```

## ✨ Features

### 🔍 **Search & Filter**
- ✅ Keyword search dengan query Scopus
- ✅ Filter by year range (from - to)
- ✅ Limit control (10 - 500 results)
- ✅ Sort options: Citations, Date, Relevance

### 📊 **Real-time Statistics**
- Total papers found
- Total citations
- Average citations
- Maximum citations

### 📄 **Paper Information**
Setiap paper menampilkan:
- **Title** - Judul paper
- **Authors** - Penulis
- **Year** - Tahun publikasi
- **Citations** - Jumlah sitasi dengan badge 🔥/⭐
- **Document Type** - Article, Conference, Review, dll
- **Journal/Publication** - Nama jurnal
- **Affiliation** - Institusi penulis
- **Open Access** indicator 🔓
- **Links** - Scopus, DOI, PDF Download

### 📥 **Export Data**
Export hasil pencarian ke:
- **JSON** - Raw data
- **CSV** - Spreadsheet format
- **Excel** - .xlsx file

### 📑 **PDF Download**
- Multiple download options (DOI, Sci-Hub mirrors)
- Open Access detection
- Google Scholar alternative

## 🎯 Usage Examples

### Basic Search
1. Query: `machine learning`
2. Limit: `50`
3. Click **🚀 Cari Paper**

### Advanced Search
1. Query: `obesity classification deep learning`
2. Limit: `100`
3. Year from: `2020`
4. Year to: `2024`
5. Sort by: `Terbaru`
6. Click **🚀 Cari Paper**

### Download PDF
1. After search results appear
2. Click **📥 Download PDF** on any paper
3. Choose download method:
   - Official Publisher (may require subscription)
   - Sci-Hub mirrors (free access)
   - Google Scholar (search for free versions)

## 🚀 API Endpoints

The application provides RESTful API endpoints:

### Main Endpoints
- `GET /` - Web interface
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /health` - Health check
- `POST /api/search` - Search with filters
- `GET /api/quick-search` - Quick search (GET)
- `POST /api/stats` - Statistical analysis
- `POST /api/export/{format}` - Export to JSON/CSV/Excel

### PDF Download Endpoints
- `GET /api/pdf-link/{doi}` - Get PDF links by DOI
- `GET /api/download-info/{eid}` - Get download options by EID

### Author & Institution
- `GET /api/author/{name}` - Search by author
- `GET /api/affiliation/{institution}` - Search by institution
- `GET /api/highly-cited` - Filter highly cited papers

📖 **Full API documentation**: http://localhost:8000/docs

## 🎨 Web Interface

### Design Features
- 🎨 Modern gradient purple theme
- 📱 Fully responsive (desktop & mobile)
- ⚡ Smooth animations & transitions
- 🔄 Loading indicators
- ✅ Success/error notifications
- 🎯 Auto-scroll to results

### Browser Support
- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers

## 🔧 Configuration

### API Key
API key sudah embedded di `api_scopus.py`:
```python
API_KEY = "73439d14c6dc73b3a06756cbc9de5a4a"
```

### Change Port
Edit `api_scopus.py` line ~560:
```python
uvicorn.run(
    "api_scopus:app",
    host="0.0.0.0",
    port=8000,  # Change this
    reload=True
)
```

### Customize Colors
Edit `static/index.html` line ~20:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

## 📝 API Usage Examples

### Python
```python
import requests

# Search papers
response = requests.post(
    "http://localhost:8000/api/search",
    json={
        "query": "machine learning",
        "limit": 50,
        "year_from": 2020,
        "sort_by": "-citedby-count"
    }
)

data = response.json()
print(f"Found {data['returned_count']} papers")
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "deep learning",
    "limit": 25,
    "sort_by": "-citedby-count"
  }'
```

### JavaScript
```javascript
fetch('http://localhost:8000/api/search', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        query: 'neural networks',
        limit: 50,
        sort_by: '-citedby-count'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🐛 Troubleshooting

### Server won't start?
```bash
# Check if port 8000 is already in use
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill existing process or use different port
```

### Import errors?
```bash
# Reinstall dependencies
pip install -r requirements_api.txt --force-reinstall
```

### Can't access from other computers?
```bash
# Make sure firewall allows port 8000
# Server already listens on 0.0.0.0 (all interfaces)
```

### Search returns 422 error?
- Check that `sort_by` uses correct enum values:
  - `-citedby-count` (not `citations`)
  - `-date` (not `date_newest`)
  - `date` (not `date_oldest`)
  - `relevance` (OK)

### PDF download not working?
- DOI must be available for the paper
- Sci-Hub mirrors may be blocked in some countries
- Try alternative download methods (Google Scholar)
- Check if paper is Open Access

## 📚 Documentation

- **README_API.md** - Complete API reference dengan contoh request/response
- **README_WEB.md** - Web interface guide dan customization
- **README_DOWNLOAD.md** - PDF download feature documentation

## 🔒 Legal Notice

**Important**: This application uses Scopus API for searching papers. PDF download features use:
- Official DOI links (may require subscription)
- Sci-Hub mirrors (check local laws regarding usage)
- Google Scholar (for finding free versions)

Please respect copyright laws and publisher rights. Use at your own discretion.

## 🆘 Support

### Common Issues
1. **Error 422**: Check request payload format
2. **Error 500**: Scopus API may be down or rate limited
3. **No results**: Try different keywords or check query syntax
4. **Slow loading**: Large result sets take time to fetch

### Rate Limits
Scopus API has rate limits:
- Max 25 results per request
- Application automatically handles pagination
- Recommended: Don't fetch more than 500 results at once

## 🎯 Tips for Best Results

### Search Tips
- Use **specific keywords** for better results
- Try **quoted phrases** for exact matches: `"deep learning"`
- Use **Boolean operators**: `machine AND learning`
- Combine with **year filters** for recent papers

### Performance Tips
- Start with smaller limits (25-50) to test queries
- Use **sort by citations** to get most influential papers
- **Export results** for offline analysis
- Use **statistics endpoint** for quick overview

## 🚀 Deployment

### Local Development
```bash
python api_scopus.py
```

### Production (with Gunicorn)
```bash
pip install gunicorn
gunicorn api_scopus:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements_api.txt .
RUN pip install -r requirements_api.txt
COPY . .
EXPOSE 8000
CMD ["python", "api_scopus.py"]
```

## 📊 Tech Stack

- **Backend**: FastAPI 0.119.0+ (Python async web framework)
- **Server**: Uvicorn (ASGI server)
- **Validation**: Pydantic 2.0+ (data validation)
- **Data Processing**: Pandas 2.0+ (data analysis)
- **Export**: openpyxl (Excel files)
- **Frontend**: Pure HTML/CSS/JavaScript (no frameworks)
- **API**: Scopus Search API (Elsevier)

## 📄 License

Educational use only. Respect Scopus API terms of service and copyright laws.

## 👨‍💻 Author

Created with ❤️ using FastAPI & Vanilla JavaScript

---

**Version**: 1.0.0  
**Last Updated**: October 14, 2025

For questions or issues, check the documentation files in this folder or visit http://localhost:8000/docs for interactive API documentation.
