import os
import argparse
import time
import random
import requests
from googlesearch import search
from bs4 import BeautifulSoup
from dateutil import parser
import pandas as pd
from datetime import datetime, timedelta

def get_date_range(target_date_str):
    """
    Returns (after_date, before_date) strings for Google dorks.
    target_date_str: 'YYYY-MM-DD'
    """
    target = datetime.strptime(target_date_str, '%Y-%m-%d')
    # search for posts AFTER the day before target
    after = (target - timedelta(days=1)).strftime('%Y-%m-%d')
    # strictly speaking google's 'after' is inclusive or > depending on interpret. 
    # usually 'after:YYYY-MM-DD' means > YYYY-MM-DD.
    # To find posts FROM Jan 5, we usually want 'after:Jan 4'
    
    # We want posts specifically on this day. 
    # A safe bet is after:yesterday. 
    # Refinement: Google search doesn't strictly obey 'before' well for very recent index.
    # We will filter by date in post-processing if possible, or rely on 'after'.
    return after

def get_queries(after_date):
    """
    Returns a list of combined search queries with the date filter.
    """
    # Combining keywords into OR queries to minimize physical requests to Google
    query_groups = [
        'robotics OR "humanoid robot" OR "Boston Dynamics"',
        '"AI robotics" OR "Tesla Optimus" OR "Figure AI"',
        'ROS2 OR "robot learning" OR "reinforcement learning robotics"',
        '"industrial automation" OR "robotics engineer"'
    ]
    
    dorks = []
    for q in query_groups:
        dorks.append(f'site:linkedin.com/posts {q} after:{after_date}')
    
    return dorks

def extract_post(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract public text (post body/snippet)
        # LinkedIn public posts often hide content behind auth, but some snippet is usually in metadata or description
        text_elem = soup.find('div', class_='break-words') or soup.find('p') or soup.find('meta', attrs={'name': 'description'})
        
        text = "N/A"
        if text_elem:
            if text_elem.name == 'meta':
                text = text_elem.get('content', '')
            else:
                text = text_elem.get_text(strip=True)
        
        # Cleanup text length
        text = text[:2000] 
        
        # Author
        author = "Unknown"
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text().strip()
            # Title usually "Author Name on LinkedIn: Post content..."
            if " on LinkedIn:" in title_text:
                author = title_text.split(" on LinkedIn:")[0]
        
        return {
            'url': url,
            'text': text,
            'author': author,
            'scraped_date': datetime.now().strftime('%Y-%m-%d'),
            # Simple keyword count for 'score'
            'keywords': len([w for w in text.lower().split() if w in ['robot', 'robotics', 'ai', 'humanoid', 'ros', 'automation']])
        }
    except Exception as e:
        # print(f"Failed {url}: {e}")
        return None

def find_top_posts(target_date_str, limit=50):
    after_date = get_date_range(target_date_str)
    queries = get_queries(after_date)
    
    print(f"[*] Searching for posts from {target_date_str} (after:{after_date})...")
    
    found_urls = set()
    all_posts = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # We need to gather enough candidates to filter for quality/limit
    total_needed = limit * 2 
    
    backoff_time = 30 # Start with 30s backoff for 429
    
    for q in queries:
        if len(found_urls) >= total_needed:
            break
            
        print(f" -> Query: {q}")
        try:
            # pause to avoid immediate rate limit
            # Increased sleep_interval to 10 to be much safer
            for url in search(q, num_results=15, sleep_interval=10, advanced=False):
                if 'linkedin.com/posts' in url and url not in found_urls:
                    found_urls.add(url)
                    print(f"    Found: {url}")
                    if len(found_urls) >= total_needed:
                        break
                # Inner loop jitter
                time.sleep(random.uniform(2, 5))
                    
        except Exception as e:
            if "429" in str(e):
                print(f"    [!] Rate Limit (429) detected. Waiting {backoff_time}s...")
                time.sleep(backoff_time)
                backoff_time *= 2 # Exponential backoff
                if backoff_time > 300: # Max 5 mins wait
                    print("    [!] Over rate limit. Saving current progress...")
                    break
            else:
                print(f"    Error searching '{q}': {e}")
                time.sleep(10)
            
    print(f"[*] Extracted {len(found_urls)} unique URLs. Scraping content...")
    
    for url in list(found_urls):
        data = extract_post(url, headers)
        if data:
            all_posts.append(data)
        time.sleep(random.uniform(0.5, 1.5)) # Polite delay
        
    # Rank and filter
    # Boost score if 'text' contains relevant keywords
    # Since we can't easily verify the EXACT date from public HTML without complex parsing, 
    # we rely on Google's 'after:' filter and sort by relevance.
    
    sorted_posts = sorted(all_posts, key=lambda x: x['keywords'], reverse=True)
    return sorted_posts[:limit]

def main():
    parser_arg = argparse.ArgumentParser(description="Scrape LinkedIn Robotics posts via Google")
    parser_arg.add_argument('--date', type=str, default=None, help="YYYY-MM-DD (default: today)")
    parser_arg.add_argument('--limit', type=int, default=50, help="Number of posts to save")
    
    args = parser_arg.parse_args()
    
    target_date = args.date
    if not target_date:
        target_date = datetime.now().strftime('%Y-%m-%d')
        
    top_posts = find_top_posts(target_date, args.limit)
    
    filename = f'robotics_posts_{target_date}.csv'
    df = pd.DataFrame(top_posts)
    df.to_csv(filename, index=False)
    
    print(f"[*] Done! Saved {len(top_posts)} posts to {filename}")

if __name__ == "__main__":
    main()