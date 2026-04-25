"""
LLM Explanation Layer using Generative AI.

Integrates with OpenRouter (LLaMA/GPT) to generate dynamic, human-readable
fraud explanations based on extracted feature contributions.
"""

import os
from openai import AsyncOpenAI
from utils.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize client only if API key is provided
try:
    if settings.LLM_API_KEY:
        client = AsyncOpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY,
        )
    else:
        client = None
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None


async def generate_llm_explanation(
    transaction_data: dict,
    risk_score: float,
    top_factors: list[tuple[str, float]],
    decision: str,
) -> str | None:
    """
    Call the LLM to generate a human-readable explanation for a fraud flag.

    Args:
        transaction_data: Raw input features.
        risk_score: The final fraud probability score (0.0 to 1.0).
        top_factors: Top contributing features as (display_name, contribution_amount).
        decision: Final system decision (e.g., ESCALATE, BLOCK, REVIEW).

    Returns:
        A concise 2-3 sentence string explanation, or None if the API fails
        or is not configured.
    """
    if not client:
        return None

    model = settings.LLM_MODEL
    
    # Format the top factors into a readable string
    factors_str = "\n".join([f"- {f[0]} (Impact: {f[1]:.4f})" for f in top_factors])
    
    # Construct the prompt
    system_prompt = (
        "You are an expert fraud analyst working for a major bank. "
        "Your task is to concisely explain to a human reviewer why a specific transaction was flagged by our machine learning models. "
        "Do NOT mention 'machine learning', 'impact scores', or 'coefficients'. Speak purely in terms of business risk. "
        "Keep the explanation strictly to 2-3 short, highly professional sentences."
    )
    
    user_prompt = f"""
    A transaction was just flagged.
    
    Context:
    - Fraud Probability Score: {risk_score:.1%}
    - System Decision: {decision}
    - Transaction Amount: ${transaction_data.get('amount', 0):.2f}
    - Distance from Home: {transaction_data.get('location_distance_km', 0):.1f} km
    - Transactions in Last 1H: {transaction_data.get('velocity_last_1h', 0)}
    
    Top Statistical Risk Factors Identified:
    {factors_str}
    
    Write the explanation now.
    """

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=150,
            # OpenRouter-specific header for app tracking
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "FraudDetectionEngine",
            }
        )
        
        explanation = response.choices[0].message.content.strip()
        logger.info("Successfully generated LLM explanation.")
        return explanation

    except Exception as e:
        logger.error(f"LLM API Call failed: {e}")
        return None
