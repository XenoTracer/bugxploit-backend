from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/scan": {"origins": "https://bugxploit.netlify.app"}})

@app.route('/')
def home():
    return jsonify({"status": "BugXploit API is live"}), 200


def get_subdomains_otx(domain):
    try:
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
        headers = {
            "User-Agent": "BugXploit Recon Engine"
        }
        response = requests.get(url, headers=headers, timeout=15)

        if not response.ok:
            return ["❌ AlienVault API error"]

        data = response.json()
        subdomains = set()

        for entry in data.get("passive_dns", []):
            hostname = entry.get("hostname")
            if hostname and domain in hostname:
                subdomains.add(hostname.strip())

        if not subdomains:
            return ["⚠️ No subdomains found."]

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
        subdomains = get_subdomains_otx(target)

        return jsonify({
            "subdomains": subdomains,
            "nmap": "⚠️ Nmap not available on Render. Switch to VPS for full port scans."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
