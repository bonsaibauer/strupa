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
README_FILE = REPO_PATH / "README.md"
CHANGELOG_MARKER = "<!-- CHANGELOG START -->"

# 📦 Releases von GitHub abrufen
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

# 📄 Gemeinsame Formatierfunktion
def format_entry(release):
    tag = release.get("tag_name", "N/A")
    name = release.get("name", tag)
    date = release.get("published_at", "unbekannt")[:10]
    body = release.get("body", "").strip() or "*Keine Beschreibung vorhanden.*"
    return f"## [{name}] - {date}\n{body}\n"

# 🔹 CHANGELOG.md – alles offen
def generate_changelog_full(releases):
    header = """# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

"""
    entries = [format_entry(r) for r in releases]
    return header + "\n".join(entries)

# 🔸 README.md – neuester sichtbar, Rest einklappen
def generate_changelog_collapsed(releases):
    if not releases:
        return "*Kein Changelog verfügbar.*"

    latest = format_entry(releases[0])
    older = [format_entry(r) for r in releases[1:]]

    collapsible = ""
    if older:
        collapsible = (
            "<details>\n"
            "<summary>📜 Ältere Einträge anzeigen</summary>\n\n"
            + "\n".join(older)
            + "\n</details>\n"
        )

    return latest + "\n" + collapsible

# 📘 README aktualisieren
def update_readme_with_changelog(changelog_section):
    if not README_FILE.exists():
        print("⚠️ README.md nicht gefunden.")
        return

    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if CHANGELOG_MARKER in content:
        content = content.split(CHANGELOG_MARKER)[0].rstrip()

    new_readme = content + f"\n\n{CHANGELOG_MARKER}\n\n" + changelog_section

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_readme)

    print(f"✅ README.md aktualisiert mit kompaktem Changelog.")

# ▶️ Hauptfunktion
def main():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("❌ GITHUB_TOKEN oder GITHUB_REPO fehlt in .env.")
        return

    releases = fetch_all_releases(GITHUB_REPO, GITHUB_TOKEN)
    if not releases:
        print("ℹ️ Keine Releases gefunden.")
        return

    # 🔧 Generiere vollständigen Changelog
    changelog_content_full = generate_changelog_full(releases)
    with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
        f.write(changelog_content_full)
    print(f"✅ CHANGELOG.md erfolgreich generiert unter: {CHANGELOG_FILE}")

    # 🔧 Kompakte Version für README
    changelog_for_readme = generate_changelog_collapsed(releases)
    update_readme_with_changelog(changelog_for_readme)

if __name__ == "__main__":
    main()
