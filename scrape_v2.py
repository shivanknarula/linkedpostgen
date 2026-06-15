# scrape_v2.py
# Forwarder wrapper for executing the new asynchronous module-based pipeline (src/main.py)
# This keeps the Vercel API, app.py, and GitHub Actions workflow fully backwards-compatible without changes.

from src.main import main

if __name__ == "__main__":
    main()
