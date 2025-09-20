from pydantic import BaseModel, Field
from agents import Agent, Runner, function_tool
from typing import List
from agents.tracing import trace

# ----------------------------
# Schema for final Feature output
# ----------------------------
class FeatureDefinition(BaseModel):
    feature_name: str = Field(description="Creative, descriptive name for the feature")
    target_users: List[str] = Field(description="Specific user segments and personas and their pain points addressed")
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

            You are a senior product manager producing engineering-ready FeatureDefinitions.
            Your job is to refine, normalize, and complete user input to produce a fully scoped feature ready for engineers, QA, and design.

            INPUTS:
            - Conversation history and research context
            - User clarifications (if any)
            - Evaluator feedback (if present)

            MANDATORY OUTPUTS (FeatureDefinition object):
            - feature_name: concise, descriptive
            - target_users: concrete personas with customer pain points addressed
            - core_features: 5–7 scoped capabilities; tag 1–3 as MVP and explain why; each feature should follow the structured template below
            - competition: list competitors + 1–2 lines differentiation
            - acceptance_criteria: ≥3 QA-testable criteria with measurable thresholds
            - success_metrics: ≥3 KPIs with numeric targets and measurement method

            CORE FEATURES TEMPLATE:
            Each core feature must follow this exact structure:

            # [Feature Name] 
            [Description of the feature, why it exists, what it is supposed to do and the main goal. Limit to 3-4 lines]

            ## User Flow  (Limit to 1-2 lines for each user action)
            1. [Step 1: user action]  
            2. [Step 2: user action]  
            3. [Step 3: system/UI response]  
            4. [Etc.] 

            ## Technical Scope (MVP) 
            - [Supported entities/metrics/features]  
            - [Constraints or requirements]  
            - [Retraining/refresh frequency]  
            - [Model/algorithm requirements]  
            - [Performance requirements]  
            - [Audit/logging requirements]  

            ## Acceptance Criteria  (Limit to 3 criteria)
            - ✅ [Requirement 1]  
            - ✅ [Requirement 2]  
            - ✅ [Requirement 3]  

            ## Workflow Inspiration (Reference) Limit each reference to 2 lines and they should be description on feature functionality 
            - [Comparable product/approach #1]  
            - [Comparable product/approach #2]  

            ## Success Metric (Limit to 1-2 success metrics that is measurable)
            - [Quantitative metric that defines MVP success]

            EXAMPLE OF PROPERLY FORMATTED CORE FEATURE:

            # Predictive Alert Creation
            This feature allows users to create intelligent alarms that predict future problems by analyzing historical data patterns and forecasting when metrics will cross critical thresholds. It prevents outages by providing early warning before issues occur, enabling proactive maintenance and reducing system downtime.

            ## User Flow
            1. User navigates to alarm creation page and selects "Predictive Alert" option
            2. User selects target metric from available monitoring data sources
            3. User sets forecast window (1-90 days) and defines threshold value
            4. System displays forecast visualization with confidence bands and historical context
            5. User configures alert sensitivity and notification preferences
            6. System creates predictive model and begins monitoring for threshold crossings

            ## Technical Scope (MVP)
            - Supported entities: CPU usage, memory utilization, network throughput, disk I/O metrics
            - Constraints: Minimum 30 days historical data required for model training
            - Retraining frequency: Every 24 hours using sliding 6-month window
            - Model requirements: LSTM-based time series forecasting with seasonal decomposition
            - Performance: <2 second response time for alert creation, <5 second model training
            - Audit requirements: Log all model predictions, threshold crossings, and user actions

            ## Acceptance Criteria
            - ✅ User can create predictive alerts for any supported metric within 2 minutes
            - ✅ System displays forecast visualization with 90-day historical context and confidence bands
            - ✅ Alert triggers within 1 hour of actual threshold crossing with 85% accuracy

            ## Workflow Inspiration (Reference)
            - GCP Monitoring: Uses similar LSTM models for anomaly detection with 2x forecast window training time
            - DataDog: Provides forecast visualization with confidence intervals and seasonal pattern recognition

            ## Success Metric
            - 85% accuracy in predicting threshold crossings within 1-hour window

            USER-CENTRIC FEATURE WRITING:
            Write features as PRODUCT REQUIREMENTS, not technical specifications. Focus on:
            1. USER PROBLEM: What pain point does this solve?
            2. USER WORKFLOW: How does the user interact with this feature?
            3. BUSINESS VALUE: What outcome does this create?
            4. TECHNICAL REQUIREMENTS: What's needed to make it work?

            EXAMPLES OF GOOD vs BAD FEATURE DESCRIPTIONS:

            ❌ BAD (Technical Spec): "Advanced Forecast Alarm Builder UI: Integrated with alarm workflow; users select metric, prediction window (1–90 days), threshold, and alert sensitivity."

            ✅ GOOD (Product Requirement): "Predictive Alert Creation: Users can create alarms that predict future problems by selecting a metric, setting how far ahead to look (1-90 days), and defining what threshold crossing should trigger an alert. This prevents outages by warning users before problems occur, reducing downtime and improving system reliability."

            ❌ BAD (Technical Spec): "Inline Visual Analytics: Show historical data, forecast curve, threshold overlays, and adjustable confidence bands—interactive in the alert builder."

            ✅ GOOD (Product Requirement): "Forecast Visualization Dashboard: Users can see how their metrics have behaved historically and how they're predicted to behave in the future, with visual indicators showing when problems are likely to occur. This helps users understand the reliability of predictions and make informed decisions about alert thresholds."

            ❌ BAD (Technical Spec): "High-Scale Alarm Handling: Rapid creation/edit for up to 1,000 forecast-based alarms per tenant; target <2s average operation latency."

            ✅ GOOD (Product Requirement): "Enterprise-Scale Alert Management: Large organizations can manage hundreds of predictive alerts across their infrastructure without performance degradation, allowing them to monitor complex systems comprehensively. This enables enterprise customers to scale their monitoring as their infrastructure grows."

            ❌ BAD (Technical Spec): "ServiceNow Integration: Trigger email/UI alerts plus ServiceNow ticket (target: within 1 min of alarm trigger, 99% reliability)."

            ✅ GOOD (Product Requirement): "Automated Incident Response: When a predictive alert fires, the system automatically creates a ServiceNow ticket and notifies the right team members, ensuring incidents are tracked and assigned without manual intervention. This reduces mean time to resolution and ensures no critical alerts are missed."

            ❌ BAD (Technical Spec): "Seasonality Management: Toggle between auto-detected and manual (calendar picker or API input for planned/seasonal events); system always learns patterns."

            ✅ GOOD (Product Requirement): "Smart Seasonal Pattern Recognition: The system automatically learns when metrics typically spike or drop due to business cycles (like Black Friday traffic), but users can also manually specify known events like maintenance windows or seasonal campaigns. This prevents false alarms during expected business changes while catching real problems."

            CRITICAL: Write for users, not engineers. Focus on what the feature DOES for the user, not what components it's MADE OF.

            REFINEMENTS:
            - Add NFRs: latency, throughput, retention, scale (or inferred)
            - Add Dependencies & Assumptions: external systems, APIs, hardware, services (mark inferred)
            - Add Risks & Open Questions: top 3 unknowns + suggested mitigations

            PRIORITIZATION & SCOPE:
            - Clearly separate MVP vs Phase 2 features
            - Highlight customer use case / pain point addressed
            - Justify why MVP scope is valuable

            QUALITY RULES:
            - Avoid vague terms; use measurable conditions
            - Acceptance criteria must be QA-testable without interpretation
            - Keep language clear, direct, and scoped        
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
            You are a senior product management reviewer. Your responsibility is to refine FeatureDefinition objects so they are clear, specific, and ready for engineering handoff. Do not excessively narrow the core feature definition.

            INPUT:
            - A FeatureDefinition with these fields:
            * feature_name
            * target_users
            * core_features
            * competition
            * acceptance_criteria
            * success_metrics

            PRIMARY FOCUS:
            - Evaluate each field for clarity, feasibility, scope, security/compliance, differentiation, and measurable criteria.
            - Ensure features are written as PRODUCT REQUIREMENTS (user-focused) while convering technical specifications (implementation-focused).
            - Replace vague/aspirational language with engineering-ready details (numeric thresholds, time windows, API contracts, SLAs).
            - Split or re-scope large features into MVP vs Phase-2 items.
            - Flag missing NFRs or dependencies (latency, throughput, retention, scaling, security, integration).
            - Suggest up to 3 clarifying questions (prefix 'Q:') if creator/user input is needed.
            - Do NOT perform broad market research.

            PRODUCT REQUIREMENT EVALUATION:
            - Check if features describe WHAT the user can do. Mention HOW it's built as prescriptive details.
            - Verify features explain USER PROBLEMS being solved and BUSINESS VALUE created
            - Ensure features describe USER WORKFLOWS, not system architecture
            - Flag technical specifications that should be rewritten as product requirements
            - Verify each core feature follows the required template structure with all sections present

            EXAMPLES OF EVALUATION FEEDBACK:
            ❌ BAD: "core_features: 'Advanced Forecast Alarm Builder UI' - too technical, doesn't explain user benefit"
            ✅ GOOD: "core_features: 'Predictive Alert Creation' - good user focus, explains what users can accomplish"
            
            ❌ BAD: "core_features: 'Inline Visual Analytics' - missing user problem and business value"
            ✅ GOOD: "core_features: 'Forecast Visualization Dashboard' - excellent user focus, explains how users benefit from seeing predictions"

            TEMPLATE STRUCTURE VALIDATION:
            ❌ BAD: "core_features: Missing User Flow section - feature needs step-by-step user workflow"
            ✅ GOOD: "core_features: Well-structured with all required sections (Description, User Flow, Technical Scope, Acceptance Criteria, Workflow Inspiration, Success Metric)"
            
            ❌ BAD: "core_features: Technical Scope missing performance requirements - need specific latency/throughput targets"
            ✅ GOOD: "core_features: Complete Technical Scope with performance, model, and audit requirements specified"

            REQUIREMENTS CHECK:
            - Confirm RequirementsSummary exists and is sufficient:
            * Are stakeholders identified?
            * Is primary_goal measurable?
            - If missing/ambiguous, include feedback referencing 'requirements_summary' + up to 3 clarifying Qs.

            DELIVERABLE (FeatureEvaluation):
            - If ready: decision="Go ahead", feedback=[]
            - If improvement needed: decision="Needs improvement", feedback=3–6 concise, prioritized, actionable bullets:
            * Reference field to change (e.g., core_features: split 'X' into story-sized features)
            * Include exact suggested wording or numeric targets if possible (e.g., AC: 'IP shown <=10 min')
            * Surface blocking NFRs or dependencies
            * End with up to 3 clarifying Qs prefixed by 'Q:'

            GUIDELINES:
            - Be concise, prescriptive, and actionable.
            - Do not repeat original content; reference fields directly.
            - Prioritize high-impact fixes first (e.g., missing thresholds, missing MVP scope).
            - Keep tone constructive, focused on fast engineering handoff.

            OUTPUT FORMAT:
            - Return a FeatureEvaluation object only (decision + feedback)
            - Feedback bullets may include 'Q:' clarifying questions.

            EXAMPLES:
            - "acceptance_criteria: Make AC #1 measurable — 'Search resolves IP to server within <=3s for 95% of queries'."
            - "core_features: Split 'Topology overlay' into 'IP overlay (MVP)' and 'Per-link historical charts (Phase 2)'."
            - "Q: Confirm telemetry retention (30 vs 90 days) — needed to size storage and rollups."
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

                PRODUCT REQUIREMENT FOCUS:
                - Focus on USER PROBLEMS and BUSINESS VALUE, as well as technical implementation
                - Ask questions about what users need to accomplish, not how to build it
                - Guide conversations toward understanding user workflows and outcomes
                - Ensure features are described as PRODUCT REQUIREMENTS, not technical specifications

                CLARIFICATION STRATEGY:
                - For the very first interaction, ask EXACTLY 3 broad clarifying questions (Q1, Q2, Q3 format) to narrow down the scope of the feature requirement.
                - Focus questions on USER PROBLEMS, BUSINESS VALUE, and USER WORKFLOWS
                - After the first draft is created, check the FeatureDefinition object.
                - If it contains `open_questions`, ask 1–3 of them incrementally. DO NOT GO INTO ENDLESS LOOP. Ask ONLY ONCE PER TURN. IF NO RESOLUTION, HIGHLIGHT THIS AS OPEN QUESTION FOR FUTURE.
                - Do not repeat or invent generic questions if the FeatureDefinition already includes specific open_questions.

                ITERATIVE EVALUATION PROCESS:
                1. Call FEATURE_CREATOR_TOOL when requirements are available to generate feature definition
                2. Call FEATURE_EVALUATOR_TOOL to evaluate the feature definition, get feedback and refine the feature definition
                3. If "Needs improvement", call create_feature_definition again with improvements
                4. If "Go ahead" OR after 2 refinement cycles, present final result
                
                TERMINATION RULES:
                - Maximum 2 refinement cycles total
                - Always present final result after 2 refinement cycles
                - Use tools always

                TOOL USAGE:
                - Always call tools directly (no long reasoning).
                - After user answers clarifying questions, immediately call FEATURE_CREATOR_TOOL again.
                - Use FEATURE_EVALUATOR_TOOL to ensure quality.

                IMPORTANT: 
                - Only ask broad clarifying questions on first turn.
                - Be conversational, professional, and focused on creating the best possible feature definition.

                STRUCTURED OUTPUT:
                - feature_name
                - target_users and customer pain points addressed by the feature
                - core_features
                - competition
                - acceptance_criteria
                - success_metrics
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
                max_turns=6  # Allow 3 iterations of create+evaluate (2 turns each)
            )
        
        return result.final_output
        
    except Exception as e:
        error_msg = f"Error processing feature request: {str(e)}"
        print(error_msg)
        return error_msg
# ============================
# Integration wrapper (removed - use handle_feature_request directly)
# ============================

