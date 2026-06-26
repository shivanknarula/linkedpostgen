import sqlite3
import urllib.request
import json
import os
import re
from datetime import datetime

SUPABASE_URL = "https://jhsvvmpyybyoroxeevqh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impoc3Z2bXB5eWJ5b3JveGVldnFoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTc5MjQ4NSwiZXhwIjoyMDk3MzY4NDg1fQ.baEy5mto1xm_QDBZl1bwQ29kY2PmWgCN8k0N7R69p40"
DB_PATH = "robotics_intelligence.db"

def get_from_supabase(table, select="*"):
    url = f"{SUPABASE_URL}/rest/v1/{table}?select={select}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"[!] Error fetching from {table}: {e}")
        if hasattr(e, "read"):
            print("Response Details:", e.read().decode())
        return []

def post_to_supabase(table, data, conflict_column=None):
    if not data:
        return
    
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if conflict_column:
        url += f"?on_conflict={conflict_column}"
        
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            print(f"[+] Successfully migrated {len(data)} rows to {table}. Status: {response.status}")
    except Exception as e:
        print(f"[!] Error migrating to {table}: {e}")
        if hasattr(e, "read"):
            print("Response Details:", e.read().decode())

def normalize_timestamp(ts_str):
    if not ts_str:
        return None
    # Remove timezone offset/suffix like +00:00, Z, etc.
    cleaned = re.sub(r'(\+|-)\d{2}:?\d{2}$', '', ts_str)
    cleaned = cleaned.replace('Z', '')
    # Replace 'T' with ' '
    cleaned = cleaned.replace('T', ' ')
    # Strip microsecond parts if any
    if '.' in cleaned:
        cleaned = cleaned.split('.')[0]
    cleaned = cleaned.strip()
    try:
        return datetime.strptime(cleaned, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"[!] SQLite DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # ==========================================
    # 1. Migrate Profiles
    # ==========================================
    cursor.execute("SELECT id, url, name, category, tier, last_crawled_at, is_active FROM profiles")
    sqlite_profiles = cursor.fetchall()
    
    profiles_payload = []
    sqlite_profile_url_map = {}
    for r in sqlite_profiles:
        sqlite_profile_url_map[r["id"]] = r["url"]
        profiles_payload.append({
            "url": r["url"],
            "name": r["name"],
            "category": r["category"],
            "tier": r["tier"],
            "last_crawled_at": r["last_crawled_at"],
            "is_active": bool(r["is_active"])
        })
        
    print(f"[*] Found {len(profiles_payload)} profiles in SQLite.")
    post_to_supabase("profiles", profiles_payload, "url")

    # Fetch updated profile mappings from Supabase
    supabase_profiles = get_from_supabase("profiles", "id,url")
    supabase_profile_map = {p["url"]: p["id"] for p in supabase_profiles}

    # ==========================================
    # 2. Migrate Crawl History
    # ==========================================
    cursor.execute("SELECT url, discovered_at, processed FROM crawl_history")
    history_payload = []
    for r in cursor.fetchall():
        history_payload.append({
            "url": r["url"],
            "discovered_at": r["discovered_at"],
            "processed": bool(r["processed"])
        })
    print(f"[*] Found {len(history_payload)} history entries in SQLite.")
    post_to_supabase("crawl_history", history_payload, "url")

    # ==========================================
    # 3. Migrate Posts
    # ==========================================
    cursor.execute("SELECT id, url, profile_id, post_text, likes, comments, published_date, category, status, created_at FROM posts")
    sqlite_posts = cursor.fetchall()
    
    posts_payload = []
    sqlite_post_url_map = {}
    for r in sqlite_posts:
        sqlite_post_url_map[r["id"]] = r["url"]
        profile_url = sqlite_profile_url_map.get(r["profile_id"])
        supabase_profile_id = supabase_profile_map.get(profile_url) if profile_url else None
        
        posts_payload.append({
            "url": r["url"],
            "profile_id": supabase_profile_id,
            "post_text": r["post_text"],
            "likes": r["likes"],
            "comments": r["comments"],
            "published_date": r["published_date"],
            "category": r["category"],
            "status": r["status"],
            "created_at": r["created_at"]
        })
        
    print(f"[*] Found {len(posts_payload)} posts in SQLite.")
    batch_size = 100
    for i in range(0, len(posts_payload), batch_size):
        post_to_supabase("posts", posts_payload[i:i+batch_size], "url")

    # Fetch updated post mappings from Supabase
    supabase_posts = get_from_supabase("posts", "id,url")
    supabase_post_map = {p["url"]: p["id"] for p in supabase_posts}

    # ==========================================
    # 4. Migrate Scores
    # ==========================================
    cursor.execute("SELECT post_id, total_score, novelty, virality, technical_depth, ai_relevance, robotics_relevance, china_relevance, founder_signal, research_signal, reasoning, evaluated_at FROM scores")
    scores_payload = []
    for r in cursor.fetchall():
        post_url = sqlite_post_url_map.get(r["post_id"])
        supabase_post_id = supabase_post_map.get(post_url) if post_url else None
        if supabase_post_id:
            scores_payload.append({
                "post_id": supabase_post_id,
                "total_score": r["total_score"],
                "novelty": r["novelty"],
                "virality": r["virality"],
                "technical_depth": r["technical_depth"],
                "ai_relevance": r["ai_relevance"],
                "robotics_relevance": r["robotics_relevance"],
                "china_relevance": r["china_relevance"],
                "founder_signal": r["founder_signal"],
                "research_signal": r["research_signal"],
                "reasoning": r["reasoning"],
                "evaluated_at": r["evaluated_at"]
            })
            
    print(f"[*] Found {len(scores_payload)} valid scores mapped to Supabase posts.")
    for i in range(0, len(scores_payload), batch_size):
        post_to_supabase("scores", scores_payload[i:i+batch_size], "post_id")

    # ==========================================
    # 5. Migrate Generated Comments
    # ==========================================
    cursor.execute("SELECT post_id, comment_text, approved, created_at FROM generated_comments")
    comments_payload = []
    for r in cursor.fetchall():
        post_url = sqlite_post_url_map.get(r["post_id"])
        supabase_post_id = supabase_post_map.get(post_url) if post_url else None
        if supabase_post_id:
            comments_payload.append({
                "post_id": supabase_post_id,
                "comment_text": r["comment_text"],
                "approved": bool(r["approved"]),
                "created_at": r["created_at"]
            })
            
    print(f"[*] Found {len(comments_payload)} valid generated comments mapped to Supabase posts.")
    for i in range(0, len(comments_payload), batch_size):
        post_to_supabase("generated_comments", comments_payload[i:i+batch_size], "post_id")

    # ==========================================
    # 6. Migrate Crawl Runs
    # ==========================================
    cursor.execute("SELECT start_time, end_time, duration_ms, status, posts_discovered, posts_extracted, posts_scored, error_message FROM crawl_runs")
    sqlite_runs = cursor.fetchall()
    
    supabase_runs = get_from_supabase("crawl_runs", "start_time")
    supabase_start_times = []
    for r in supabase_runs:
        norm = normalize_timestamp(r.get("start_time"))
        if norm:
            supabase_start_times.append(norm)
            
    runs_to_insert = []
    for r in sqlite_runs:
        norm_local = normalize_timestamp(r["start_time"])
        if not norm_local:
            continue
        exists = False
        for s_time in supabase_start_times:
            if abs((norm_local - s_time).total_seconds()) < 10:
                exists = True
                break
        if not exists:
            runs_to_insert.append({
                "start_time": r["start_time"],
                "end_time": r["end_time"],
                "duration_ms": r["duration_ms"],
                "status": r["status"],
                "posts_discovered": r["posts_discovered"],
                "posts_extracted": r["posts_extracted"],
                "posts_scored": r["posts_scored"],
                "error_message": r["error_message"]
            })
            
    print(f"[*] Found {len(runs_to_insert)} new crawl runs to insert.")
    if runs_to_insert:
        post_to_supabase("crawl_runs", runs_to_insert)

    conn.close()
    print("[*] Migration complete!")

if __name__ == "__main__":
    migrate()
