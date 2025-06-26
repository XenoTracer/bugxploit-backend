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
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=15)

        if not response.ok:
            return ["⚠️ crt.sh returned an error."]

        try:
            data = response.json()
        except Exception:
            return ["⚠️ crt.sh did not return valid JSON."]

        subdomains = set()
        for entry in data:
            name = entry.get('name_value')
            if name:
                for sub in name.split('\n'):
                    if '*' not in sub:
                        subdomains.add(sub.strip())

        if not subdomains:
            return ["⚠️ No subdomains found. Domain might not have SSL certificates."]

        return list(sorted(subdomains))

    except Exception as e:
        return [f"❌ Error: {str(e)}"]

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
