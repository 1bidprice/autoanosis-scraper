# Autoanosis Web Scraping Service

Professional web scraping API with headless browser support for reliable article extraction.

## Features

- ✅ **Headless Browser** (Playwright/Chromium)
- ✅ **Bypasses Rate Limiting** (HTTP 429)
- ✅ **Site-Specific Extractors** (medicalxpress, sciencedaily)
- ✅ **Generic Fallback** (works with any site)
- ✅ **RESTful API** (FastAPI)
- ✅ **Free Hosting** (Render.com)

## API Endpoints

### `POST /scrape`

Scrape full article content from a URL.

**Request:**
```json
{
  "url": "https://medicalxpress.com/news/...",
  "timeout": 30000
}
```

**Response:**
```json
{
  "success": true,
  "content": "Full article text...",
  "word_count": 1234,
  "error": null
}
```

## Deployment Options

### Option 1: Render.com (Recommended - Free)

1. **Create Render Account**: https://render.com
2. **New Web Service** → "Deploy from Git"
3. **Connect GitHub repo** or upload files
4. **Render will auto-detect** `render.yaml`
5. **Deploy** (takes 5-10 minutes)
6. **Get URL**: `https://autoanosis-scraper.onrender.com`

### Option 2: Railway.app (Alternative - Free)

1. **Create Railway Account**: https://railway.app
2. **New Project** → "Deploy from GitHub"
3. **Add Dockerfile**
4. **Deploy**
5. **Get URL**: `https://autoanosis-scraper.up.railway.app`

### Option 3: Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run server
python main.py

# Test
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://medicalxpress.com/news/..."}'
```

## WordPress Plugin Integration

After deployment, update WordPress plugin with your API URL:

```php
$scraper_api_url = 'https://your-scraper.onrender.com/scrape';
```

## Performance

- **Scraping Time**: 5-15 seconds per article
- **Success Rate**: 95%+ (bypasses rate limiting)
- **Free Tier Limits**: 
  - Render: 750 hours/month (always on)
  - Railway: 500 hours/month

## Troubleshooting

### Service Sleeps (Render Free Tier)
- Free tier sleeps after 15 min inactivity
- First request takes 30-60s to wake up
- Subsequent requests are fast

### Solution: Keep-Alive
Add to WordPress plugin:
```php
// Ping scraper every 10 minutes to keep it awake
wp_schedule_event(time(), 'every_10_minutes', 'ping_scraper');
```

## Security

- CORS enabled (restrict in production)
- No authentication (add API key if needed)
- Rate limiting recommended for production

## Support

For issues or questions, contact: support@autoanosis.com
