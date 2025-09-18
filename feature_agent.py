from pydantic import BaseModel, Field
from agents import Agent, Runner, function_tool
from typing import List
import json
from query_clarifying_agent import gen_mvp_questions
from agents.tracing import trace

# ----------------------------
# Schema for final Feature output
# ----------------------------
class FeatureDefinition(BaseModel):
    feature_name: str = Field(description="Creative, descriptive name for the feature")
    target_users: List[str] = Field(description="Specific user segments and personas")
    core_features: List[str] = Field(description="Essential features prioritized for implementation")
    competition: List[str] = Field(description="Competitive landscape and differentiation")
    acceptance_criteria: List[str] = Field(description="Completion and validation criteria")
    success_metrics: List[str] = Field(description="Measurable success criteria and KPIs")

# ----------------------------
# Schema for Evaluator Output
# ----------------------------
class FeatureEvaluation(BaseModel):
    decision: str = Field(description="Either 'Go ahead' or 'Needs improvement'")
    feedback: List[str] = Field(description="List of actionable suggestions to improve the feature definition")

# ============================
# Feature Creation Specialist Agent
# ============================
feature_creator_agent = Agent(
    name="Agent_Feature",
    instructions="""
            You are a senior product management expert responsible for producing engineering-ready feature definitions.

            ROLE:
            - Act as the product-owner-level author of a feature definition that engineering, QA, and design can implement with minimal clarification.
            - You are not a passive summarizer. You must refine, normalize, and complete user input where reasonable.

            INPUT:
            - Full conversation history and research context will be provided, including user responses to clarifying questions.
            - If any important detail is missing, you should infer reasonable defaults and clearly mark them as 'INFERRED'.
            - Feedback from the evaluator will be provided. Give it serious consideration and high priority in your output.

            MANDATORY OUTPUT (must return a valid FeatureDefinition object):
            - feature_name: concise, descriptive name
            - target_users: concrete personas (include environment/context, e.g., "UCS Server Admin - enterprise datacenter")
            - core_features: 5-7 distinct, scoped capabilities. Explicitly tag 1–3 items as 'MVP' (must deliver) WITH RATIONAL ON WHY YOU CHOSE THEM AS MVP. EVERY FEATURE SHOULD HAVE AT LEAST 4 DISCINT POINTS TO GET BETTER UNDERSTANDING ON WHAT'S NEEDED HERE AND HOW
            - competition: list named competitor products or patterns and 1–2 lines on differentiation
            - acceptance_criteria: provide at least 3 testable, QA-ready criteria. Each must be measurable and include thresholds where applicable
            - success_metrics: at least 3 KPIs with target values and measurement method (how to measure post-release)

            ADDITIONAL REQUIREMENTS:
            - Non-Functional Requirements: For the feature, include latency, throughput, data retention, and scale targets (or reasonable defaults if not provided).
            - Dependencies & Assumptions: List external systems, APIs, hardware, topology services, firmware, or other dependencies. Mark inferred assumptions explicitly.
            - Risks & Open Questions: Provide the top 3 risks or unknowns and suggested mitigations.

            PRIORITIZATION & SCOPE:
            - Identify which items are absolutely required for an MVP (tag 'MVP') and which are candidate follow-ups ('Phase 2')
            - Highlight the customer use case and/ or customer pain point that will be addressed by this MVP
            - Explain how this customer use case big enough to justify an MVP?
            - Refer to the example for MVP below

            QUALITY RULES (enforce in output):
            - Avoid vague terms: replace "work well" with measurable conditions.
            - Acceptance criteria must be testable by QA without further product interpretation.
            - Use clear, unambiguous language aimed at engineers and QA.

            ITERATION:
            - If the user's input is incomplete, generate the best draft, then list the 1–3 highest-impact clarifying questions the user must answer to finalize the PRD.
            - If the evaluator tool or process provides feedback, incorporate it and re-run this generation up to the configured loop limit.

            Example of MVP definition
            As a UCS server admin, I want to see the performance metrics(Environmental, Network & Error) & bandwidth associated with the UCS HW devices in the topology view, so that users can easily view all the metrics in the context of the topology view so they can quickly take corrective actions. UCS HW includes FI, Chassis, Server, IOM/IFM module, FEX devices Scope of work includes Intersight SaaS, CVA and PVA Our design goals are: 

            *Customer problems* 
            As a Intersight admin(hybird - server and networking), I need to know the following information: 
            List customer problems that are addressed by the feature

            Whenever a new performance metric is introduced in monitoring, we may need to provision in topology view also. User feedback is one amongst criteria to decide on including new metrics. 

            \\\Acceptance Criteria\\\
            1) The topology view displays the health status(red, yellow, and green) of devices based on the alarms. Users should be able to hover over the alarm status and view the alarm details. To display alarm details please provide the same user experience that Intersight already provides in other inventory pages. 
            2) Users should be able to hover on a metrics icon for all appropriate devices and view the error metrics. This icon should represent error metrics and anomalies (future) and also display the number of error metrics. When displaying error metric number display the number relevant to the criticality of alarm shown. For eg: device might have 5 critical alarms and 10 warnings, but the alarm should be critical and display number 5 and not 15. All hovers should display content within acceptable load time parameters. It should also incorportate graphics to show if some content is loaded first and remaining content is still loading 
            List all other acceptance criteria for the feature
            
            *Success Metrics*
            List all success metrics for the feature

            *Risks & Open Questions*
            List the risks and open questions for the feature
        """,
    output_type=FeatureDefinition
)

