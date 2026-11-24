# LangChain Gmail Job Agent

An AI agent that turns a cluttered job-search inbox into a clean, prioritized tracker. It reads recent recruiter and job emails through the Gmail API, uses an OpenAI model with LangChain structured output to pull out the key facts, scores each lead, and writes it to an Excel tracker.

## Why it's useful

- **Structured extraction:** every email becomes one typed record (company, role, location, pay, status, priority, 0-100 fit score, next action), validated with Pydantic.
- **Scam screening:** the model is told to mark leads as *Suspicious* when sender domains, grammar or claims look unreliable.
- **No duplicates:** rows are keyed on the Gmail message ID, so re-running is safe.
- **Read-only by design:** uses the `gmail.readonly` scope. It never sends, deletes or changes email.

## Pipeline

```text
Gmail API search -> email text -> LangChain + OpenAI (structured output) -> JobLead record -> Excel tracker
```

## Tech

Python, LangChain, OpenAI (gpt-4o-mini), Pydantic, Gmail API (OAuth), openpyxl.

---

## Version 1 details
This version reads recent Gmail job-related emails, uses LangChain + OpenAI to extract job leads, scores the fit for Dallas Manning, and appends clean records into an Excel job tracker.

## What it does

- Searches Gmail for job/recruiter/career emails
- Reads subject, sender, snippet, and body text
- Uses LangChain structured output to extract:
  - company
  - position
  - location
  - pay range
  - source
  - status
  - priority
  - fit score
  - next action
  - notes
- Updates an Excel tracker
- Avoids duplicate rows using Gmail Message ID

## What it does NOT do yet

- It does not send email replies
- It does not delete emails
- It does not mark emails as spam
- It does not apply to jobs automatically

Those can be added later after the read-only version works correctly.

## Folder setup

Put these files in one folder:

```text
langchain_gmail_job_agent/
  job_agent.py
  gmail_reader.py
  extractor.py
  excel_tracker.py
  config.py
  requirements.txt
  .env.example
  credentials.json
  job_search_tracker_UPDATED.xlsx
```

## Step 1 — Create virtual environment

From PowerShell inside the project folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Step 2 — Set your OpenAI key

Copy `.env.example` to `.env`.

Edit `.env`:

```text
OPENAI_API_KEY=your_real_key_here
GMAIL_QUERY=(job OR jobs OR career OR careers OR hiring OR recruiter OR opportunity OR application OR interview OR position) newer_than:2d
TRACKER_PATH=job_search_tracker_UPDATED.xlsx
MAX_EMAILS=25
```

## Step 3 — Set up Gmail API

1. Go to Google Cloud Console.
2. Create or select a project.
3. Enable Gmail API.
4. Configure OAuth consent screen.
5. Create OAuth Client ID.
6. Choose Desktop App.
7. Download the file.
8. Rename it to `credentials.json`.
9. Place it in this project folder.

The first run opens a browser login window. After approval, the script creates `token.json` so you do not need to log in every run.

## Step 4 — Run it

```powershell
python job_agent.py
```

Expected output:

```text
Searching Gmail with query: ...
Found 10 candidate emails.
Lead: Ford Motor Company | Multiple Opportunities | High | 88
Lead: Lear Corporation | Senior Quality Engineer | High | 84
Added 2 new rows to job_search_tracker_UPDATED.xlsx
```

## Recommended first test

Use this query first so it only reads recent leads:

```text
newer_than:2d (Ford OR Lear OR Indeed OR Monster OR SimplyHired OR Google Jobs OR recruiter OR hiring)
```

## Upgrade path

Version 2:
- Add spam/suspicious sender scoring
- Add label management
- Add daily summary report

Version 3:
- Draft replies in Dallas's voice
- Add resume-match scoring
- Add job description scraper

Version 4:
- Add calendar/interview handling
- Add dashboard

## Author

Dallas E. Manning
