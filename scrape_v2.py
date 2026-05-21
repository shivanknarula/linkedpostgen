import asyncio
import argparse
import random
import time
import os
from playwright.sync_api import sync_playwright
from datetime import datetime
import csv
import os
from groq import Groq

def get_target_profiles():
    # Specific high-profile accounts or companies to track
    return [
        'https://www.linkedin.com/company/boston-dynamics/',
        'https://www.linkedin.com/company/figure-ai/',
        'https://www.linkedin.com/company/agility-robotics/',
        'https://www.linkedin.com/company/apptronik/',
        'https://www.linkedin.com/company/unitree/',
        'https://www.linkedin.com/company/1x-technologies/',
        'https://www.linkedin.com/company/sanctuary-ai/',
        'https://www.linkedin.com/company/tesla-motors/',
        'https://www.linkedin.com/in/lexfridman/',
        'https://www.linkedin.com/in/andrewng/',
        'https://www.linkedin.com/in/elonmusk/',
        'https://www.linkedin.com/in/demishassabis/',
        'https://www.linkedin.com/in/yann-lecun/'
    ]

def get_queries():
    # Focused keywords for LinkedIn search as fallback
    return [
        'robotics "humanoid"',
        '"Boston Dynamics" OR "Figure AI"',
        'ROS2 "robot learning"',
        '"industrial automation" robotics',
        '"AI agents" OR "autonomous systems"'
    ]

HISTORY_FILE = "generated_links_history.txt"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def update_history(new_urls):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for url in new_urls:
            f.write(f"{url}\n")


import urllib.parse

    
def find_urls_via_linkedin(p, queries, history_set, limit=50, state_file="session.json"):
    """
    Uses Playwright to search LinkedIn directly using session.
    """

    print(f"[*] Discovery Phase: Finding {limit} candidates via LinkedIn Search...")
    urls = set()
    
    browser = p.chromium.launch(headless=True)
    if not os.path.exists(state_file):
        print(f"! Error: {state_file} not found. Please run --login first.")
        return []
        
    context = browser.new_context(storage_state=state_file)
    page = context.new_page()
    
    # Phase 1: High-Value Discovery (Target Specific Profiles First)
    target_profiles = get_target_profiles()
    print(f"[*] Discovery Phase: Checking {len(target_profiles)} Target Profiles...")
    
    for profile_url in target_profiles:
        if len(urls) >= limit:
            break
            
        posts_url = profile_url.rstrip('/') + '/recent-activity/all/'
        print(f" -> Checking profile: {posts_url}")
        try:
            page.goto(posts_url, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            # Simple scroll
            for s in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
                
            all_links = page.locator('a').all()
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    # FIX: corrected operator precedence + None guard
                    if href and ('/posts/' in href or 'activity-' in href):
                        if href.startswith('/'):
                            href = "https://www.linkedin.com" + href
                        clean_url = href.split('?')[0].split('&')[0]
                        # FIX: also filter against history_set so we skip already-scraped URLs
                        if 'linkedin.com' in clean_url and clean_url not in urls and clean_url not in history_set:
                            urls.add(clean_url)
                except:
                    continue
        except Exception as e:
            print(f"    ! Profile check failed for {profile_url}: {e}")

    # Fallback to general search if limit not reached
    if len(urls) < limit:
        print(f"[*] Discovery Phase: Falling back to keyword search (Need {limit - len(urls)} more)...")
        for q in queries:
            encoded_q = urllib.parse.quote(q)
            
            # CHANGE 2: Paginate search results
            for page_no in range(1, 4): # 3 pages per keyword max
                if len(urls) >= limit:
                    break
                    
                search_url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_q}&page={page_no}&origin=GLOBAL_SEARCH_HEADER"
                print(f" -> Searching LinkedIn: {q} (Page {page_no})")
                
                try:
                    page.goto(search_url, timeout=40000, wait_until="domcontentloaded")
                    page.wait_for_timeout(4000)
                    
                    if "login" in page.url:
                        print("    ! Redirected to login. Session might have expired.")
                        browser.close()
                        return list(urls)
                    
                    # CHANGE 1: Deep scroll (15-20 scrolls)
                    MAX_SCROLLS = 18
                    for s in range(MAX_SCROLLS):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        # random wait
                        page.wait_for_timeout(random.randint(1200, 2000))
                        
                    # Broad Link Extraction
                    all_links = page.locator('a').all()
                    
                    # CHANGE 3: Improve URL matching (patterns)
                    POST_PATTERNS = (
                        "/posts/",
                        "/feed/update/urn:li:activity:",
                        "activity-",
                        "/pulse/",
                    )
                    
                    for link in all_links:
                        try:
                            href = link.get_attribute('href')
                            if href:
                                if href.startswith('/'):
                                    href = "https://www.linkedin.com" + href
                                    
                                if any(p in href for p in POST_PATTERNS):
                                    clean_url = href.split('?')[0].split('&')[0]
                                    # FIX: filter against history_set so already-scraped posts are skipped
                                    if 'linkedin.com' in clean_url and clean_url not in urls and clean_url not in history_set:
                                        urls.add(clean_url)
                                        if len(urls) >= limit:
                                            break
                        except:
                            continue
                except Exception as e:
                    print(f"    ! Search attempt failed for {q} p{page_no}: {e}")
            
    browser.close()
    print(f"    Found {len(urls)} new candidates (filtered duplicates from history).")
    return list(urls)[:limit]


