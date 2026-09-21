import os
import subprocess
import requests
from google import genai
from google.genai import types

# 1. Initialize Clients & Load Environment Variables
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def get_recent_git_commits():
    """Extracts recent commit logs to analyze what was built."""
    result = subprocess.run(
        ["git", "log", "--oneline", "-n", "5"], 
        capture_output=True, 
        text=True
    )
    return result.stdout

def generate_architectural_breakdown(commit_log):
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
    
    Commits:
    {commit_log}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.2)
    )
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

def push_to_notion(parsed_data):
    """Sends the structured engineering payload to your Notion Database API."""
    url = "https://api.notion.com/v1/pages"
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
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
            }
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Successfully synced '{parsed_data.get('title')}' to Notion!")
    else:
        print(f"Failed to sync: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Reading Git commit history...")
    commits = get_recent_git_commits()
    
    print("Generating architectural breakdown via Gemini...")
    raw_ai_text = generate_architectural_breakdown(commits)
    
    parsed_data = parse_ai_output(raw_ai_text)
    print("Parsed Milestone Data:\n", parsed_data)
    
    # Executes the live push to Notion
    if parsed_data.get("title"):
        push_to_notion(parsed_data)
    else:
        print("Error: Failed to parse valid milestone data from AI output.")