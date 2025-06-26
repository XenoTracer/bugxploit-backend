from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app, resources={r"/scan": {"origins": "https://bugxploit.netlify.app"}})

@app.route('/')
def home():
    return jsonify({"status": "BugXploit API is live"}), 200

def get_subdomains_crtsh(domain):
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        response = requests.get(url, timeout=15)
        if response.ok:
            data = response.json()
            subdomains = set()
            for entry in data:
                name = entry['name_value']
                for sub in name.split('\n'):
                    if '*' not in sub:
                        subdomains.add(sub.strip())
            return list(sorted(subdomains))
        else:
            return ["Failed to fetch data"]
    except Exception as e:
        return [f"Error fetching subdomains: {str(e)}"]

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    target = data.get('target')

    if not target:
        return jsonify({"error": "No target provided"}), 400

    try:
        subdomains = get_subdomains_crtsh(target)

        return jsonify({
            "subdomains": subdomains,
            "nmap": "⚠️ Nmap not available on Render. Switch to VPS for full port scans."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
