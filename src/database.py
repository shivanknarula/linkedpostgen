import sqlite3
import os
from datetime import datetime
from src.config import DB_PATH, GLOBAL_PROFILES, CHINESE_PROFILES

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enable Write-Ahead Log (WAL) mode for concurrency and speed
    cursor.execute("PRAGMA journal_mode=WAL;")
    
    # 1. Profiles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT CHECK(category IN ('global', 'chinese')) NOT NULL,
        tier INTEGER CHECK(tier IN (1, 2)) NOT NULL DEFAULT 2,
        last_crawled_at TIMESTAMP,
        is_active INTEGER NOT NULL DEFAULT 1
    );
    """)

    # 2. Crawl History Cache
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crawl_history (
        url TEXT PRIMARY KEY,
        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed INTEGER DEFAULT 0
    );
    """)

    # 3. Posts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        profile_id INTEGER,
        post_text TEXT NOT NULL,
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        published_date TEXT,
        category TEXT CHECK(category IN ('global', 'chinese')) NOT NULL,
        status TEXT CHECK(status IN ('discovered', 'extracted', 'filtered', 'scored')) NOT NULL DEFAULT 'discovered',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(profile_id) REFERENCES profiles(id)
    );
    """)

    # 4. Quality Scores Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        post_id INTEGER PRIMARY KEY,
        total_score INTEGER NOT NULL,
        novelty INTEGER NOT NULL,
        virality INTEGER NOT NULL,
        technical_depth INTEGER NOT NULL,
        ai_relevance INTEGER NOT NULL,
        robotics_relevance INTEGER NOT NULL,
        china_relevance INTEGER NOT NULL,
        founder_signal INTEGER NOT NULL,
        research_signal INTEGER NOT NULL,
        reasoning TEXT,
        evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
    );
    """)

    # 5. AI Generated Comments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS generated_comments (
        post_id INTEGER PRIMARY KEY,
        comment_text TEXT NOT NULL,
        approved INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
    );
    """)

    # 6. Crawl Runs Table (Observability)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crawl_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        duration_ms INTEGER,
        status TEXT CHECK(status IN ('running', 'success', 'failed')) NOT NULL,
        posts_discovered INTEGER DEFAULT 0,
        posts_extracted INTEGER DEFAULT 0,
        posts_scored INTEGER DEFAULT 0,
        error_message TEXT
    );
    """)

    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_total_score ON scores(total_score);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_tier ON profiles(tier);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_crawl_history_processed ON crawl_history(processed);")

    conn.commit()
    conn.close()
    
    # Seed profiles from config
    seed_profiles()

def seed_profiles():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Load all profiles from config
    all_config_profiles = GLOBAL_PROFILES + CHINESE_PROFILES
    config_urls = set()
    
    for p in all_config_profiles:
        config_urls.add(p["url"])
        cursor.execute("""
        INSERT INTO profiles (url, name, category, tier, is_active)
        VALUES (?, ?, ?, ?, 1)
        ON CONFLICT(url) DO UPDATE SET
            name = excluded.name,
            category = excluded.category,
            tier = excluded.tier,
            is_active = 1
        """, (p["url"], p["name"], p["category"], p["tier"]))
        
    # Mark profiles not in current config as inactive
    placeholders = ",".join("?" for _ in config_urls)
    cursor.execute(f"""
    UPDATE profiles SET is_active = 0 WHERE url NOT IN ({placeholders})
    """, tuple(config_urls))
    
    conn.commit()
    conn.close()

# Run logging helpers
def start_crawl_run():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO crawl_runs (status) VALUES ('running')
    """)
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id

def finish_crawl_run(run_id, status, posts_discovered, posts_extracted, posts_scored, error_message=None, duration_ms=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE crawl_runs
    SET status = ?, end_time = CURRENT_TIMESTAMP, posts_discovered = ?, posts_extracted = ?, posts_scored = ?, error_message = ?, duration_ms = ?
    WHERE id = ?
    """, (status, posts_discovered, posts_extracted, posts_scored, error_message, duration_ms, run_id))
    conn.commit()
    conn.close()

# Crawl History / URL Deduplication
def get_history_set():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM crawl_history")
    urls = {row['url'] for row in cursor.fetchall()}
    conn.close()
    return urls

