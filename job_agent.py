from __future__ import annotations

from config import GMAIL_QUERY, MAX_EMAILS, TRACKER_PATH
from gmail_reader import search_job_emails
from extractor import build_model, extract_job_lead
from excel_tracker import append_leads


def main():
    print(f"Searching Gmail with query: {GMAIL_QUERY}")
    emails = search_job_emails(GMAIL_QUERY, MAX_EMAILS)
    print(f"Found {len(emails)} candidate emails.")

    model = build_model()
    rows = []

    for email in emails:
        lead = extract_job_lead(email, model=model)
        if not lead.is_job_lead:
            continue

        rows.append(
            {
                "Date": email.get("date"),
                "Company": lead.company,
                "Position": lead.position,
                "Location": lead.location,
                "Pay Range": lead.pay_range,
                "Source": lead.source or email.get("from"),
                "Status": lead.status,
                "Priority": lead.priority,
                "Fit Score": lead.fit_score,
                "Next Action": lead.next_action,
                "Notes": lead.reason,
                "Gmail URL": email.get("gmail_url"),
                "Message ID": email.get("message_id"),
            }
        )
        print(f"Lead: {lead.company} | {lead.position} | {lead.priority} | {lead.fit_score}")

    added = append_leads(TRACKER_PATH, rows)
    print(f"Added {added} new rows to {TRACKER_PATH}")


if __name__ == "__main__":
    main()
