import requests
import json
from datetime import datetime
import time
from urllib.parse import urljoin
from config import conf

BASE_URL = "https://www.mehrnews.com"
SEARCH_URL = "https://www.mehrnews.com/search?a=1&q=%D8%AC%D9%86%DA%AF&dr=custom&df=%DB%B1%DB%B4%DB%B0%DB%B4%2F%DB%B0%DB%B3%2F%DB%B2%DB%B2&dt=%DB%B1%DB%B4%DB%B0%DB%B4%2F%DB%B0%DB%B4%2F%DB%B5&sort=date&pageSize=50"

headers = {
    "X-API-Key": conf.AGENTQL_API_KEY,
    "Content-Type": "application/json"
}

def make_agentql_request(query, url, wait_time=2, mode="fast"):
    """Make a request to AgentQL API"""
    payload = {
        "query": query,
        "url": url,
        "params": {
            "wait_for": wait_time,
            "is_scroll_to_bottom_enabled": False,
            "mode": mode,
            "is_screenshot_enabled": False
        }
    }
    
    try:
        response = requests.post(conf.AGENTQL_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request to {url}: {e}")
        return None

def get_news_links():
    """Get all news article links from the search page"""
    links_query = """
    {
      news_links[] {
        link
        title_preview
      }
    }
    """
    
    print("Fetching news links from search page...")
    data = make_agentql_request(links_query, SEARCH_URL)
    
    if not data or 'data' not in data or 'news_links' not in data['data']:
        print("Could not extract news links")
        return []
    
    links = []
    for item in data['data']['news_links']:
        link = item.get('link', '')
        if link:
            # Convert relative URLs to absolute URLs
            if link.startswith('/'):
                link = urljoin(BASE_URL, link)
            elif not link.startswith('http'):
                link = f"{BASE_URL}/{link}"
            
            links.append({
                'url': link,
                'title_preview': item.get('title_preview', '')
            })
    
    print(f"Found {len(links)} news articles")
    return links

def get_article_details(article_url):
    """Get detailed information from a single news article"""
    detail_query = """
    {
      title
      summary
      publish_date
      names_of_individuals
      places
      organizations
      events
      data_sources
      image_link
      article_content
    }
    """
    
    print(f"Fetching details from: {article_url}")
    data = make_agentql_request(detail_query, article_url, wait_time=3)
    
    if not data or 'data' not in data:
        return None
    
    # Add the news_link to the extracted data
    article_data = data['data']
    article_data['news_link'] = article_url
    
    return article_data

def main():
    """Main function to orchestrate the scraping process"""
    print("Starting news scraping process...")
    
    # Step 1: Get all news article links
    news_links = get_news_links()
    
    if not news_links:
        print("No news links found. Exiting.")
        return
    
    # Step 2: Process each article
    all_news_data = []
    failed_urls = []
    
    for i, link_info in enumerate(news_links, 1):
        url = link_info['url']
        print(f"\nProcessing article {i}/{len(news_links)}")
        
        # Get detailed information
        article_details = get_article_details(url)
        
        if article_details:
            all_news_data.append(article_details)
            print(f"✓ Successfully processed: {article_details.get('title', 'No title')[:50]}...")
        else:
            failed_urls.append(url)
            print(f"✗ Failed to process: {url}")
        
        # Rate limiting - wait between requests
        if i < len(news_links):  # Don't wait after the last request
            print("Waiting 2 seconds before next request...")
            time.sleep(2)
    
    # Step 3: Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save successful results
    if all_news_data:
        filename = f"news_dataset_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "total_articles": len(all_news_data),
                    "extraction_date": datetime.now().isoformat(),
                    "source_url": SEARCH_URL
                },
                "articles": all_news_data
            }, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Successfully saved {len(all_news_data)} articles to {filename}")
    
    # Save failed URLs for retry
    if failed_urls:
        failed_filename = f"failed_urls_{timestamp}.json"
        with open(failed_filename, 'w', encoding='utf-8') as f:
            json.dump(failed_urls, f, indent=2)
        print(f"✗ {len(failed_urls)} URLs failed - saved to {failed_filename}")
    
    print(f"\nScraping completed!")
    print(f"Success: {len(all_news_data)} articles")
    print(f"Failed: {len(failed_urls)} articles")

def retry_failed_urls(failed_filename):
    """Retry processing failed URLs"""
    try:
        with open(failed_filename, 'r', encoding='utf-8') as f:
            failed_urls = json.load(f)
        
        print(f"Retrying {len(failed_urls)} failed URLs...")
        
        successful_retries = []
        still_failed = []
        
        for i, url in enumerate(failed_urls, 1):
            print(f"Retry {i}/{len(failed_urls)}: {url}")
            article_details = get_article_details(url)
            
            if article_details:
                successful_retries.append(article_details)
                print("✓ Success on retry")
            else:
                still_failed.append(url)
                print("✗ Still failed")
            
            time.sleep(3)  # Longer wait for retries
        
        # Save retry results
        if successful_retries:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            retry_filename = f"retry_success_{timestamp}.json"
            with open(retry_filename, 'w', encoding='utf-8') as f:
                json.dump(successful_retries, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved {len(successful_retries)} retry successes to {retry_filename}")
        
        if still_failed:
            still_failed_filename = f"still_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(still_failed_filename, 'w', encoding='utf-8') as f:
                json.dump(still_failed, f, indent=2)
            print(f"✗ {len(still_failed)} URLs still failed")
        
    except FileNotFoundError:
        print(f"File {failed_filename} not found")
    except json.JSONDecodeError:
        print(f"Invalid JSON in {failed_filename}")

if __name__ == "__main__":
    # Run main scraping
    main()
    