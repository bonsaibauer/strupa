import re
import requests
from pathlib import Path
from dotenv import load_dotenv
import os

# 📍 Pfade
SCRIPT_PATH = Path(__file__).resolve()
SERVICE_PATH = SCRIPT_PATH.parent
REPO_PATH = SCRIPT_PATH.parents[1]
README_FILE = REPO_PATH / "README.md"
OUTPUT_FILE = SERVICE_PATH / "readme_comment.md"

# 🔐 Token laden
load_dotenv(dotenv_path=SERVICE_PATH / ".env")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("❌ Kein GITHUB_TOKEN gefunden. Bitte in .env Datei setzen.")
    exit(1)

# RegEx für Markdown-Links
link_pattern = re.compile(r'\[(.*?)\]\((.*?)\)')

GITHUB_API_BASE = "https://api.github.com/repos"

def is_github_broken(url):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # --- A) blob/: Prüfung per API
    if "/blob/" in url:
        try:
            parts = url.split("github.com/")[1].split("/blob/")
            repo_path = parts[0]
            branch, path = parts[1].split("/", 1)
            api_url = f"{GITHUB_API_BASE}/{repo_path}/contents/{path}?ref={branch}"

            response = requests.get(api_url, headers=headers)
            print(f"🔍 API: {url} → {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):  # Datei
                    return False
                elif isinstance(data, list):  # Ordner
                    return len(data) == 0  # leer → broken
            elif response.status_code == 404:
                return True
        except Exception as e:
            print(f"⚠ Fehler bei API-Check {url}: {e}")
            return False

    # --- B) Andere GitHub-Links: HEAD-Check (wiki/, releases/, issues/, pull/)
    elif "github.com" in url and not "/blob/" in url:
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            print(f"🔍 HEAD: {url} → {response.status_code}")
            return response.status_code == 404
        except Exception as e:
            print(f"⚠ Fehler bei HEAD-Check {url}: {e}")
            return False

    return False

def mark_broken_links(line):
    def replace(match):
        text, url = match.groups()
        original = match.group(0)

        if "🔗✖" in original:
            return original

        if url.startswith("https://github.com") and is_github_broken(url):
            print(f"❌ Broken Link erkannt: {url}")
            return f"🔗✖ [{text}]({url})"

        return original

    return link_pattern.sub(replace, line)

def process_readme():
    with open(README_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = [mark_broken_links(line) for line in lines]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print(f"\n✅ Fertig! Datei mit Markierungen gespeichert unter:\n{OUTPUT_FILE}")

if __name__ == "__main__":
    print("🔐 Starte vollständige GitHub-Linkprüfung (API + HEAD)...\n")
    process_readme()

