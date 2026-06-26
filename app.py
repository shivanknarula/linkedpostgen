import os
import subprocess
from flask import Flask, render_template, jsonify
from src.database import get_results_list, get_metrics_summary

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
            f.write("[*] Starting LinkedIn Intelligence Platform async background process...\n")
            
        log_file = open("scrape_run.log", "a", encoding="utf-8")
        
        # Start new async orchestrator as background process
        current_process = subprocess.Popen(
            ["node", "crawler.js"],
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
    try:
        results = get_results_list(limit=50)
        return jsonify({"status": "success", "data": results})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Could not read results: {str(e)}"}), 500

@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    try:
        metrics = get_metrics_summary()
        return jsonify({"status": "success", "metrics": metrics})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Could not read metrics: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
