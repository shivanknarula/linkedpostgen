import asyncio
import json
import os
from groq import AsyncGroq
from src.config import GROQ_MODEL, MAX_CONCURRENT_GROQ_CALLS, HEURISTIC_KEYWORDS, BLACK_LIST_PHRASES

class AIScoringPipeline:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.client = AsyncGroq(api_key=self.api_key)
        else:
            self.client = None
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_GROQ_CALLS)

    def stage1_rule_filter(self, text: str) -> bool:
        """Discard obviously short, promotional, or irrelevant posts quickly without calling APIs."""
        if not text or len(text) < 70:
            return False
            
        # Check against blacklist phrases
        text_lower = text.lower()
        if any(phrase in text_lower for phrase in BLACK_LIST_PHRASES):
            return False
            
        return True

    def stage2_heuristic_relevance(self, text: str) -> bool:
        """Heuristic relevance check: requires at least one domain keyword to match."""
        text_lower = text.lower()
        return any(kw in text_lower for kw in HEURISTIC_KEYWORDS)

    async def stage3_llm_score(self, post_text: str, category: str) -> dict:
        """Sends the post to Groq asynchronously to extract granular metrics, reasonings, and comments."""
        if not self.client:
            return {
                "total_score": 0, "novelty": 0, "virality": 0, "technical_depth": 0,
                "ai_relevance": 0, "robotics_relevance": 0, "china_relevance": 0,
                "founder_signal": 0, "research_signal": 0,
                "reasoning": "Missing GROQ_API_KEY", "comment": ""
            }

        prompt = f"""
        You are an expert evaluator for a high-value global AI and Robotics Intelligence Platform.
        Analyze the following LinkedIn post (Category: {category}) and rate it against our quality parameters.
        Each metric score MUST be an integer between 0 and 10.
        
        Quality Matrix:
        1. Novelty: Is it presenting a new breakthrough, project, code, or perspective?
        2. Virality: Does it have strong engagement signals or potential for high reach?
        3. Technical Depth: Does it contain implementation details, code links, metrics, or architectural concepts?
        4. AI Relevance: Is it directly relevant to Artificial Intelligence, LLMs, or agents?
        5. Robotics Relevance: Is it directly relevant to physical/embodied robotics or humanoid control?
        6. China Relevance: For Chinese posts, is it highlighting breakthroughs or key developments in the Chinese AI ecosystem?
        7. Founder Signal: Is it written by or directly discussing a high-signal founder or CEO?
        8. Research Signal: Does it discuss academic papers, researchers, labs, or training methodologies?

        Write a professional, detailed comment (1-3 sentences) in the persona of an expert Robotics Engineer and Startup Founder only if the total score is 65 or higher. The comment should validate the poster, add a deep technical insight or contrarian perspective, and end with an open-ended question. If the total score is less than 65, leave the comment blank.

        You MUST respond in strict JSON format. Do not write any conversational text.
        
        Response Schema:
        {{
            "total_score": <integer 0-100 indicating overall platform value>,
            "novelty": <0-10>,
            "virality": <0-10>,
            "technical_depth": <0-10>,
            "ai_relevance": <0-10>,
            "robotics_relevance": <0-10>,
            "china_relevance": <0-10>,
            "founder_signal": <0-10>,
            "research_signal": <0-10>,
            "reasoning": "<short description explaining score>",
            "comment": "<comment or empty string>"
        }}

        Post text:
        {post_text[:3000]}
        """

        async with self.semaphore:
            max_retries = 5
            backoff = 2.0
            for attempt in range(max_retries):
                try:
                    response = await self.client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=GROQ_MODEL,
                        response_format={"type": "json_object"},
                        max_tokens=350,
                        temperature=0.2
                    )
                    raw_json = response.choices[0].message.content.strip()
                    data = json.loads(raw_json)
                    return data
                except Exception as e:
                    err_str = str(e)
                    is_rate_limit = "429" in err_str or "rate limit" in err_str.lower()
                    if is_rate_limit and attempt < max_retries - 1:
                        # Extract wait time if possible, e.g. "try again in 9.22s"
                        sleep_time = backoff
                        import re
                        match = re.search(r"try again in (\d+\.?\d*)s", err_str)
                        if match:
                            sleep_time = float(match.group(1)) + 0.5
                        else:
                            sleep_time = backoff
                            backoff *= 2.0
                        print(f"    [!] Groq rate limit hit. Retrying in {sleep_time:.2f}s... (Attempt {attempt+1}/{max_retries})")
                        await asyncio.sleep(sleep_time)
                    else:
                        print(f"    ! Groq scoring API error: {e}")
                        return None

    async def evaluate_posts(self, posts: list) -> list:
        """Evaluates a batch of posts in parallel using asynchronous tasks."""
        evaluated_results = []
        tasks = []
        
        # Filtering phases
        posts_to_score = []
        for post in posts:
            url = post['url']
            text = post['text']
            category = post['category']
            
            # Stage 1 rule filter
            if not self.stage1_rule_filter(text):
                print(f"    - Post filtered at Stage 1 (rule check): {url[:50]}...")
                continue
                
            # Stage 2 heuristic relevance
            if not self.stage2_heuristic_relevance(text):
                print(f"    - Post filtered at Stage 2 (heuristics): {url[:50]}...")
                continue
                
            posts_to_score.append(post)
            
        print(f"[*] Batch Evaluation: {len(posts_to_score)} / {len(posts)} posts passed Stages 1 & 2.")
        
        # Stage 3 Groq scoring
        for post in posts_to_score:
            tasks.append(self.stage3_llm_score(post['text'], post['category']))
            
        llm_results = await asyncio.gather(*tasks)
        
        for post, res in zip(posts_to_score, llm_results):
            if res:
                # Merge metadata with results
                post['score_data'] = res
                evaluated_results.append(post)
                
        # Stage 4: Sort by total_score descending
        evaluated_results.sort(key=lambda x: x['score_data'].get('total_score', 0), reverse=True)
        return evaluated_results
