import asyncio
import os
from flask import Flask, jsonify
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

app = Flask(__name__)

async def scrape_quora_logic(url):
    print(f"Starting scraper for: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        for i in range(3):
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(2000)
            
        html = await page.content()
        await browser.close()
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        content_divs = soup.find_all('div', class_=lambda x: x and ('q-box' in x or 'q-text' in x))
        for div in content_divs:
            text = div.get_text(separator=' ', strip=True)
            if len(text) > 50 and text not in results:
                results.append(text)
                
        return results

@app.route('/')
def home():
    return "Quora Scraper API is running! Go to /scrape to start scraping."

@app.route('/scrape')
def trigger_scrape():
    # We use asyncio.run to execute the async function inside the synchronous Flask route
    try:
        url = "https://www.quora.com/topic/Technology"
        data = asyncio.run(scrape_quora_logic(url))
        return jsonify({"status": "success", "url": url, "data_count": len(data), "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
