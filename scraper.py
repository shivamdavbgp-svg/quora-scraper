import os
import requests
from flask import Flask, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_quora_logic(url):
    print(f"Starting ScraperAPI for: {url}")
    api_key = "8a3c2070fc15e1569fc6f024d6fda72f"
        
    payload = {
        'api_key': api_key, 
        'url': url,
        'render': 'true'
    }
    
    response = requests.get('https://api.scraperapi.com/', params=payload)
    
    if response.status_code != 200:
        raise Exception(f"ScraperAPI failed with status code {response.status_code}: {response.text}")
        
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    
    title = soup.title.string if soup.title else "No Title"
    results = []
    
    for tag in soup.find_all(['p', 'span']):
        text = tag.get_text(separator=' ', strip=True)
        if len(text) > 80 and text not in results:
            results.append(text)
            
    return {"title": title, "results": results[:20]}

@app.route('/')
def home():
    return "Quora Scraper API (via ScraperAPI) is running! Go to /scrape to start scraping."

@app.route('/scrape')
def trigger_scrape():
    try:
        url = "https://www.quora.com/topic/Technology"
        extracted = scrape_quora_logic(url)
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
