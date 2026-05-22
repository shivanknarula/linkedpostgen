import os
import csv
import subprocess
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

current_process = None

@app.route("/api/scrape", methods=["POST"])
def run_scrape():
    global current_process
    
    # Check if a process is already running
    if current_process is not None and current_process.poll() is None:
        return jsonify({"status": "error", "message": "Scraper is already running."}), 400
        
    try:
        # Initialize and clear log file
        with open("scrape_run.log", "w", encoding="utf-8") as f:
            f.write("[*] Starting LinkedIn Scraper background process...\n")
            
        log_file = open("scrape_run.log", "a", encoding="utf-8")
        
        # Start scraper as background process
        current_process = subprocess.Popen(
            ["python", "-u", "scrape_v2.py"],
            stdout=log_file,
            stderr=log_file,
            text=True
        )
        log_file.close() # close duplicate parent handle, subprocess continues writing
        
        return jsonify({
            "status": "success", 
            "message": "Scraper successfully started in the background."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/scrape/status", methods=["GET"])
def get_scrape_status():
    global current_process
    
    running = False
    if current_process is not None:
        if current_process.poll() is None:
            running = True
            
    logs = ""
    if os.path.exists("scrape_run.log"):
        try:
            with open("scrape_run.log", "r", encoding="utf-8") as f:
                logs = f.read()
        except Exception as e:
            logs = f"Error reading logs: {str(e)}"
            
    return jsonify({
        "status": "success",
        "running": running,
        "logs": logs
    })

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
