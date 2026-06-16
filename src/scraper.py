import asyncio
import os
import random
from datetime import datetime
from playwright.async_api import async_playwright
from src.config import MAX_CONCURRENT_TABS, HEADLESS, PAGE_TIMEOUT_MS, STEADY_STATE_TIMEOUT_MS

class AsyncLinkedInScraper:
    def __init__(self, state_file="session.json"):
        self.state_file = state_file
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_TABS)
        
    async def block_assets(self, route):
        """Intercept and block heavy resources to minimize load times."""
        if route.request.resource_type in ["image", "stylesheet", "media", "font", "other"]:
            await route.abort()
        else:
            await route.continue_()

    async def verify_session(self, page) -> bool:
        """Rapid validation of stored LinkedIn session state."""
        try:
            print("[*] Verifying LinkedIn session...")
            await page.route("**/*", self.block_assets)
            await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=12000)
            await page.wait_for_timeout(1000)
            url = page.url
            if "login" in url or "uas/login" in url:
                print("[!] LinkedIn login session has expired.")
                return False
            print("    LinkedIn session is active.")
            return True
        except Exception as e:
            print(f"[!] Session verification failed/timed out: {e}")
            return False

    async def fetch_profile_post_urls(self, context, profile_url, history_set) -> list:
        """Scrapes a single profile for recent posts concurrently under semaphore control."""
        async with self.semaphore:
            posts_url = profile_url.rstrip('/') + '/recent-activity/all/'
            page = await context.new_page()
            await page.route("**/*", self.block_assets)
            
            discovered_urls = []
            try:
                print(f" -> Fetching profile posts: {profile_url}")
                await page.goto(posts_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
                await page.wait_for_timeout(STEADY_STATE_TIMEOUT_MS)
                
                # Single brief scroll to reveal 5-10 recent posts
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(700)
                
                # Search for post links
                links = await page.query_selector_all('a')
                for link in links:
                    href = await link.get_attribute('href')
                    if href:
                        clean_url = href.split('?')[0].split('&')[0]
                        if clean_url.startswith('/'):
                            clean_url = "https://www.linkedin.com" + clean_url
                        if ('/posts/' in clean_url or 'activity-' in clean_url) and clean_url not in history_set:
                            discovered_urls.append(clean_url)
            except Exception as e:
                print(f"    ! Failed scraping profile {profile_url}: {e}")
            finally:
                await page.close()
            return list(set(discovered_urls))

    async def extract_single_post_content(self, context, post_url) -> dict:
        """Navigates to a single post URL and extracts text and metrics."""
        async with self.semaphore:
            page = await context.new_page()
            await page.route("**/*", self.block_assets)
            
            result = None
            try:
                print(f" -> Extracting post content: {post_url}")
                await page.goto(post_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
                
                # Dismiss login popups if any
                try:
                    await page.locator('button[icon="x-icon"]').click(timeout=1000)
                except:
                    pass
                
                # Click "see more" if present
                try:
                    await page.locator('.see-more').first.click(timeout=800)
                except:
                    pass
                
                # Extract main text
                text = ""
                main_loc = page.locator('article')
                if await main_loc.count() > 0:
                    text = await main_loc.first.inner_text()
                else:
                    text = await page.locator('body').inner_text()
                    if text:
                        text = text[:4000]
                
                # Clean text
                text = text.replace('\n\n', '\n').strip() if text else ""
                
                # Extract metrics
                likes = 0
                comments = 0
                try:
                    social_loc = page.locator('.social-details-social-counts').first
                    if await social_loc.count() > 0:
                        social_text = await social_loc.inner_text(timeout=1000)
                        if 'Like' in social_text:
                            likes_str = social_text.split('Like')[0].strip().replace(',', '')
                            if likes_str.isdigit():
                                likes = int(likes_str)
                        if 'Comment' in social_text:
                            comments_parts = social_text.split('Comment')[0].split('\n')
                            comment_str = comments_parts[-1].strip().replace(',', '')
                            if comment_str.isdigit():
                                comments = int(comment_str)
                except:
                    pass
                
                published_date = datetime.now().strftime("%Y-%m-%d")
                
                result = {
                    'url': post_url,
                    'text': text,
                    'likes': likes,
                    'comments': comments,
                    'date': published_date
                }
            except Exception as e:
                print(f"    ! Failed post extraction for {post_url}: {e}")
            finally:
                await page.close()
            return result