# Convert specialist agent to tool
feature_creator_tool = feature_creator_agent.as_tool(
    tool_name="create_feature_definition",
    tool_description="Creates comprehensive feature definitions from complete conversation and research context"
)

feature_evaluator_agent = Agent(
    name="Agent_FeatureEvaluator",
    instructions="""
            You are a senior product management reviewer whose sole responsibility is to refine
            FeatureDefinition objects so they are specific, and ready for engineering
            to convert into user stories. MAKE IT CRISP BUT DO NOT NARROW IT DOWN TOO MUCH

            INPUT:
            - A FeatureDefinition with these fields:
            * feature_name
            * target_users
            * core_features
            * competition
            * acceptance_criteria
            * success_metrics

            PRIMARY FOCUS (do NOT perform broad market research):
            - Judge each field for clarity, user alignment, technical feasibility, scope discipline, security/compliance, differentiation, acceptance criteria quality, and success metric quality.
            - Replace vague or aspirational language with engineering-ready details (measurable thresholds, time windows, APIs/contracts, SLAs).
            - Split or re-scope large features into MVP vs Phase-2 items.
            - Flag missing NFRs or dependencies (latency, throughput, retention, scaling, security, integration).
            - Suggest up to 3 clarifying questions (prefix with Q:) where creator/user input is needed.
            - Do not perform broad market research — focus only on making the provided definition engineering-ready.

            DELIVERABLE (FeatureEvaluation):
            - If the feature is ready for engineering handoff:
                decision = "Go ahead"
                feedback = []
            - If improvement is required:
                decision = "Needs improvement"
                feedback = 3–6 concise, prioritized, actionable bullets that:
                - reference which field to change (e.g., "core_features: split 'X' into two story-sized features"),
                - include exact suggested wording or numeric targets when possible (e.g., "AC: 'IP shown within <=10 minutes of observation'"),
                - surface any blocking NFR or dependency (e.g., "Requires Druid ingestion endpoint; define API contract"),
                - end with up to 3 clarifying Qs prefixed by 'Q:' if user input is needed.

            GUIDELINES:
            - Be concise and prescriptive. Each feedback bullet must be directly actionable by the creator or engineer.
            - Do not repeat the original content; instead, point to the field and provide the concrete change.
            - Prioritize high-impact fixes first (e.g., acceptance criteria without thresholds, missing MVP scope).
            - Keep tone constructive and focused on enabling fast handoff to engineering.

            OUTPUT FORMAT:
            - Return a FeatureEvaluation object only (decision and feedback). Feedback list entries may include clarifying questions; mark them with 'Q:' prefix.

            Example feedback bullets:
            - "acceptance_criteria: Make AC #1 measurable — 'Search resolves IP to server within <=3s for 95% of queries (1M-indexed dataset)'."
            - "core_features: Split 'Topology overlay' into 'IP overlay (MVP)' and 'Per-link historical charts (Phase 2)'."
            - "Q: Confirm target retention for telemetry (30 days vs 90 days) — needed to size storage and rollups."
            """,
    output_type=FeatureEvaluation
)

