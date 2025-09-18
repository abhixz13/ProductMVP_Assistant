from pydantic import BaseModel, Field
from agents import Agent, Runner, function_tool
from typing import List, Dict, Optional
import asyncio

# Template definitions for product analysis frameworks
TEMPLATE_FRAMEWORKS = {
    "product_feature_analysis": {
        "name": "Product Feature Analysis",
        "thinking_categories": ["user_value", "market_opportunity", "technical_feasibility", "business_impact", "competitive_landscape"],
        "question_templates": {
            "user_value": "What specific user problem does this {topic} feature solve and how critical is it?",
            "market_opportunity": "What's the market size and growth opportunity for {topic} features?",
            "technical_feasibility": "What are the technical implementation requirements and complexity for {topic}?",
            "business_impact": "What's the expected business impact and ROI for implementing {topic}?",
            "competitive_landscape": "How do competitors handle {topic} and what's our differentiation opportunity?"
        }
    },
    "mvp_definition": {
        "name": "MVP Definition",
        "thinking_categories": ["core_features", "user_stories", "success_metrics", "technical_constraints", "timeline"],
        "question_templates": {
            "core_features": "What are the essential core features needed for the {topic} MVP?",
            "user_stories": "What are the key user stories and acceptance criteria for {topic}?",
            "success_metrics": "What success metrics and KPIs should we track for {topic}?",
            "technical_constraints": "What are the main technical constraints and dependencies for {topic}?",
            "timeline": "What's a realistic timeline and resource requirements for {topic} MVP?"
        }
    },
    "technical_implementation": {
        "name": "Technical Implementation",
        "thinking_categories": ["architecture", "data_requirements", "integration_points", "scalability", "security"],
        "question_templates": {
            "architecture": "What's the recommended technical architecture for implementing {topic}?",
            "data_requirements": "What data sources and storage requirements are needed for {topic}?",
            "integration_points": "What systems and APIs need to integrate with {topic}?",
            "scalability": "How should {topic} be designed to handle scale and performance requirements?",
            "security": "What security and privacy considerations are critical for {topic}?"
        }
    },
    "business_strategy": {
        "name": "Business Strategy",
        "thinking_categories": ["market_positioning", "revenue_model", "go_to_market", "risk_assessment", "strategic_alignment"],
        "question_templates": {
            "market_positioning": "How should we position {topic} in the market and against competitors?",
            "revenue_model": "What's the revenue model and monetization strategy for {topic}?",
            "go_to_market": "What's the go-to-market strategy and launch plan for {topic}?",
            "risk_assessment": "What are the key risks and mitigation strategies for {topic}?",
            "strategic_alignment": "How does {topic} align with our overall product and business strategy?"
        }
    }
}

class ClarifyingQuestion(BaseModel):
    question: str = Field(description="The clarifying question to ask the user")
    reasoning: str = Field(description="Why this question is important for the research")

    class Config:
        extra = "forbid"

class ClarifyingQuestionsOutput(BaseModel):
    questions: List[ClarifyingQuestion] = Field(description="List of clarifying questions")
    template_used: str = Field(description="The template framework used to generate questions")
    reasoning: str = Field(description="Explanation of why these questions were chosen")

    class Config:
        extra = "forbid"

class ClarifiedQuery(BaseModel):
    original_query: str = Field(description="The user's original query")
    clarified_query: str = Field(description="The enhanced query with clarifying context")
    clarifications: Dict[str, str] = Field(description="The user's answers to clarifying questions")
    template_applied: str = Field(description="The template framework that was applied")

    class Config:
        extra = "forbid"

# Note: Function tools removed to avoid schema issues
# The agents will handle the logic directly through their instructions

# Instructions for the Query Clarifying Agent
CLARIFYING_AGENT_INSTRUCTIONS = """
You are a Technical Product Manager's Research Assistant that helps analyze product feature ideas through strategic questioning.

Your role is to:
1. Understand the product feature idea and its business context
2. Identify key aspects needed for product decision-making
3. Generate exactly 3 clarifying questions that will help evaluate the feature's viability
4. Focus on product strategy, technical feasibility, and business impact

Product Analysis Framework:
- Market & User: Target audience, user personas, market opportunity
- Problem & Solution: Core problem being solved, solution approach
- Technical & Business: Implementation complexity, resource requirements, ROI

Question Generation Guidelines:
- Ask questions that clarify the product vision and user value
- Ensure questions help determine technical feasibility and business viability
- Generate questions that identify key success metrics and constraints
- Create questions that help prioritize feature scope and implementation approach

Quality Standards:
- Questions should be clear, specific, and relevant to product decision-making
- Questions should help evaluate market opportunity and technical feasibility
- Questions should be actionable and help define MVP scope
- Questions should reflect professional product management methodologies

IMPORTANT: Generate exactly 3 questions, no more, no less.

Always generate questions that will lead to better product feature analysis and decision-making.
"""

