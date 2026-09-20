"""
Redis-backed Interview Store

Each interview session is stored as a JSON string under the key:
    interview:{interview_id}

The key automatically expires after SESSION_TTL seconds (default 24 hours),
so old sessions are cleaned up without any manual work.

Pattern used everywhere:
    1. Read  → r.get(key) → json.loads
    2. Modify → change the dict in Python
    3. Write back → r.setex(key, TTL, json.dumps)
"""

import json
import uuid
from datetime import datetime
from typing import Optional

import redis

from app.config import REDIS_URL, SESSION_TTL


# One Redis connection shared across the whole app (thread-safe by default)
r = redis.from_url(REDIS_URL, decode_responses=True)


def _key(interview_id: str) -> str:
    """Return the Redis key for an interview session."""
    return f"interview:{interview_id}"


def _get(interview_id: str) -> Optional[dict]:
    """Read and deserialize an interview session from Redis. Returns None if not found."""
    raw = r.get(_key(interview_id))
    return json.loads(raw) if raw else None


def _save(interview: dict) -> None:
    """Serialize and write an interview session back to Redis, refreshing the TTL."""
    r.setex(_key(interview["interviewId"]), SESSION_TTL, json.dumps(interview))


# ─────────────────────────────────────────────────────────────────────────────
# Public API  (same method signatures as the old InterviewStore class)
# ─────────────────────────────────────────────────────────────────────────────

def create_interview(session_id: str, resume_file_name: str) -> dict:
    """Create a new interview session and store it in Redis."""
    interview_id = uuid.uuid4().hex
    interview = {
        "interviewId": interview_id,
        "sessionId": session_id,
        "resumeFileName": resume_file_name,
        "status": "in_progress",
        "totalQuestions": 0,
        "createdAt": datetime.utcnow().isoformat(),
        "questions": [],
        "report": None,
    }
    _save(interview)
    return interview


def get_interview(interview_id: str) -> Optional[dict]:
    """Retrieve a full interview session by ID."""
    return _get(interview_id)


def add_question(
    interview_id: str,
    question_text: str,
    category: str,
    difficulty: str,
    context_used: str,
) -> Optional[dict]:
    """Append a generated question to the interview and persist."""
    interview = _get(interview_id)
    if not interview:
        return None

    question_id = uuid.uuid4().hex
    order = interview["totalQuestions"] + 1

    question_item = {
        "questionId": question_id,
        "question": question_text,
        "category": category,
        "difficulty": difficulty,
        "contextUsed": context_used,
        "order": order,
        "answer": "",
        "evaluation": None,
    }

    interview["questions"].append(question_item)
    interview["totalQuestions"] = order
    _save(interview)

    return {
        "questionId": question_id,
        "question": question_text,
        "category": category,
        "difficulty": difficulty,
        "questionNumber": order,
        "contextUsed": context_used,
    }


def save_answer_and_evaluation(
    interview_id: str,
    question_id: str,
    answer: str,
    evaluation_data: dict,
) -> Optional[dict]:
    """Attach the candidate's answer and LLM evaluation to a question."""
    interview = _get(interview_id)
    if not interview:
        return None

    target_q = next((q for q in interview["questions"] if q["questionId"] == question_id), None)
    if not target_q:
        return None

    eval_record = {
        "evaluationId": uuid.uuid4().hex,
        "technicalScore": evaluation_data.get("technical_score", 0),
        "communicationScore": evaluation_data.get("communication_score", 0),
        "problemSolvingScore": evaluation_data.get("problem_solving_score", 0),
        "overallScore": evaluation_data.get("overall_score", 0),
        "strengths": evaluation_data.get("strengths", []),
        "weaknesses": evaluation_data.get("weaknesses", []),
        "feedback": evaluation_data.get("feedback", ""),
        "followUpSuggestion": evaluation_data.get("follow_up_suggestion", ""),
    }

    target_q["answer"] = answer
    target_q["evaluation"] = eval_record
    _save(interview)

    return eval_record


def save_report(interview_id: str, report_data: dict) -> Optional[dict]:
    """Save the final report and mark the interview as completed."""
    interview = _get(interview_id)
    if not interview:
        return None

    report_record = {
        "reportId": uuid.uuid4().hex,
        "overallScore": report_data.get("overall_score", 0),
        "technicalScore": report_data.get("technical_score", 0),
        "communicationScore": report_data.get("communication_score", 0),
        "problemSolvingScore": report_data.get("problem_solving_score", 0),
        "strongAreas": report_data.get("strong_areas", []),
        "weakAreas": report_data.get("weak_areas", []),
        "recommendedLearning": report_data.get("recommended_learning", []),
        "overallFeedback": report_data.get("overall_feedback", ""),
    }

    interview["report"] = report_record
    interview["status"] = "completed"
    _save(interview)

    return report_record


def get_interview_history(interview_id: str) -> list:
    """Return answered Q&A pairs formatted for the LLM question generator."""
    interview = _get(interview_id)
    if not interview:
        return []

    history = []
    for q in interview["questions"]:
        if q.get("answer"):
            ev = q.get("evaluation") or {}
            history.append({
                "question": q["question"],
                "answer": q["answer"],
                "category": q["category"],
                "evaluation": {
                    "overall_score": ev.get("overallScore", 0),
                    "technical_score": ev.get("technicalScore", 0),
                    "communication_score": ev.get("communicationScore", 0),
                    "problem_solving_score": ev.get("problemSolvingScore", 0),
                    "feedback": ev.get("feedback", ""),
                    "strengths": ev.get("strengths", []),
                    "weaknesses": ev.get("weaknesses", []),
                } if ev else {},
            })
    return history
