from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)

# Restrict CORS to your frontend only
CORS(app, resources={r"/scan": {"origins": "https://bugxploit.netlify.app"}})

@app.route('/')
def home():
    return jsonify({"status": "BugXploit API is live"}), 200

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    target = data.get('target')

    if not target:
        return jsonify({"error": "No target provided"}), 400

    try:
        # Run Subfinder
        subfinder_cmd = ["subfinder", "-d", target, "-silent"]
        subfinder_result = subprocess.run(subfinder_cmd, capture_output=True, text=True, timeout=30)

        # Run Nmap
        nmap_cmd = ["nmap", "-T4", "--top-ports", "100", target]
        nmap_result = subprocess.run(nmap_cmd, capture_output=True, text=True, timeout=60)

        return jsonify({
            "subdomains": subfinder_result.stdout.splitlines(),
            "nmap": nmap_result.stdout
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT dynamically
    app.run(host="0.0.0.0", port=port)
