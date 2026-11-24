from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI


class JobLead(BaseModel):
    is_job_lead: bool = Field(description="True if the email contains a job lead, recruiter message, interview, application update, or career opportunity.")
    company: str = ""
    position: str = ""
    location: str = ""
    pay_range: str = ""
    source: str = ""
    status: Literal["New Lead", "Review", "Applied", "Interview", "Suspicious", "Ignore"] = "Review"
    priority: Literal["High", "Medium", "Low"] = "Medium"
    fit_score: int = Field(default=50, ge=0, le=100)
    reason: str = ""
    next_action: str = ""


SYSTEM_PROMPT = """
You extract job-search leads for Dallas Manning.
Dallas is strongest in plant management, operations leadership, energy, nuclear engineering, quality systems, manufacturing, water treatment, automotive suppliers, EMS/SCADA, and AI/data-adjacent infrastructure.
Flag suspicious emails when sender domains, grammar, or claims look unreliable.
Return one clean structured record.
"""


def build_model(model_name: str = "gpt-4o-mini"):
    llm = ChatOpenAI(model=model_name, temperature=0)
    return llm.with_structured_output(JobLead)


def extract_job_lead(email: dict, model=None) -> JobLead:
    model = model or build_model()
    content = f"""
From: {email.get('from')}
Subject: {email.get('subject')}
Date: {email.get('date')}
Snippet: {email.get('snippet')}
Body:
{email.get('body')}
"""
    return model.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": content},
    ])