def login_and_save_state(p, username, password, state_file="session.json"):
    print(f"[*] Logging in as {username}...")
    browser = p.chromium.launch(headless=False) # Visual login usually safer for bot detection
    context = browser.new_context()
    page = context.new_page()
    
    try:
        page.goto("https://www.linkedin.com/login")
        
        # Fill creds
        page.fill('#username', username)
        page.fill('#password', password)
        page.click('button[type="submit"]')
        
        print("    Submitted credentials. Waiting for navigation...")
        try:
            # Wait for feed or something indicating success
            page.wait_for_url('**/feed/**', timeout=20000)
            print("    Login successful (reached feed).")
        except:
            print("    ! Warning: Did not reach feed URL. Check if captcha/mfa required.")
            print("    Saving state anyway in case it's just a slow load.")
            
        print(f"[*] Saving session state to {state_file}...")
        context.storage_state(path=state_file)
        
    except Exception as e:
        print(f"    ! Login failed: {e}")
    
    browser.close()

def extract_content(p, urls, state_file="session.json"):
    print("[*] Extraction Phase...")
    results = []
    
    # Load state if exists
    browser = p.chromium.launch(headless=True)
    
    if os.path.exists(state_file):
        print(f"    Loading session from {state_file}")
        context = browser.new_context(storage_state=state_file,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    else:
        print("    ! No session file found. Running anonymously (might hit auth wall).")
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    page = context.new_page()
    
    for i, url in enumerate(urls):
        print(f" [{i+1}/{len(urls)}] Scraping: {url}")
        try:
            page.goto(url, timeout=20000)
            
            # Dismiss login modal if it appears (common on LinkedIn public)
            try:
                page.locator('button[icon="x-icon"]').click(timeout=2000)
            except:
                pass
                
            # Expand text
            try:
                # multiple variants of 'see more'
                page.locator('.see-more').first.click(timeout=1000)
            except:
                pass
            
            # Extract Text
            # Try main article content first
            text = ""
            main_loc = page.locator('article')
            if main_loc.count() > 0:
                text = main_loc.first.inner_text()
            else:
                # Fallback to meta description or body
                text = page.locator('body').inner_text()[:4000]
            
            # Extract Engagement Metrics (Likes/Comments)
            likes = 0
            comments = 0
            try:
                # Basic scrape for likes
                social_text = page.locator('.social-details-social-counts').first.inner_text()
                # Basic parsing: "1,234 Likes \n 56 Comments"
                if 'Like' in social_text:
                    likes_str = social_text.split('Like')[0].strip().replace(',', '')
                    if likes_str.isdigit():
                        likes = int(likes_str)
                if 'Comment' in social_text:
                    # messy but tries to get the number before 'Comment'
                    comments_parts = social_text.split('Comment')[0].split('\n')
                    comment_str = comments_parts[-1].strip().replace(',', '')
                    if comment_str.isdigit():
                        comments = int(comment_str)
            except:
                pass

            
            # Cleanup
            text = text.replace('\n\n', '\n').strip()
            
            # Date
            date_str = datetime.now().strftime("%Y-%m-%d")
            
            results.append({
                'url': url,
                'date': date_str,
                'text': text,
                'likes': likes,
                'comments': comments
            })
            
            time.sleep(1) # Polite sleep
            
        except Exception as e:
            print(f"    ! Extraction failed: {e}")
            
    browser.close()
    return results

import json

def generate_ai_comment_and_score(post_text):
    """
    Generates a Commentability Score (1-10) and a high-value comment.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"score": 0, "comment": "AI Comment Unavailable (Set GROQ_API_KEY)", "reasoning": "Missing API Key"}
        
    try:
        client = Groq(api_key=api_key)
        prompt = (
            "You are an expert Robotics Engineer and Startup Founder looking to build high-quality network on LinkedIn. "
            "You are reviewing the following LinkedIn post. Your goal is to determine if the post is worth commenting on to build authority, and if so, draft the perfect comment.\n\n"
            "STEP 1: SCORE\n"
            "Rate the 'Commentability' of this post from 1 to 10.\n"
            "- 1-4 (Low): Generic PR, hiring posts, shallow memes. Hard to add value.\n"
            "- 5-7 (Medium): Standard industry news. You can add a decent thought.\n"
            "- 8-10 (High): Thought leadership, controversial takes, deep technical discussions, or posts by major figures where a smart comment will get high visibility.\n\n"
            "STEP 2: COMMENT\n"
            "If the score is 6 or higher, write a high-value comment. The comment MUST follow this framework:\n"
            "1. Acknowledge & Validate: Briefly validate the poster's original point.\n"
            "2. Add Unique Value: Provide a contrarian take, an unknown fact, or a deep technical insight.\n"
            "3. The Hook: End with an open-ended question to the author or audience to force a reply.\n\n"
            "Format the output STRICTLY as JSON:\n"
            "{\n"
            "  \"score\": <int>,\n"
            "  \"reasoning\": \"<short reason for score>\",\n"
            "  \"comment\": \"<your proposed comment, or empty if score < 6>\"\n"
            "}\n\n"
            "Post content:\n\n" + post_text[:3000]
        )
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            max_tokens=300,
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        data = json.loads(response_text)
        return {
            "score": data.get("score", 0),
            "reasoning": data.get("reasoning", ""),
            "comment": data.get("comment", "Pending analysis.")
        }
    except Exception as e:
        print(f"    ! AI Comment failed: {e}")
        return {"score": 0, "comment": "Error generating comment.", "reasoning": str(e)}

def save_to_file(posts, filename="robotics_posts.txt"):
    print(f"[*] Saving {len(posts)} posts to {filename} (Overwriting)...")
    # Sort historically by score
    sorted_posts = sorted(posts, key=lambda x: x.get('score', 0), reverse=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        for p in sorted_posts:
            f.write(f"LINK: {p['url']}\n")
            f.write(f"DATE: {p['date']}\n")
            f.write(f"METRICS: {p.get('likes', '0')} Likes, {p.get('comments', '0')} Comments\n")
            f.write(f"SCORE: {p.get('score', '0')}/10 - {p.get('reasoning', '')}\n")
            f.write(f"AI COMMENT:\n{p.get('comment', 'N/A')}\n")
            f.write("TEXT:\n")
            f.write(p['text'])
            f.write("\n" + "="*80 + "\n\n")

def save_to_csv(posts, filename="robotics_posts.csv"):
    keys = ['url', 'date', 'score', 'reasoning', 'comment', 'likes', 'comments', 'text']

    # FIX: Merge with existing CSV so posts accumulate across runs instead of being overwritten
    existing_rows = {}
    if os.path.exists(filename):
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_rows[row['url']] = row
        except Exception as e:
            print(f"    ! Could not read existing CSV (will overwrite): {e}")

    # Merge: new posts take priority over old ones with the same URL
    for p in posts:
        existing_rows[p['url']] = {k: p.get(k, '') for k in keys}

    merged = sorted(existing_rows.values(), key=lambda x: int(x.get('score') or 0), reverse=True)
    print(f"[*] Saving {len(merged)} total posts to {filename} ({len(posts)} new + {len(existing_rows) - len(posts)} existing)...")

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        for row in merged:
            dict_writer.writerow(row)

from dotenv import load_dotenv

def main():
    load_dotenv() # Load .env
    
    parser_arg = argparse.ArgumentParser()
    parser_arg.add_argument('--limit', type=int, default=50, help="Number of raw candidates to fetch (aim for ~2x desired output)")
    parser_arg.add_argument('--target_output', type=int, default=50, help="Stop analyzing after finding this many high-value posts")
    parser_arg.add_argument('--login', action='store_true', help="Run login flow")
    parser_arg.add_argument('--username', type=str, help="LinkedIn username (defaults to env)")
    parser_arg.add_argument('--password', type=str, help="LinkedIn password (defaults to env)")
    
    args = parser_arg.parse_args()
    
    with sync_playwright() as p:
        if args.login:
            username = args.username or os.getenv('LINKEDIN_USERNAME')
            password = args.password or os.getenv('LINKEDIN_PASSWORD')
            
            if not username or not password:
                print("! Error: Username/Password required (via args or .env) for login.")
                return
            login_and_save_state(p, username, password)
            return

        all_urls = set()
        queries = get_queries()
        
        all_urls = set()
        queries = get_queries()
        
        # Discovery Phase
        history = load_history()
        print(f"[*] Loaded {len(history)} links from history.")
        
        candidates = find_urls_via_linkedin(p, queries, history, limit=args.limit)
        
        if candidates:
            print(f"[*] Total unique new candidates: {len(candidates)}")
            posts = extract_content(p, candidates) 

            # Generate AI comments and scores
            print(f"[*] Intelligence Phase: Analyzing up to {len(posts)} posts to find {args.target_output} high-value targets...")
            analyzed_posts = []
            high_value_posts = []
            
            for post in posts:
                print(f"    Analyzing: {post['url']}")
                analysis = generate_ai_comment_and_score(post['text'])
                post['score'] = analysis['score']
                post['reasoning'] = analysis['reasoning']
                post['comment'] = analysis['comment']
                analyzed_posts.append(post)
                
                if post.get('score', 0) >= 6:
                    high_value_posts.append(post)
                    print(f"      -> Success! Found {len(high_value_posts)}/{args.target_output} high-value posts.")
                    
                if len(high_value_posts) >= args.target_output:
                    print(f"[*] Reached target output of {args.target_output} high-value comments. Stopping analysis.")
                    break
            
            print(f"[*] Filtering Complete: Found {len(high_value_posts)} high-value posts from {len(analyzed_posts)} analyzed candidates.")
            
            # Save all for records, but maybe prioritize the good ones
            save_to_file(high_value_posts, "high_value_comments.txt")
            save_to_file(analyzed_posts, "all_scraped_posts.txt")
            save_to_csv(analyzed_posts)
            
            # Update history with new candidates
            update_history(candidates)
            print(f"[*] Updated history with {len(candidates)} new links.")
        else:
            print("[!] No URLs found via LinkedIn Search.")

if __name__ == "__main__":
    main()
