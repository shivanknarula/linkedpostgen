import sqlite3
import urllib.request
import json
import os

SUPABASE_URL = "https://jhsvvmpyybyoroxeevqh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impoc3Z2bXB5eWJ5b3JveGVldnFoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTc5MjQ4NSwiZXhwIjoyMDk3MzY4NDg1fQ.baEy5mto1xm_QDBZl1bwQ29kY2PmWgCN8k0N7R69p40"
DB_PATH = "robotics_intelligence.db"

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

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"[!] SQLite DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Migrate Profiles
    cursor.execute("SELECT id, url, name, category, tier, last_crawled_at, is_active FROM profiles")
    profiles = []
    for r in cursor.fetchall():
        profiles.append({
            "id": r["id"],
            "url": r["url"],
            "name": r["name"],
            "category": r["category"],
            "tier": r["tier"],
            "last_crawled_at": r["last_crawled_at"],
            "is_active": bool(r["is_active"])
        })
    print(f"[*] Found {len(profiles)} profiles in SQLite.")
    post_to_supabase("profiles", profiles, "url")

    # 2. Migrate Crawl History
    cursor.execute("SELECT url, discovered_at, processed FROM crawl_history")
    history = []
    for r in cursor.fetchall():
        history.append({
            "url": r["url"],
            "discovered_at": r["discovered_at"],
            "processed": bool(r["processed"])
        })
    print(f"[*] Found {len(history)} history entries in SQLite.")
    post_to_supabase("crawl_history", history, "url")

    # 3. Migrate Posts
    cursor.execute("SELECT id, url, profile_id, post_text, likes, comments, published_date, category, status, created_at FROM posts")
    posts = []
    valid_post_ids = set()
    for r in cursor.fetchall():
        posts.append({
            "id": r["id"],
            "url": r["url"],
            "profile_id": r["profile_id"],
            "post_text": r["post_text"],
            "likes": r["likes"],
            "comments": r["comments"],
            "published_date": r["published_date"],
            "category": r["category"],
            "status": r["status"],
            "created_at": r["created_at"]
        })
        valid_post_ids.add(r["id"])
    print(f"[*] Found {len(posts)} posts in SQLite.")
    
    batch_size = 100
    for i in range(0, len(posts), batch_size):
        post_to_supabase("posts", posts[i:i+batch_size], "url")

    # 4. Migrate Scores (filtering out orphaned scores)
    cursor.execute("SELECT post_id, total_score, novelty, virality, technical_depth, ai_relevance, robotics_relevance, china_relevance, founder_signal, research_signal, reasoning, evaluated_at FROM scores")
    scores = []
    for r in cursor.fetchall():
        if r["post_id"] in valid_post_ids:
            scores.append({
                "post_id": r["post_id"],
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
    print(f"[*] Found {len(scores)} valid scores (matching posts) in SQLite.")
    for i in range(0, len(scores), batch_size):
        post_to_supabase("scores", scores[i:i+batch_size], "post_id")

    # 5. Migrate Generated Comments (filtering out orphaned comments)
    cursor.execute("SELECT post_id, comment_text, approved, created_at FROM generated_comments")
    comments = []
    for r in cursor.fetchall():
        if r["post_id"] in valid_post_ids:
            comments.append({
                "post_id": r["post_id"],
                "comment_text": r["comment_text"],
                "approved": bool(r["approved"]),
                "created_at": r["created_at"]
            })
    print(f"[*] Found {len(comments)} valid generated comments in SQLite.")
    post_to_supabase("generated_comments", comments, "post_id")

    conn.close()
    print("[*] Migration complete!")

if __name__ == "__main__":
    migrate()
