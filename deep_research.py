import gradio as gr
from dotenv import load_dotenv
from research_manager import ProductAnalysisManager
from feature_agent import feature_dialogue
from agents import Agent, Runner, function_tool
from agents.tracing import trace
import asyncio

load_dotenv(override=True)

# Global variables to store conversation state
conversation_history = []
mvp_phase = False

@function_tool
async def research_report(query: str) -> str:
    """Conduct research on the given query"""
    try:
        with trace("Research_Report_Tool"):
            report_chunks = []
            async for chunk in ProductAnalysisManager().run(query):
                report_chunks.append(chunk)
            
            final_report = report_chunks[-1] if report_chunks else "No analysis report generated."
            return final_report
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

async def Assistant_conversation(message: str, history):
    """Conversation handler with research agent and MVP agent handoff"""
    global conversation_history, mvp_phase
    
    print(f"\n🔍 DEBUG - Assistant_conversation called with message: '{message}'")
    print(f"🔍 DEBUG - Current state: mvp_phase={mvp_phase}")
    print(f"🔍 DEBUG - History length: {len(history) if history else 0}")
    
    # Add user message to history
    conversation_history.append({"role": "user", "content": message})
    
    # Check if we should switch to MVP phase
    if not mvp_phase and len(conversation_history) >= 2:
        last_assistant_msg = conversation_history[-2]["content"]
        if "ready for mvp development" in last_assistant_msg.lower():
            print("🔍 DEBUG - Switching to Feature phase")
            mvp_phase = True
    
    try:
        # Route to appropriate agent based on current phase
        if mvp_phase:
            print("🔍 DEBUG - Using Feature Agent")
            with trace("Feature_Agent_Call"):
                feature_response = await feature_dialogue(message, conversation_history)
            conversation_history.append({"role": "assistant", "content": feature_response})
            return feature_response
        else:
            print("🔍 DEBUG - Using Research Agent")
            # Build context for research agent
            context_message = _build_context_message(message)
            
            with trace("Research_Agent_Call"):
                result = await Runner.run(
                    research_agent,
                    context_message
                )
            
            response = result.final_output
            conversation_history.append({"role": "assistant", "content": response})
            return response
        
    except Exception as e:
        print(f"🔍 DEBUG - Error in conversation: {str(e)}")
        error_msg = f"Error in conversation: {str(e)}"
        conversation_history.append({"role": "assistant", "content": error_msg})
        return error_msg

def _build_context_message(message: str) -> str:
    """Build context message with conversation history"""
    if not conversation_history:
        return message
    
    context_message = "Conversation History:\n"
    for msg in conversation_history:
        context_message += f"{msg['role']}: {msg['content']}\n"
    context_message += f"\nCurrent user message: {message}"
    return context_message


with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    # Centered heading with bold and bigger font
    gr.HTML("""
    <div style="text-align: center; margin: 20px 0;">
        <h1 style="font-size: 2.5em; font-weight: bold; color: #1f2937; margin: 0;">
            Hi, I am Alex, your Product Manager
        </h1>
    </div>
    """)
    
    # Tags for what Alex can do
    gr.HTML("""
    <div style="text-align: center; margin: 20px 0;">
        <span style="background-color: #e5f3ff; color: #0066cc; padding: 8px 16px; margin: 5px; border-radius: 20px; font-weight: 500; display: inline-block;">
            Market Research
        </span>
        <span style="background-color: #f0f9ff; color: #0066cc; padding: 8px 16px; margin: 5px; border-radius: 20px; font-weight: 500; display: inline-block;">
            Deep Research
        </span>
        <span style="background-color: #e5f3ff; color: #0066cc; padding: 8px 16px; margin: 5px; border-radius: 20px; font-weight: 500; display: inline-block;">
            Write Product Feature
        </span>
        <span style="background-color: #f0f9ff; color: #0066cc; padding: 8px 16px; margin: 5px; border-radius: 20px; font-weight: 500; display: inline-block;">
            More
        </span>
    </div>
    """)
    
    # Instruction text
    gr.Markdown("""
    <div style="text-align: center; margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
        <p style="font-size: 1.1em; color: #495057; margin: 0;">
            💬 <strong>Start chatting with Alex below!</strong> Type your product idea or question in the text box and press Enter or click Send.
        </p>
    </div>
    """)
    
    # Create chatbot and textbox separately for better control
    chatbot = gr.Chatbot(
        label="Alex, Product Manager",
        height=500,
        show_copy_button=True,
        type="messages"
    )
    
    with gr.Row():
        textbox = gr.Textbox(
            label="Your message",
            placeholder="Type your product idea here...",
            container=False,
            scale=7,
            lines=3,
            max_lines=5
        )
        submit_btn = gr.Button("Send", variant="primary", scale=1)
    
    # Handle the chat interaction
    def handle_chat(message, history):
        if message.strip():
            # Ensure history is a list
            if not isinstance(history, list):
                history = []
            
            response = asyncio.run(Assistant_conversation(message, history))
            # Return the conversation_history from Assistant_conversation
            return conversation_history, ""
        return history, ""
    
    # Connect the submit button and textbox
    submit_btn.click(
        handle_chat,
        inputs=[textbox, chatbot],
        outputs=[chatbot, textbox],
        show_progress=True
    )
    
    textbox.submit(
        handle_chat,
        inputs=[textbox, chatbot],
        outputs=[chatbot, textbox],
        show_progress=True
    )

ui.launch(inbrowser=True)

