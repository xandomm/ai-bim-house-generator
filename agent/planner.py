"""
Planner: converts natural language prompts into HousePlan schemas.

MVP: Uses a mock parser that returns default values.
TODO: Replace with real LLM integration (Gemini/OpenAI) for production.
"""

from models.schema import HousePlan


def parse_prompt(prompt: str) -> HousePlan:
    """Parse a natural language prompt into a structured HousePlan.

    Args:
        prompt: User's natural language description of the house.

    Returns:
        HousePlan with extracted or default parameters.

    Examples:
        >>> parse_prompt("casa de 12x8 metros")
        HousePlan(width=12.0, depth=8.0, ...)

        >>> parse_prompt("casa moderna com telhado")
        HousePlan(width=10.0, depth=10.0, with_roof=True, ...)
    """
    # MVP: return sensible defaults
    # TODO: integrate with LLM to extract dimensions, roof preference, etc.
    plan = HousePlan(
        width=10.0,
        depth=10.0,
        wall_height=3.0,
        wall_thickness=0.2,
        with_roof=False,
        ridge_height=2.0,
        output_path="house.ifc",
    )

    # Simple keyword detection (placeholder logic)
    prompt_lower = prompt.lower()

    if "telhado" in prompt_lower or "roof" in prompt_lower:
        plan.with_roof = True

    # You can add more heuristics here or replace with LLM call
    # Example with OpenAI:
    # response = openai.ChatCompletion.create(...)
    # plan = HousePlan(**extract_from_llm_response(response))

    return plan


def parse_prompt_with_gemini(prompt: str, api_key: str) -> HousePlan:
    """Parse a prompt using Google Gemini (placeholder for future implementation).

    Args:
        prompt: User's natural language description.
        api_key: Google API key for Gemini.

    Returns:
        HousePlan with extracted parameters.
    """
    # TODO: Implement Gemini integration
    # from langchain_google_genai import ChatGoogleGenerativeAI
    # llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=api_key)
    # response = llm.invoke(f"Extract house parameters from: {prompt}")
    # return HousePlan(**parse_llm_json(response))

    raise NotImplementedError("Gemini integration not yet implemented. Use parse_prompt() for MVP.")
