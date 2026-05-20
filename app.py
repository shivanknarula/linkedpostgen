import os
import csv
import subprocess
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/scrape", methods=["POST"])
def run_scrape():
    try:
        # Run the scrape script
        # Using subprocess to run the exact command requested
        process = subprocess.Popen(
            ["python", "scrape_v2.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Wait for the process to finish
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            return jsonify({"status": "error", "message": stderr}), 500
            
        return jsonify({"status": "success", "message": "Scraping completed successfully.", "output": stdout})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/results", methods=["GET"])
def get_results():
    results = []
    csv_file = "robotics_posts.csv"
    if os.path.exists(csv_file):
        try:
            with open(csv_file, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    results.append(row)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Could not read CSV: {str(e)}"}), 500
            
    return jsonify({"status": "success", "data": results})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
