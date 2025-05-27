#!/usr/bin/env python3
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# 🔐 Umgebungsvariablen laden
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")  # Format: owner/repo

# 📍 Pfade
SCRIPT_PATH = Path(__file__).resolve()
REPO_PATH = SCRIPT_PATH.parents[1]
CHANGELOG_FILE = REPO_PATH / "CHANGELOG.md"

# 📦 Alle Releases von GitHub abrufen
def fetch_all_releases(repo, token):
    url = f"https://api.github.com/repos/{repo}/releases"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Fehler beim Abrufen der Releases: {response.status_code}")
            return []
        return response.json()
    except Exception as e:
        print(f"⚠️ Ausnahme beim Abrufen der Releases: {e}")
        return []

# 📄 CHANGELOG generieren
def generate_changelog(releases):
    header = """# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

"""

    entries = []
    for release in releases:
        tag = release.get("tag_name", "N/A")
        name = release.get("name", tag)
        date = release.get("published_at", "unbekannt")[:10]
        body = release.get("body", "").strip() or "*Keine Beschreibung vorhanden.*"

        entry = f"## [{name}] - {date}\n{body}\n"
        entries.append(entry)

    return header + "\n".join(entries)

# 🧠 Hauptfunktion
def main():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("❌ GITHUB_TOKEN oder GITHUB_REPO fehlt in .env.")
        return

    releases = fetch_all_releases(GITHUB_REPO, GITHUB_TOKEN)
    if not releases:
        print("ℹ️ Keine Releases gefunden.")
        return

    changelog_content = generate_changelog(releases)

    with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
        f.write(changelog_content)

    print(f"✅ CHANGELOG.md erfolgreich generiert unter: {CHANGELOG_FILE}")

if __name__ == "__main__":
    main()
