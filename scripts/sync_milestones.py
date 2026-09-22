import os
import subprocess
from collections import defaultdict
import requests
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# 1. Initialize Clients & Load Environment Variables
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_VERSION = "2022-06-28"

def get_push_commits():
    """Extracts commits included in the current GitHub push, grouped by date."""
    before = os.getenv("GITHUB_EVENT_BEFORE")
    after = os.getenv("GITHUB_EVENT_AFTER", "HEAD")
    sync_all_history = os.getenv("SYNC_ALL_HISTORY") == "true"
    command = ["git", "log", "--date=short", "--format=%ad%x1f%h%x1f%s"]

    if sync_all_history:
        command.append(after)
    elif before and before != "0" * 40:
        command.append(f"{before}..{after}")
    else:
        command.append(after)

    result = subprocess.run(
        command,
        capture_output=True, 
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    commits_by_date = defaultdict(list)
    for line in result.stdout.splitlines():
        commit_date, commit_sha, subject = line.split("\x1f", maxsplit=2)
        commits_by_date[commit_date].append(f"{commit_sha} {subject}")
    return commits_by_date

def generate_architectural_breakdown(commit_date, commit_log):
    """Passes code history to Gemini to extract structured How and Why context."""
    prompt = f"""
    You are an expert backend systems architect and tech writer. Analyze these code commits 
    and generate a detailed engineering milestone document.
    
    You must structure your response strictly using these tags:
    TITLE: [Catchy title with Day number]
    CATEGORY: [Backend Architecture / Database / Security]
    SUMMARY: [Concise paragraph of what was built]
    HOW: [Step-by-step technical implementation details of how it was built]
    WHY: [The core architectural reason and system design trade-offs of why this pattern was chosen]
    
    Date:
    {commit_date}

    Commits:
    {commit_log}
    """
    
    # Initialize a clean chat session to prevent Automatic Function Calling issues
    chat = client.chats.create(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(temperature=0.2)
    )
    
    response = chat.send_message(prompt)
    return response.text


def parse_ai_output(ai_text):
    """Parses the Gemini structured text into a clean Python dictionary."""
    data = {}
    current_key = None
    for line in ai_text.split("\n"):
        if line.startswith("TITLE:"):
            current_key = "title"
            data[current_key] = line.replace("TITLE:", "").strip()
        elif line.startswith("CATEGORY:"):
            current_key = "category"
            data[current_key] = line.replace("CATEGORY:", "").strip()
        elif line.startswith("SUMMARY:"):
            current_key = "summary"
            data[current_key] = line.replace("SUMMARY:", "").strip()
        elif line.startswith("HOW:"):
            current_key = "how"
            data[current_key] = line.replace("HOW:", "").strip()
        elif line.startswith("WHY:"):
            current_key = "why"
            data[current_key] = line.replace("WHY:", "").strip()
        elif current_key and line.strip():
            data[current_key] += " " + line.strip()
    return data

def notion_headers():
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }

def find_page_by_key(milestone_key):
    """Finds an existing page so workflow retries are idempotent."""
    response = requests.post(
        f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
        headers=notion_headers(),
        json={
            "filter": {
                "property": "Milestone Key",
                "rich_text": {"equals": milestone_key}
            }
        },
        timeout=30
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    return results[0]["id"] if results else None

def push_to_notion(parsed_data, commit_date):
    """Sends the structured engineering payload to your Notion Database API."""
    url = "https://api.notion.com/v1/pages"
    
    milestone_key = f"{os.getenv('GITHUB_REPOSITORY', 'local')}:{commit_date}"
    
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": parsed_data.get("title", "Engineering Milestone")}}]
            },
            "Category": {
                "select": {"name": parsed_data.get("category", "Backend Architecture")}
            },
            "Summary": {
                "rich_text": [{"text": {"content": parsed_data.get("summary", "")}}]
            },
            "How": {
                "rich_text": [{"text": {"content": parsed_data.get("how", "")}}]
            },
            "Why": {
                "rich_text": [{"text": {"content": parsed_data.get("why", "")}}]
            },
            "Date": {
                "date": {"start": commit_date}
            },
            "Milestone Key": {
                "rich_text": [{"text": {"content": milestone_key}}]
            }
        }
    }

    page_id = find_page_by_key(milestone_key)
    if page_id:
        response = requests.patch(
            f"https://api.notion.com/v1/pages/{page_id}",
            json={"properties": payload["properties"]},
            headers=notion_headers(),
            timeout=30
        )
        action = "Updated"
    else:
        response = requests.post(url, json=payload, headers=notion_headers(), timeout=30)
        action = "Created"

    response.raise_for_status()
    print(f"{action} Notion milestone for {commit_date}: {parsed_data.get('title')}")

if __name__ == "__main__":
    if not NOTION_TOKEN or not DATABASE_ID or not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY, NOTION_TOKEN, and NOTION_DATABASE_ID are required")

    print("Reading commits included in the GitHub push...")
    commits_by_date = get_push_commits()
    for commit_date, commits in sorted(commits_by_date.items()):
        print(f"Generating architectural breakdown for {commit_date}...")
        raw_ai_text = generate_architectural_breakdown(commit_date, "\n".join(commits))
        parsed_data = parse_ai_output(raw_ai_text)
        if not parsed_data.get("title"):
            raise RuntimeError(f"Failed to parse milestone data for {commit_date}")
        push_to_notion(parsed_data, commit_date)