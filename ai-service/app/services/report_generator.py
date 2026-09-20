import logging
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.schemas import ReportAnalysis, FinalReport

logger = logging.getLogger(__name__)

REPORT_PROMPT = """You are an expert interview performance analyst.
Based on the interview evaluation data below, provide a written analysis.

DO NOT calculate or return any scores — the scores are already computed.
Your job is ONLY to write:
1. strong_areas — specific topics/skills where the candidate did well
2. weak_areas — specific topics/skills where the candidate struggled
3. recommended_learning — actionable topics to study for improvement
4. overall_feedback — a 3-5 sentence honest and encouraging narrative summary

INTERVIEW DATA:
{evaluations_text}"""


def generate_report(evaluations: list[dict]) -> FinalReport:
    n = len(evaluations)

    # Compute all scores in Python — never let the LLM do math
    def avg100(key):
        return round(sum(e.get(key, 0) for e in evaluations) / n * 10)

    overall_score = avg100("overall_score")
    technical_score = avg100("technical_score")
    communication_score = avg100("communication_score")
    problem_solving_score = avg100("problem_solving_score")

    # Format evaluations for the LLM (text-only analysis)
    evaluations_text = ""
    for i, e in enumerate(evaluations, 1):
        evaluations_text += (
            f"\n--- Question {i} ({e.get('category', 'General')}) ---\n"
            f"Question: {e.get('question', '')}\n"
            f"Answer: {e.get('answer', '')}\n"
            f"Scores: Technical {e.get('technical_score')}/10, "
            f"Communication {e.get('communication_score')}/10, "
            f"Problem Solving {e.get('problem_solving_score')}/10\n"
            f"Strengths: {', '.join(e.get('strengths', []))}\n"
            f"Weaknesses: {', '.join(e.get('weaknesses', []))}\n"
            f"Feedback: {e.get('feedback', '')}\n"
        )

    # LLM only writes the text analysis — not scores
    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.4)
    structured_llm = llm.with_structured_output(ReportAnalysis)

    prompt = ChatPromptTemplate.from_messages([
        ("system", REPORT_PROMPT),
        ("human", "Generate the written analysis for this interview.")
    ])

    analysis = (prompt | structured_llm).invoke({"evaluations_text": evaluations_text})

    logger.info(
        f"Report generated — Overall: {overall_score}/100, "
        f"Technical: {technical_score}/100, Communication: {communication_score}/100, "
        f"Problem Solving: {problem_solving_score}/100"
    )

    # Merge computed scores + LLM text into final report
    return FinalReport(
        overall_score=overall_score,
        technical_score=technical_score,
        communication_score=communication_score,
        problem_solving_score=problem_solving_score,
        strong_areas=analysis.strong_areas,
        weak_areas=analysis.weak_areas,
        recommended_learning=analysis.recommended_learning,
        overall_feedback=analysis.overall_feedback,
    )