def add_urls_to_history(urls):
    if not urls:
        return
    conn = get_db_connection()
    cursor = conn.cursor()
    for url in urls:
        cursor.execute("INSERT OR IGNORE INTO crawl_history (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()

# Posts management
def add_discovered_post(url, category, profile_url=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    profile_id = None
    if profile_url:
        cursor.execute("SELECT id FROM profiles WHERE url = ?", (profile_url,))
        row = cursor.fetchone()
        if row:
            profile_id = row['id']
            
    cursor.execute("""
    INSERT OR IGNORE INTO posts (url, profile_id, category, status, post_text)
    VALUES (?, ?, ?, 'discovered', '')
    """, (url, profile_id, category))
    conn.commit()
    conn.close()

def save_extracted_post(url, text, likes, comments, published_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE posts
    SET post_text = ?, likes = ?, comments = ?, published_date = ?, status = 'extracted'
    WHERE url = ?
    """, (text, likes, comments, published_date, url))
    
    # Mark in crawl_history as processed
    cursor.execute("""
    INSERT OR REPLACE INTO crawl_history (url, processed) VALUES (?, 1)
    """, (url,))
    
    conn.commit()
    conn.close()

def save_post_scoring(url, status, total_score=None, scores_dict=None, reasoning=None, comment_text=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM posts WHERE url = ?", (url,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return
    post_id = row['id']
    
    cursor.execute("UPDATE posts SET status = ? WHERE id = ?", (status, post_id))
    
    if total_score is not None and scores_dict is not None:
        cursor.execute("""
        INSERT OR REPLACE INTO scores (
            post_id, total_score, novelty, virality, technical_depth, 
            ai_relevance, robotics_relevance, china_relevance, founder_signal, research_signal, reasoning
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post_id, total_score,
            scores_dict.get('novelty', 0),
            scores_dict.get('virality', 0),
            scores_dict.get('technical_depth', 0),
            scores_dict.get('ai_relevance', 0),
            scores_dict.get('robotics_relevance', 0),
            scores_dict.get('china_relevance', 0),
            scores_dict.get('founder_signal', 0),
            scores_dict.get('research_signal', 0),
            reasoning
        ))
        
    if comment_text:
        cursor.execute("""
        INSERT OR REPLACE INTO generated_comments (post_id, comment_text)
        VALUES (?, ?)
        """, (post_id, comment_text))
        
    conn.commit()
    conn.close()

def get_unscored_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT url, post_text, category FROM posts 
    WHERE status = 'extracted' AND post_text != ''
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{'url': r['url'], 'text': r['post_text'], 'category': r['category']} for r in rows]

def get_results_list(limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query scored posts with scores and comments, sorted by total_score descending
    cursor.execute("""
    SELECT 
        p.url, 
        p.published_date as date, 
        p.post_text as text,
        p.likes, 
        p.comments, 
        p.category,
        s.total_score as score, 
        s.reasoning,
        c.comment_text as comment
    FROM posts p
    JOIN scores s ON p.id = s.post_id
    LEFT JOIN generated_comments c ON p.id = c.post_id
    ORDER BY s.total_score DESC, p.created_at DESC
    LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            'url': r['url'],
            'date': r['date'],
            'score': str(r['score']),
            'reasoning': r['reasoning'],
            'comment': r['comment'] or '',
            'likes': str(r['likes']),
            'comments': str(r['comments']),
            'text': r['text'],
            'category': r['category']
        })
    return results

def get_metrics_summary():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM profiles WHERE is_active = 1")
    active_profiles = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM posts")
    total_posts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM posts WHERE status = 'scored'")
    scored_posts = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(total_score) FROM scores")
    avg_score = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM crawl_runs")
    total_runs = cursor.fetchone()[0]
    
    cursor.execute("SELECT * FROM crawl_runs ORDER BY id DESC LIMIT 5")
    latest_runs = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return {
        "active_profiles": active_profiles,
        "total_posts_discovered": total_posts,
        "total_posts_scored": scored_posts,
        "average_score": round(avg_score, 1),
        "total_runs": total_runs,
        "latest_runs": latest_runs
    }

def export_to_legacy_files():
    """Exports SQLite scored posts to robotics_posts.csv and text files for Vercel/legacy compatibility."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch scored posts for CSV
    cursor.execute("""
    SELECT 
        p.url, 
        p.published_date as date, 
        p.post_text as text,
        p.likes, 
        p.comments, 
        p.category,
        s.total_score as score, 
        s.reasoning,
        c.comment_text as comment
    FROM posts p
    JOIN scores s ON p.id = s.post_id
    LEFT JOIN generated_comments c ON p.id = c.post_id
    ORDER BY s.total_score DESC, p.created_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    import csv
    keys = ['url', 'date', 'score', 'reasoning', 'comment', 'likes', 'comments', 'text', 'category']
    
    # Write to CSV
    csv_file = "robotics_posts.csv"
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for r in rows:
                # scale score back to 0-10 for CSV compatibility
                score_scaled = str(r['score'] // 10)
                writer.writerow({
                    'url': r['url'],
                    'date': r['date'],
                    'score': score_scaled,
                    'reasoning': r['reasoning'],
                    'comment': r['comment'] or '',
                    'likes': str(r['likes']),
                    'comments': str(r['comments']),
                    'text': r['text'],
                    'category': r['category']
                })
        print(f"[*] Exported {len(rows)} posts to {csv_file}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        
    # Write to high_value_comments.txt and all_scraped_posts.txt
    try:
        with open("high_value_comments.txt", "w", encoding="utf-8") as f_high, \
             open("all_scraped_posts.txt", "w", encoding="utf-8") as f_all:
             
            for r in rows:
                score_scaled = r['score'] // 10
                text_block = (
                    f"LINK: {r['url']}\n"
                    f"DATE: {r['date']}\n"
                    f"METRICS: {r['likes']} Likes, {r['comments']} Comments\n"
                    f"SCORE: {score_scaled}/10 - {r['reasoning']}\n"
                    f"CATEGORY: {r['category']}\n"
                    f"AI COMMENT:\n{r['comment'] or 'N/A'}\n"
                    f"TEXT:\n{r['text']}\n"
                    f"{'='*80}\n\n"
                )
                f_all.write(text_block)
                if score_scaled >= 6:
                    f_high.write(text_block)
        print("[*] Exported txt files successfully.")
    except Exception as e:
        print(f"Error exporting to txt files: {e}")

    # Export history to generated_links_history.txt
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM crawl_history")
        urls = [row['url'] for row in cursor.fetchall()]
        conn.close()
        
        with open("generated_links_history.txt", "w", encoding="utf-8") as f:
            for url in urls:
                f.write(f"{url}\n")
        print(f"[*] Exported {len(urls)} history links to generated_links_history.txt")
    except Exception as e:
        print(f"Error exporting history: {e}")

