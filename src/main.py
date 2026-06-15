import asyncio
import argparse
import os
import time
from datetime import datetime
from playwright.async_api import async_playwright
from src.config import HEADLESS, DB_PATH
from src.database import (
    init_db, get_db_connection, start_crawl_run, finish_crawl_run,
    get_history_set, add_urls_to_history, add_discovered_post,
    save_extracted_post, get_unscored_posts, save_post_scoring,
    export_to_legacy_files
)
from src.scraper import AsyncLinkedInScraper
from src.discovery import DiscoveryEngine
from src.scoring import AIScoringPipeline

async def run_login_flow(username, password, state_file="session.json"):
    """Runs a visible browser login session to generate state_file (session.json)."""
    print(f"[*] Starting login flow as {username}...")
    async with async_playwright() as p:
        # headful is needed for MFA / captcha checks
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
            await page.fill('#username', username)
            await page.fill('#password', password)
            await page.click('button[type="submit"]')
            
            print("    Waiting for feed page to verify login...")
            await page.wait_for_url('**/feed/**', timeout=30000)
            print("    Login succeeded! Saving session state...")
            await context.storage_state(path=state_file)
        except Exception as e:
            print(f"[!] Login failed: {e}")
        finally:
            await browser.close()

async def run_pipeline(args):
    start_time = time.time()
    
    # Ensure DB is initialized
    init_db()
    
    run_id = start_crawl_run()
    print(f"[*] Started Crawl Run ID: {run_id}")
    
    posts_discovered = 0
    posts_extracted = 0
    posts_scored = 0
    error_message = None
    
    try:
        scraper = AsyncLinkedInScraper(state_file="session.json")
        discovery = DiscoveryEngine(scraper)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=HEADLESS)
            
            # Setup session state context
            state_file = "session.json"
            if os.path.exists(state_file):
                context = await browser.new_context(
                    storage_state=state_file,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            else:
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
            # Step 1: Session check
            page = await context.new_page()
            is_active_session = await scraper.verify_session(page)
            await page.close()
            
            # Step 2: Discovery Engine
            conn = get_db_connection()
            discovered = await discovery.run_discovery(context, conn, is_active_session=is_active_session, target_limit=args.limit)
            posts_discovered = len(discovered)
            print(f"[*] Discovered {posts_discovered} candidate URLs.")
            
            # Add discovered posts to DB
            for item in discovered:
                add_discovered_post(item['url'], item['category'], item['profile_url'])
            
            # Step 3: Extraction Phase (for newly discovered posts)
            history_set = get_history_set()
            urls_to_extract = [item['url'] for item in discovered if item['url'] not in history_set]
            
            if urls_to_extract:
                print(f"[*] Extracting content for {len(urls_to_extract)} new posts...")
                extraction_tasks = [scraper.extract_single_post_content(context, url) for url in urls_to_extract]
                extraction_results = await asyncio.gather(*extraction_tasks)
                
                # Save extracted text/metrics
                for res in extraction_results:
                    if res and res['text']:
                        save_extracted_post(res['url'], res['text'], res['likes'], res['comments'], res['date'])
                        posts_extracted += 1
                        
                # Add to processed history
                add_urls_to_history(urls_to_extract)
            else:
                print("[*] No new posts to extract content for in this run.")
                
            await browser.close()
            
        # Step 4: AI Scoring Pipeline (Groq)
        conn = get_db_connection()
        unscored_posts = get_unscored_posts()
        conn.close()
        
        if unscored_posts:
            print(f"[*] Running AI Scoring Pipeline on {len(unscored_posts)} unscored posts...")
            scorer = AIScoringPipeline()
            scored_results = await scorer.evaluate_posts(unscored_posts)
            
            for post in scored_results:
                url = post['url']
                score_data = post['score_data']
                
                save_post_scoring(
                    url=url,
                    status='scored',
                    total_score=score_data.get('total_score', 0),
                    scores_dict=score_data,
                    reasoning=score_data.get('reasoning', ''),
                    comment_text=score_data.get('comment', '')
                )
                posts_scored += 1
                
            print(f"[*] Scored {posts_scored} posts successfully.")
        else:
            print("[*] No unscored posts to evaluate.")
            
    except Exception as e:
        error_message = str(e)
        print(f"[!] Pipeline Execution Failed: {error_message}")
        
    finally:
        end_time = time.time()
        duration_ms = int((end_time - start_time) * 1000)
        status = "failed" if error_message else "success"
        
        finish_crawl_run(
            run_id=run_id,
            status=status,
            posts_discovered=posts_discovered,
            posts_extracted=posts_extracted,
            posts_scored=posts_scored,
            error_message=error_message,
            duration_ms=duration_ms
        )
        print(f"[*] Crawl Run ID {run_id} finished in {duration_ms / 1000:.2f} seconds. Status: {status}")
        
        # Export files for backward/cloud compatibility
        export_to_legacy_files()

def main():
    parser = argparse.ArgumentParser(description="LinkedIn AI & Robotics Intelligence Platform orchestrator")
    parser.add_argument('--limit', type=int, default=50, help="Number of raw candidates to fetch")
    parser.add_argument('--target_output', type=int, default=12, help="Stop analyzing after finding this many high-value posts")
    parser.add_argument('--login', action='store_true', help="Run login flow")
    parser.add_argument('--username', type=str, help="LinkedIn username (defaults to env)")
    parser.add_argument('--password', type=str, help="LinkedIn password (defaults to env)")
    
    args = parser.parse_args()
    
    from dotenv import load_dotenv
    load_dotenv()
    
    if args.login:
        username = args.username or os.getenv('LINKEDIN_USERNAME')
        password = args.password or os.getenv('LINKEDIN_PASSWORD')
        if not username or not password:
            print("[!] Error: Username/Password required (via args or .env) for login.")
            return
        asyncio.run(run_login_flow(username, password))
    else:
        asyncio.run(run_pipeline(args))

if __name__ == "__main__":
    main()
