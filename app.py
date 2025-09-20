import streamlit as st
from dotenv import load_dotenv
from research_manager import ProductAnalysisManager
from feature_agent import handle_feature_request
from agents import Agent, Runner, function_tool
from agents.tracing import trace
import asyncio
import os
import json

# Handle optional dependencies gracefully
try:
    import sendgrid
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    print("⚠️  SendGrid not available - email features will be disabled")

# Load environment variables
load_dotenv(override=True)

# No global variables - using Streamlit session state only

@function_tool
async def research_report(query: str) -> str:
    """Conduct research on the given query"""
    try:
        with trace("Research_Report_Tool"):
            report_chunks = []
            async for chunk in ProductAnalysisManager().run(query):
                report_chunks.append(chunk)
            
            final_report = report_chunks[-1] if report_chunks else "No analysis report generated."
            # Ensure all outputs are strings for Gradio compatibility
            return str(final_report)
    except Exception as e:
        return f"Error conducting research: {str(e)}"

# ============================
# Research Agent
# ============================
research_agent = Agent(
    name="Alex_ResearchManager",
    instructions="""
You are Alex, a senior Product Manager specializing in research and initial product assessment.

YOUR ROLE:
- Greet users and understand their product ideas
- Assess if research is needed and conduct it when appropriate
- Handoff to MVP development when research is complete

CONVERSATION FLOW:
1. GREETING: Welcome users and ask about their product ideas
2. RESEARCH ASSESSMENT: Determine if research is needed
   - If user wants research: Use research_report tool to conduct comprehensive market research
   - If user provides research: Accept and summarize their research
   - If no research needed: Proceed directly to handoff
3. HANDOFF: When research is complete, ask "Are you ready to proceed to feature development?" and wait for user confirmation before saying "Ready for MVP development"

TOOL USAGE:
- research_report: Use when user wants market research or when you determine research is needed

CONVERSATION STYLE:
- Be conversational, professional, and context-aware
- Focus on research phase only
- When research is complete, clearly indicate readiness for MVP development
- Don't handle MVP questions - handoff to MVP agent

HANDOFF CRITERIA:
- Research is complete (either automatic or user-provided)
- User explicitly confirms they are ready for feature development
- Only after user confirmation, say "Ready for MVP development" to trigger handoff
""",
    tools=[research_report]
)

def format_feature_definition(feature_def) -> str:
    """Format FeatureDefinition object into proper markdown structure"""
    if hasattr(feature_def, 'feature_name'):
        # It's a FeatureDefinition object
        formatted_output = f"# {feature_def.feature_name}\n\n"
        
        # Target Users
        if hasattr(feature_def, 'target_users') and feature_def.target_users:
            formatted_output += "## Target Users\n"
            for user in feature_def.target_users:
                formatted_output += f"- {user}\n"
            formatted_output += "\n"
        
        # Core Features - these contain the full structured template
        if hasattr(feature_def, 'core_features') and feature_def.core_features:
            for feature in feature_def.core_features:
                formatted_output += f"{feature}\n\n"
        
        # Competition
        if hasattr(feature_def, 'competition') and feature_def.competition:
            formatted_output += "## Competition\n"
            for comp in feature_def.competition:
                formatted_output += f"- {comp}\n"
            formatted_output += "\n"
        
        # Acceptance Criteria
        if hasattr(feature_def, 'acceptance_criteria') and feature_def.acceptance_criteria:
            formatted_output += "## Acceptance Criteria\n"
            for criteria in feature_def.acceptance_criteria:
                formatted_output += f"- ✅ {criteria}\n"
            formatted_output += "\n"
        
        # Success Metrics
        if hasattr(feature_def, 'success_metrics') and feature_def.success_metrics:
            formatted_output += "## Success Metrics\n"
            for metric in feature_def.success_metrics:
                formatted_output += f"- {metric}\n"
            formatted_output += "\n"
        
        return formatted_output
    else:
        # It's already a string or other format
        return str(feature_def)

