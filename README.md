# Day 1: The Request-Response Lifecycle & Automated Validation

## 🎯 What I Learned Today
- **The Problem:** Relying solely on frontend validation is a systemic trap; malformed data (like negative prices or incorrect data types) can crash backend calculations or corrupt databases.
- **The Solution:** Using FastAPI and **Pydantic** models to intercept incoming HTTP request bodies and validate them automatically during object initialization.
- **Key Takeaway:** If a validation rule fails (e.g., negative stock quantity or missing required fields), Pydantic short-circuits execution instantly and returns a standardized **422 Unprocessable Entity** response before hitting any business logic.

## Automatic Notion Milestones

Milestone documentation is generated locally after each commit. The hook sends the
commit summary to Ollama, then syncs the generated document to the Notion database.

### One-time setup

1. Install Ollama from https://ollama.com/download.
2. Start Ollama and download the model:

	```bash
	ollama pull llama3.2
	```

3. Ensure `.env` contains:

	```text
	NOTION_TOKEN=your_notion_integration_token
	NOTION_DATABASE_ID=your_notion_database_id
	```

4. Install the hook:

	```bash
	python scripts/install_post_commit_hook.py
	```

After setup, each local `git commit` generates or updates the Notion page for that
day. The Notion database needs `Name`, `Category`, `Summary`, `How`, `Why`, `Date`,
and `Milestone Key` properties.