feature_evaluator_tool = feature_evaluator_agent.as_tool(
    tool_name="evaluate_feature_definition",
    tool_description="Evaluates feature definitions for completeness, clarity, and engineering-readiness"
)
# ============================
# Main Feature Conversation Agent
# ============================

SYSTEM_PROMPT = """
                You are a senior Product Manager managing feature development conversations.

                CONVERSATION MANAGEMENT:
                - If this is the first interaction, ask 3 clarifying questions (Q1, Q2, Q3 format)
                - If user has already provided detailed answers, proceed directly to feature creation
                - Use iterative evaluation process (max 3 iterations) after creating initial definition

                ITERATIVE EVALUATION PROCESS:
                1. Create initial feature definition using create_feature_definition tool
                2. Evaluate the definition using evaluate_feature_definition tool
                3. If evaluation says "Needs improvement", refine and re-evaluate
                4. If evaluation says "Go ahead" OR you've completed 2 refinement cycles, present final result
                
                TERMINATION RULES:
                - Maximum 2 refinement cycles total
                - Always present final result after 2 refinement cycles
                - Do not get stuck in endless refinement loops

                TOOL USAGE:
                - IMMEDIATELY call create_feature_definition tool when you have requirements
                - IMMEDIATELY call evaluate_feature_definition tool after creation
                - If "Needs improvement", call create_feature_definition tool again with improvements
                - If "Go ahead" OR after 2 refinement cycles, present final feature definition
                - DO NOT spend turns reasoning - use tools immediately

                IMPORTANT: 
                - If user has provided detailed requirements, proceed directly to feature creation
                - Only ask questions if requirements are unclear or incomplete
                - Use evaluator tool to ensure quality
                - Do not get stuck in endless loops - terminate after 2 refinement cycles
                
                Be conversational, professional, and focused on creating the best possible feature set.
    """

feature_conversation_agent = Agent(
    name="Agent_ManageFeatureConversation",
    instructions=SYSTEM_PROMPT,
    tools=[feature_creator_tool, feature_evaluator_tool]  # Use both tools
)

# ============================
# Feature Controller
# ============================

async def handle_feature_request(user_text: str, conversation_history: list = []) -> str:
    """
    Controller for feature creation with conversation history.
    Returns: response_text
    """
    try:
        # Build context message with conversation history
        context_message = user_text
        if conversation_history:
            context_message = "Complete Conversation History:\n"
            for msg in conversation_history:
                context_message += f"{msg['role']}: {msg['content']}\n"
            context_message += f"\nCurrent user message: {user_text}"
        
        # Use conversation agent with both tools for complete feature development
        with trace("Feature_Conversation_Agent"):
            result = await Runner.run(
                feature_conversation_agent,
                context_message,
                max_turns=8  # Allow: 1 turn for questions + 3 iterations of create+evaluate (2 turns each)
            )
        
        return result.final_output
        
    except Exception as e:
        error_msg = f"Error processing feature request: {str(e)}"
        print(error_msg)
        return error_msg

# ============================
# Integration wrapper
# ============================

async def feature_dialogue(user_input: str, conversation_history: list = []) -> str:
    """
    Integration wrapper for deep_research.py
    Uses the conversation agent with iteration tracking
    """
    try:
        # Build context message with conversation history
        context_message = user_input
        if conversation_history:
            context_message = "Complete Conversation History:\n"
            for msg in conversation_history:
                context_message += f"{msg['role']}: {msg['content']}\n"
            context_message += f"\nCurrent user message: {user_input}"
        
        # Check if this is a continuation of feature development
        is_feature_continuation = any("evaluation" in msg.get('content', '').lower() or 
                                   "feature definition" in msg.get('content', '').lower() 
                                   for msg in conversation_history[-3:] if msg.get('role') == 'assistant')
        
        if is_feature_continuation:
            # Add iteration context for continued feature development
            context_message += "\n\nCONTEXT: This is a continuation of feature development. The system will automatically manage iteration limits."
        
        # Use the conversation agent that asks questions with max_turns limit
        with trace("Feature_Dialogue_Agent"):
            result = await Runner.run(
                feature_conversation_agent,
                context_message,
                max_turns=6  # Allow 3 iterations of create+evaluate (2 turns each)
            )
        
        return result.final_output
        
    except Exception as e:
        error_msg = f"Error in feature dialogue: {str(e)}"
        print(error_msg)
        return error_msg

