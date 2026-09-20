"""
Answer Evaluator Service (LLM 2)

Evaluates candidate answers using a structured rubric.

Key design decisions:
- Uses a detailed scoring rubric (not arbitrary "give a score out of 10")
- Receives resume context so the evaluator can check factual accuracy
  against what the candidate actually worked on
- Uses with_structured_output(AnswerEvaluation) for guaranteed schema
- Suggests follow-up questions for weak answers (enables adaptive interviewing)
"""
import logging
# pyrefly: ignore [missing-import]
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.schemas import AnswerEvaluation
from app.services.resume_processor import retrieve_context

logger = logging.getLogger(__name__)

EVALUATOR_PROMPT = """You are an expert interview evaluator. Evaluate the candidate's answer 
using the following structured rubric.

═══════════════════════════════════════════════════════════
SCORING RUBRIC
═══════════════════════════════════════════════════════════

TECHNICAL ACCURACY (0-10):
  0-2 → Incorrect or completely irrelevant answer
  3-4 → Major conceptual gaps or significant errors
  5-6 → Basic understanding but missing important details
  7-8 → Good understanding with minor gaps
  9-10 → Excellent, comprehensive, and accurate

COMMUNICATION (0-10):
  0-2 → Very unclear, incoherent response
  3-4 → Difficult to follow, poorly structured
  5-6 → Understandable but could be clearer
  7-8 → Clear and well-structured explanation
  9-10 → Excellent clarity, great use of examples

PROBLEM SOLVING (0-10):
  0-2 → No logical approach demonstrated
  3-4 → Weak approach, doesn't address the core problem
  5-6 → Basic approach but misses edge cases
  7-8 → Good systematic approach with consideration of trade-offs
  9-10 → Excellent approach with thorough analysis

═══════════════════════════════════════════════════════════

RESUME CONTEXT (for factual verification):
{resume_context}

INTERVIEW QUESTION:
{question}

CANDIDATE'S ANSWER:
{answer}

Evaluate the answer strictly according to the rubric above. Be fair but thorough.
Identify specific strengths and weaknesses. Provide constructive feedback that 
helps the candidate improve. If the overall score is 5 or below, suggest a 
follow-up question that probes the same topic from a simpler angle."""


def evaluate_answer(
    session_id: str,
    question: str,
    answer: str,
    category: str = "",
    context_used: str = ""
) -> AnswerEvaluation:
    
    # Retrieve relevant resume context for fact-checking the answer
    search_query = f"{category} {question}" if category else question
    resume_context = retrieve_context(session_id, search_query, k=3)

    # If we have the original context used for the question, append it
    if context_used:
        resume_context = f"{context_used}\n\n---\n\n{resume_context}"

    # Build the evaluation chain with structured output
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.3  # Lower temperature for more consistent evaluation
    )
    structured_llm = llm.with_structured_output(AnswerEvaluation)

    prompt = ChatPromptTemplate.from_messages([
        ("system", EVALUATOR_PROMPT),
        ("human", "Evaluate this answer according to the rubric.")
    ])

    chain = prompt | structured_llm

    result = chain.invoke({
        "resume_context": resume_context,
        "question": question,
        "answer": answer
    })

    logger.info(
        f"Evaluation complete - Technical: {result.technical_score}, "
        f"Communication: {result.communication_score}, "
        f"Problem Solving: {result.problem_solving_score}, "
        f"Overall: {result.overall_score}"
    )

    return result
