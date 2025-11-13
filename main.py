"""
Autoanosis Web Scraping Service
FastAPI + Playwright for reliable article scraping
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from playwright.async_api import async_playwright
import asyncio
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Autoanosis Scraper API",
    description="Web scraping service with headless browser support",
    version="1.0.0"
)

# CORS middleware - allow WordPress to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    url: HttpUrl
    timeout: Optional[int] = 30000  # 30 seconds default

class ScrapeResponse(BaseModel):
    success: bool
    content: str
    word_count: int
    error: Optional[str] = None

@app.get("/")
async def root():
    return {
        "service": "Autoanosis Scraper API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_article(request: ScrapeRequest):
    """
    Scrape full article content from a URL using headless browser
    """
    url = str(request.url)
    logger.info(f"Scraping request for: {url}")
    
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            # Create context with realistic settings
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US'
            )
            
            # Create page
            page = await context.new_page()
            
            # Navigate to URL
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until='networkidle', timeout=request.timeout)
            
            # Wait for content to load
            await page.wait_for_timeout(2000)
            
            # Extract article content using multiple strategies
            content = await extract_article_content(page, url)
            
            # Close browser
            await browser.close()
            
            if not content:
                raise HTTPException(status_code=404, detail="No content found")
            
            word_count = len(content.split())
            logger.info(f"Successfully scraped {word_count} words from {url}")
            
            return ScrapeResponse(
                success=True,
                content=content,
                word_count=word_count
            )
            
    except Exception as e:
        logger.error(f"Scraping error for {url}: {str(e)}")
        return ScrapeResponse(
            success=False,
            content="",
            word_count=0,
            error=str(e)
        )

async def extract_article_content(page, url: str) -> str:
    """
    Extract article content using site-specific and generic strategies
    """
    
    # Site-specific strategies
    if 'medicalxpress.com' in url:
        content = await extract_medicalxpress(page)
        if content:
            return content
    
    if 'sciencedaily.com' in url:
        content = await extract_sciencedaily(page)
        if content:
            return content
    
    # Generic fallback strategies
    strategies = [
        'article',
        '[role="main"]',
        '.article-content',
        '.entry-content',
        '.post-content',
        'main'
    ]
    
    for selector in strategies:
        try:
            element = await page.query_selector(selector)
            if element:
                # Get all paragraphs within this element
                paragraphs = await element.query_selector_all('p')
                texts = []
                for p in paragraphs:
                    text = await p.inner_text()
                    text = text.strip()
                    # Filter out short paragraphs (likely navigation/ads)
                    if len(text) > 50 and not any(word in text.lower() for word in ['cookie', 'subscribe', 'advertisement']):
                        texts.append(text)
                
                if texts:
                    content = '\n\n'.join(texts)
                    if len(content.split()) > 100:
                        return content
        except Exception as e:
            logger.warning(f"Strategy {selector} failed: {e}")
            continue
    
    return ""

async def extract_medicalxpress(page) -> str:
    """
    Extract content from medicalxpress.com
    """
    try:
        # Wait for article content
        await page.wait_for_selector('article', timeout=5000)
        
        # Get all paragraphs in article
        paragraphs = await page.query_selector_all('article p')
        texts = []
        
        for p in paragraphs:
            text = await p.inner_text()
            text = text.strip()
            if len(text) > 50:
                texts.append(text)
        
        if texts:
            return '\n\n'.join(texts)
    except Exception as e:
        logger.warning(f"medicalxpress extraction failed: {e}")
    
    return ""

async def extract_sciencedaily(page) -> str:
    """
    Extract content from sciencedaily.com
    """
    try:
        # Wait for main content
        await page.wait_for_selector('#story_text', timeout=5000)
        
        # Get story text
        element = await page.query_selector('#story_text')
        if element:
            paragraphs = await element.query_selector_all('p')
            texts = []
            
            for p in paragraphs:
                text = await p.inner_text()
                text = text.strip()
                if len(text) > 30:
                    texts.append(text)
            
            if texts:
                return '\n\n'.join(texts)
    except Exception as e:
        logger.warning(f"sciencedaily extraction failed: {e}")
    
    return ""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
