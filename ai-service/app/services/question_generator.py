"""
Question Generator Service (LLM 1)

Generates interview questions grounded in the candidate's resume using RAG.

Key design decisions:
- Uses retriever to fetch relevant resume chunks before generating questions
- Supports adaptive questioning: if previous answer was weak (score <= 5),
  generates a follow-up on the same topic
- Explicitly instructs the LLM to ONLY use information from the resume context
  (RAG grounding — prevents hallucination)
- Uses with_structured_output(InterviewQuestion) for guaranteed schema compliance
"""
import logging
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.schemas import InterviewQuestion
from app.services.resume_processor import retrieve_context

logger = logging.getLogger(__name__)

# System prompt for the question generator
QUESTION_GENERATOR_PROMPT = """You are an expert technical interviewer. Your job is to generate 
insightful, personalized interview questions based on the candidate's resume.

CRITICAL RULES:
1. Generate questions ONLY from information supported by the provided resume context.
2. Do NOT assume technologies, experience, or skills that are not explicitly mentioned in the resume.
3. Make questions specific to the candidate's actual projects and experience.
4. Vary the difficulty and category across questions.
5. If interview history is provided, avoid repeating topics already covered.
6. The 'difficulty' field MUST strictly be one of: 'easy', 'medium', or 'hard'. Do not put conversational intro text into 'difficulty'.

RESUME CONTEXT:
{resume_context}

INTERVIEW HISTORY (previous questions, answers, and evaluations):
{interview_history}

ADAPTIVE INSTRUCTIONS:
{adaptive_instructions}

Generate the next interview question. Make it specific and grounded in the resume.
The category should be dynamically determined based on what you find in the resume 
(e.g., a specific technology, project name, concept, or skill area)."""

FIRST_QUESTION_INSTRUCTIONS = """This is the first question of the interview. 
Start with a question about one of the candidate's projects or most prominent skills. 
Choose something that will open up a broad discussion."""

FOLLOW_UP_INSTRUCTIONS = """The candidate's previous answer was weak (scored {score}/10). 
Generate a follow-up question on the SAME topic to probe deeper or approach it from a 
simpler angle. The previous question was about: {previous_category}
Previous question: {previous_question}"""

NEXT_TOPIC_INSTRUCTIONS = """The candidate answered the previous question well. 
Move to a DIFFERENT topic area from the resume that hasn't been covered yet.
Previously covered categories: {covered_categories}"""


def generate_question(session_id: str, interview_history: list[dict] = None) -> InterviewQuestion:
    """
    Generate the next interview question using RAG + Ollama.

    Args:
        session_id: Resume session ID for ChromaDB retrieval
        interview_history: List of previous Q&A dicts with evaluations

    Returns:
        InterviewQuestion with question, category, difficulty, and context_used
    """
    if interview_history is None:
        interview_history = []

    # Determine adaptive instructions based on history
    if not interview_history:
        adaptive_instructions = FIRST_QUESTION_INSTRUCTIONS
        search_query = "skills projects experience education technologies"
    else:
        last_entry = interview_history[-1]
        last_eval = last_entry.get("evaluation", {})
        last_score = last_eval.get("overall_score", 10)

        if last_score <= 5:
            # Weak answer -> follow up on the same topic
            adaptive_instructions = FOLLOW_UP_INSTRUCTIONS.format(
                score=last_score,
                previous_category=last_entry.get("category", "unknown"),
                previous_question=last_entry.get("question", "")
            )
            search_query = last_entry.get("category", "skills")
        else:
            # Strong answer -> move to a new topic
            covered = [entry.get("category", "") for entry in interview_history]
            adaptive_instructions = NEXT_TOPIC_INSTRUCTIONS.format(
                covered_categories=", ".join(covered)
            )
            # Search for something new
            search_query = f"skills projects experience NOT {' NOT '.join(covered)}"

    # RAG: Retrieve relevant resume context
    resume_context = retrieve_context(session_id, search_query, k=4)

    # Format interview history for the prompt
    history_text = ""
    if interview_history:
        for i, entry in enumerate(interview_history, 1):
            eval_data = entry.get("evaluation", {})
            history_text += f"\n--- Question {i} ---\n"
            history_text += f"Category: {entry.get('category', 'N/A')}\n"
            history_text += f"Q: {entry.get('question', 'N/A')}\n"
            history_text += f"A: {entry.get('answer', 'N/A')}\n"
            history_text += f"Score: {eval_data.get('overall_score', 'N/A')}/10\n"
            history_text += f"Feedback: {eval_data.get('feedback', 'N/A')}\n"
    else:
        history_text = "No previous questions — this is the first question."

    # Build the chain with structured output
    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.7
    )
    structured_llm = llm.with_structured_output(InterviewQuestion)

    prompt = ChatPromptTemplate.from_messages([
        ("system", QUESTION_GENERATOR_PROMPT),
        ("human", "Generate the next interview question.")
    ])

    chain = prompt | structured_llm

    result = chain.invoke({
        "resume_context": resume_context,
        "interview_history": history_text,
        "adaptive_instructions": adaptive_instructions
    })

    logger.info(f"Generated question - Category: {result.category}, Difficulty: {result.difficulty}")
    return result