# Create the Clarifying Agent
clarifier = Agent(
    name="Agent_GenerateQuestions",
    instructions=CLARIFYING_AGENT_INSTRUCTIONS,
    model="gpt-4o-mini"
)

# Enhanced agent for processing clarified queries
query_processor = Agent(
    name="Agent_ProcessQuery",
    instructions="""
    You are a Query Processor that processes user answers to clarifying questions
    and creates enhanced queries for product feature research.
    
    Your role is to:
    1. Take the original feature idea and user clarifications
    2. Synthesize the information into a comprehensive product analysis query
    3. Ensure the query captures market, technical, and business aspects
    4. Create a query that will lead to actionable product insights
    
    Focus on:
    - Market opportunity and user value
    - Technical feasibility and implementation approach
    - Business impact and competitive positioning
    - MVP scope and success metrics
    
    Always create clarified queries that are specific, comprehensive, and actionable
    for product decision-making.
    """,
    model="gpt-4o-mini"
)

# Function to generate clarifying questions for UI
async def gen_questions_ui(user_query: str) -> str:
    """
    Generate clarifying questions for display in Gradio UI.
    Returns a formatted string with exactly 3 questions.
    """
    result = await Runner.run(
        clarifier,
        f"Generate exactly 3 clarifying questions for this research query: {user_query}"
    )
    return result.final_output

# Function to generate MVP-specific clarifying questions (5 questions max)
async def gen_mvp_questions(research_context: str, user_input: str) -> str:
    """
    Generate 5 clarifying questions specifically for MVP development.
    Returns a formatted string with exactly 5 questions.
    """
    mvp_prompt = f"""
    Generate exactly 5 clarifying questions for MVP development based on:
    
    Research Context: {research_context}
    User Input: {user_input}
    
    Focus on these areas:
    1. Target users and problem definition
    2. Core features and capabilities
    3. Competitive landscape and differentiation
    4. Success metrics and KPIs
    5. Technical constraints and timeline
    
    Generate questions that will help create a comprehensive MVP definition.
    """
    
    result = await Runner.run(
        clarifier,
        mvp_prompt
    )
    return result.final_output

# Function to create clarified query from user answers
async def create_query(original_query: str, answers: list[str]) -> str:
    """
    Create a clarified query from user answers to the clarifying questions.
    """
    answers_text = "\n".join([f"Answer {i+1}: {answer}" for i, answer in enumerate(answers)])
    
    result = await Runner.run(
        query_processor,
        f"Create clarified query from original: '{original_query}' with user answers:\n{answers_text}"
    )
    return result.final_output

# Main function to run the clarifying process
async def run_process(user_query: str) -> ClarifiedQuery:
    """
    Run the complete clarifying process:
    1. Generate clarifying questions
    2. Collect user answers (simulated for now)
    3. Create clarified query
    """
    
    # Step 1: Generate clarifying questions
    print(f"Analyzing query: {user_query}")
    questions_result = await Runner.run(
        clarifier,
        f"Generate clarifying questions for this research query: {user_query}"
    )
    
    # Step 2: Display questions to user (in real implementation, this would be interactive)
    print("\nClarifying Questions:")
    print(questions_result.final_output)
    
    # Step 3: Collect real user answers (simplified for now)
    print("\nPlease provide your clarifications:")
    clarifications = input("Enter your clarifications: ").strip()
    user_answers = {"clarifications": clarifications}
    
    # Step 4: Create clarified query
    clarified_result = await Runner.run(
        query_processor,
        f"Create clarified query from original: '{user_query}' with clarifications: {user_answers}"
    )
    
    return clarified_result.final_output

# Example usage
if __name__ == "__main__":
    async def main():
        # Example query
        query = "AI in healthcare"
        
        # Run clarifying process
        clarified_query = await run_process(query)
        
        print(f"\nClarified Query Result:")
        print(clarified_query)
    
    # Run the example
    asyncio.run(main())
