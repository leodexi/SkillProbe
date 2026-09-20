import os
import tempfile
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas import SubmitAnswerRequest
from app import store
from app.services.resume_processor import process_resume
from app.services.question_generator import generate_question
from app.services.answer_evaluator import evaluate_answer
from app.services.report_generator import generate_report

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/interviews", tags=["Interviews"])


@router.post("/upload")
async def upload_resume(resume: UploadFile = File(...)):
    """Upload and process a resume PDF, starting a new interview session."""
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await resume.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Process PDF and store chunks in ChromaDB
        result = process_resume(tmp_path)
        session_id = result["session_id"]
        num_chunks = result["num_chunks"]

        # Create session in memory store
        interview = store.create_interview(
            session_id=session_id,
            resume_file_name=resume.filename
        )

        return {
            "interviewId": interview["interviewId"],
            "sessionId": session_id,
            "resumeFileName": resume.filename,
            "numChunks": num_chunks,
            "message": "Resume processed successfully"
        }

    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/{interview_id}")
async def get_interview(interview_id: str):
    """Get the current interview state."""
    interview = store.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return interview


@router.post("/{interview_id}/question")
async def get_next_question(interview_id: str):
    """Generate next question grounded in resume and previous history."""
    interview = store.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    session_id = interview["sessionId"]
    history = store.get_interview_history(interview_id)

    try:
        q = generate_question(session_id=session_id, interview_history=history)

        question_data = store.add_question(
            interview_id=interview_id,
            question_text=q.question,
            category=q.category,
            difficulty=q.difficulty,
            context_used=q.context_used
        )

        return question_data
    except Exception as e:
        logger.error(f"Question generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {str(e)}")


@router.post("/{interview_id}/answer")
async def submit_answer(interview_id: str, request: SubmitAnswerRequest):
    """Submit candidate's answer and get structured evaluation."""
    if not request.answer or not request.answer.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty.")

    interview = store.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    target_q = next((q for q in interview["questions"] if q["questionId"] == request.questionId), None)
    if not target_q:
        raise HTTPException(status_code=404, detail="Question not found.")

    try:
        eval_result = evaluate_answer(
            session_id=interview["sessionId"],
            question=target_q["question"],
            answer=request.answer.strip(),
            category=target_q.get("category", ""),
            context_used=target_q.get("contextUsed", "")
        )

        eval_record = store.save_answer_and_evaluation(
            interview_id=interview_id,
            question_id=request.questionId,
            answer=request.answer.strip(),
            evaluation_data=eval_result.model_dump()
        )

        return eval_record
    except Exception as e:
        logger.error(f"Answer evaluation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to evaluate answer: {str(e)}")


@router.post("/{interview_id}/report")
async def generate_report_for_interview(interview_id: str):
    """Generate comprehensive final report summarizing the entire interview."""
    interview = store.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    if interview.get("report"):
        return interview["report"]

    evaluations = []
    for q in interview["questions"]:
        if q.get("evaluation"):
            ev = q["evaluation"]
            evaluations.append({
                "question": q["question"],
                "answer": q["answer"],
                "category": q["category"],
                "technical_score": ev["technicalScore"],
                "communication_score": ev["communicationScore"],
                "problem_solving_score": ev["problemSolvingScore"],
                "overall_score": ev["overallScore"],
                "strengths": ev["strengths"],
                "weaknesses": ev["weaknesses"],
                "feedback": ev["feedback"]
            })

    if not evaluations:
        raise HTTPException(status_code=400, detail="Answer at least one question before generating report.")

    try:
        report_result = generate_report(evaluations=evaluations)
        report_record = store.save_report(interview_id, report_result.model_dump())
        return report_record
    except Exception as e:
        logger.error(f"Report generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
