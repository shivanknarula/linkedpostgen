import asyncio
import random
import urllib.parse
from src.config import GLOBAL_PROFILES, CHINESE_PROFILES, GLOBAL_QUERIES, CHINESE_QUERIES, MAX_CONCURRENT_TABS, PAGE_TIMEOUT_MS
from src.scraper import AsyncLinkedInScraper

class DiscoveryEngine:
    def __init__(self, scraper: AsyncLinkedInScraper):
        self.scraper = scraper

    async def get_crawling_targets(self, conn) -> tuple:
        """Determines the active profiles to crawl based on tiers."""
        cursor = conn.cursor()
        
        # Load Tier 1 always
        cursor.execute("SELECT url, category FROM profiles WHERE tier = 1 AND is_active = 1")
        tier1 = [{'url': r['url'], 'category': r['category']} for r in cursor.fetchall()]
        
        # Load Tier 2 rotating pool: grab a random subset of 12 profiles
        cursor.execute("SELECT url, category FROM profiles WHERE tier = 2 AND is_active = 1")
        all_tier2 = [{'url': r['url'], 'category': r['category']} for r in cursor.fetchall()]
        
        # Pick 12 random Tier 2 profiles (or all if fewer than 12)
        tier2_sample = random.sample(all_tier2, min(len(all_tier2), 12)) if all_tier2 else []
        
        return tier1, tier2_sample

    async def run_search_query_linkedin(self, page, query, history_set, limit=15) -> list:
        """Performs a LinkedIn keyword search to discover post URLs asynchronously."""
        urls = []
        encoded_q = urllib.parse.quote(query)
        POST_PATTERNS = ("/posts/", "/feed/update/urn:li:activity:", "activity-", "/pulse/")
        
        try:
            # We search pages 1 and 2 max for efficiency
            for page_no in range(1, 3):
                search_url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_q}&page={page_no}&origin=GLOBAL_SEARCH_HEADER"
                print(f" -> Searching LinkedIn: {query} (Page {page_no})")
                await page.goto(search_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
                await page.wait_for_timeout(2000)
                
                # Single quick scroll
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)
                
                links = await page.query_selector_all('a')
                for link in links:
                    href = await link.get_attribute('href')
                    if href:
                        clean_url = href.split('?')[0].split('&')[0]
                        if clean_url.startswith('/'):
                            clean_url = "https://www.linkedin.com" + clean_url
                        if any(p in clean_url for p in POST_PATTERNS) and clean_url not in history_set and clean_url not in urls:
                            urls.append(clean_url)
                            if len(urls) >= limit:
                                break
                if len(urls) >= limit:
                    break
        except Exception as e:
            print(f"    ! LinkedIn search failed for '{query}': {e}")
        return urls

    async def run_search_query_yahoo(self, page, query, history_set, limit=15) -> list:
        """Performs a Yahoo US Search to discover post URLs asynchronously (no login needed)."""
        urls = []
        search_query = f'site:linkedin.com/posts {query}'
        encoded_query = urllib.parse.quote(search_query)
        yahoo_url = f"https://us.search.yahoo.com/search?p={encoded_query}&cc=us&vc=us"
        
        try:
            print(f" -> Searching Yahoo US Fallback: {query}")
            await page.goto(yahoo_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
            await page.wait_for_timeout(2000)
            
            links = await page.query_selector_all('a')
            for link in links:
                href = await link.get_attribute('href')
                if href:
                    if "yahoo.com" in href:
                        continue
                    if "linkedin.com/posts/" in href or "linkedin.com/pulse/" in href or "/posts/" in href:
                        clean_url = href.split('?')[0].split('&')[0]
                        if clean_url not in history_set and clean_url not in urls:
                            urls.add(clean_url) if isinstance(urls, set) else urls.append(clean_url)
                            print(f"    + Discovered via Yahoo: {clean_url}")
                            if len(urls) >= limit:
                                break
        except Exception as e:
            print(f"    ! Yahoo search failed: {e}")
        return urls

    async def run_single_search_query(self, context, category, query, history_set, is_active_session, limit) -> list:
        """Runs a single search query in a separate browser page under semaphore control."""
        async with self.scraper.semaphore:
            page = await context.new_page()
            await page.route("**/*", self.scraper.block_assets)
            found_urls = []
            try:
                if is_active_session:
                    found_urls = await self.run_search_query_linkedin(page, query, history_set, limit=limit)
                else:
                    found_urls = await self.run_search_query_yahoo(page, query, history_set, limit=limit)
            except Exception as e:
                print(f"    ! Search failed for '{query}': {e}")
            finally:
                await page.close()
            return [{'url': url, 'category': category, 'profile_url': None} for url in found_urls]

    async def discover_urls(self, context, profiles, history_set, is_active_session=True) -> list:
        """Orchestrates multi-profile concurrent fetching."""
        tasks = []
        for p in profiles:
            tasks.append(self.scraper.fetch_profile_post_urls(context, p['url'], history_set))
            
        results = await asyncio.gather(*tasks)
        
        discovered = []
        for profile, urls in zip(profiles, results):
            for u in urls:
                discovered.append({'url': u, 'category': profile['category'], 'profile_url': profile['url']})
        return discovered

    async def run_discovery(self, context, db_conn, is_active_session=True, target_limit=50) -> list:
        """Core Orchestrator for URL discovery across all tiers."""
        history_set = {r['url'] for r in db_conn.execute("SELECT url FROM crawl_history").fetchall()}
        
        tier1, tier2 = await self.get_crawling_targets(db_conn)
        profiles_to_crawl = tier1 + tier2
        
        print(f"[*] Discovery Phase: Crawling {len(profiles_to_crawl)} profiles...")
        discovered_candidates = []
        
        if is_active_session and profiles_to_crawl:
            # Tier 1 & Tier 2: Crawl profiles concurrently
            candidates = await self.discover_urls(context, profiles_to_crawl, history_set, is_active_session=True)
            discovered_candidates.extend(candidates)
            
        print(f"[*] Discovered {len(discovered_candidates)} posts from direct profile crawls.")
        
        # Check if we need more candidate URLs to meet target_limit
        if len(discovered_candidates) < target_limit:
            remaining = target_limit - len(discovered_candidates)
            print(f"[*] Discovery limit not reached. Running Tier 3/4 Search Discoveries (needs {remaining} more)...")
            
            # Combine queries
            queries = [
                *(('global', q) for q in GLOBAL_QUERIES),
                *(('chinese', q) for q in CHINESE_QUERIES)
            ]
            
            # Execute search queries concurrently under semaphore control
            tasks = [
                self.run_single_search_query(context, category, query, history_set, is_active_session, limit=10)
                for category, query in queries
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Flatten results and append to candidates
            for res_list in results:
                for item in res_list:
                    if not any(c['url'] == item['url'] for c in discovered_candidates):
                        discovered_candidates.append(item)
            
        return discovered_candidates[:target_limit]
