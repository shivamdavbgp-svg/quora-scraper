import asyncio
import os
from flask import Flask, jsonify
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup

app = Flask(__name__)

async def scrape_quora_logic(url):
    print(f"Starting scraper for: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Apply stealth plugin to hide the fact that this is an automated browser
        await stealth_async(page)
        
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        for i in range(3):
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(2000)
            
        html = await page.content()
        title = await page.title()
        await browser.close()
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Fallback extraction: grab paragraphs or spans with meaningful text
        for tag in soup.find_all(['p', 'span']):
            text = tag.get_text(separator=' ', strip=True)
            if len(text) > 80 and text not in results:
                results.append(text)
                
        return {"title": title, "results": results[:20]} # limit to 20 results

@app.route('/')
def home():
    return "Quora Scraper API is running! Go to /scrape to start scraping."

@app.route('/scrape')
def trigger_scrape():
    try:
        url = "https://www.quora.com/topic/Technology"
        extracted = asyncio.run(scrape_quora_logic(url))
        return jsonify({
            "status": "success", 
            "url": url, 
            "page_title": extracted["title"],
            "data_count": len(extracted["results"]), 
            "data": extracted["results"]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