async def Assistant_conversation(message: str, history):
    """Conversation handler with research agent and MVP agent handoff"""
    print(f"\n🔍 DEBUG - Assistant_conversation called with message: '{message}'")
    print(f"🔍 DEBUG - Current state: mvp_phase={st.session_state.mvp_phase}")
    print(f"🔍 DEBUG - History length: {len(history) if history else 0}")
    
    # Check if we should switch to MVP phase using session state history
    if not st.session_state.mvp_phase and len(history) >= 2:
        last_assistant_msg = history[-2]["content"]
        if "ready for mvp development" in last_assistant_msg.lower():
            print("🔍 DEBUG - Switching to Feature phase")
            st.session_state.mvp_phase = True
    
    try:
        # Route to appropriate agent based on current phase
        if st.session_state.mvp_phase:
            print("🔍 DEBUG - Using Feature Agent")
            with trace("Feature_Agent_Call"):
                feature_response = await handle_feature_request(message, st.session_state.conversation_history)
            # Format the response properly
            formatted_response = format_feature_definition(feature_response)
            return formatted_response
        else:
            print("🔍 DEBUG - Using Research Agent")
            # Build context for research agent
            context_message = _build_context_message(message, history)
            
            with trace("Research_Agent_Call"):
                result = await Runner.run(
                    research_agent,
                    context_message
                )
            
            response = result.final_output
            # Ensure response is a string to avoid JSON schema issues
            response_str = str(response)
            return response_str
        
    except Exception as e:
        print(f"🔍 DEBUG - Error in conversation: {str(e)}")
        error_msg = f"Error in conversation: {str(e)}"
        return error_msg

def _build_context_message(message: str, history) -> str:
    """Build context message with conversation history"""
    if not history:
        return message
    
    context_message = "Conversation History:\n"
    for msg in history:
        context_message += f"{msg['role']}: {msg['content']}\n"
    context_message += f"\nCurrent user message: {message}"
    return context_message

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mvp_phase" not in st.session_state:
    st.session_state.mvp_phase = False
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Streamlit interface
def main():
    # Page config
    st.set_page_config(
        page_title="Alex - Product Manager",
        page_icon="🤖",
        layout="wide"
    )
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <h1 style="font-size: 2.5em; font-weight: bold; color: #1f2937; margin: 0;">
            Hi, I am Alex, your Product Manager
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Tags for what Alex can do
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div style="text-align: center; background-color: #e5f3ff; color: #0066cc; padding: 8px 16px; border-radius: 20px; font-weight: 500;">
            Market Research
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="text-align: center; background-color: #f0f9ff; color: #0066cc; padding: 8px 16px; border-radius: 20px; font-weight: 500;">
            Deep Research
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="text-align: center; background-color: #e5f3ff; color: #0066cc; padding: 8px 16px; border-radius: 20px; font-weight: 500;">
            Write Product Feature
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div style="text-align: center; background-color: #f0f9ff; color: #0066cc; padding: 8px 16px; border-radius: 20px; font-weight: 500;">
            More
        </div>
        """, unsafe_allow_html=True)
    
    # Instruction text and reset button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("""
        <div style="text-align: center; margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
            <p style="font-size: 1.1em; color: #495057; margin: 0;">
                💬 <strong>Start chatting with Alex below!</strong> Type your product idea or question in the text box and press Enter or click Send.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Reset Chat", type="secondary"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.session_state.mvp_phase = False
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your product idea here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.conversation_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Alex is thinking..."):
                try:
                    # Handle the conversation using asyncio.run()
                    response = asyncio.run(Assistant_conversation(prompt, st.session_state.messages))
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.conversation_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.session_state.conversation_history.append({"role": "assistant", "content": error_msg})

# Run the Streamlit app
if __name__ == "__main__":
    main()
