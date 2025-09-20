import gradio as gr
from dotenv import load_dotenv
import asyncio
import os

# Load environment variables
load_dotenv(override=True)

# Global variables to store conversation state
conversation_history = []
mvp_phase = False

def simple_chat(message, history):
    """Simple chat function that bypasses the problematic agents"""
    global conversation_history, mvp_phase
    
    # Add user message to history
    conversation_history.append({"role": "user", "content": message})
    
    # Simple response logic
    if "research" in message.lower():
        response = "I can help you with research! What specific topic would you like me to research?"
    elif "feature" in message.lower() or "mvp" in message.lower():
        response = "Great! I can help you develop features for your MVP. What feature would you like to work on?"
    elif "hello" in message.lower() or "hi" in message.lower():
        response = "Hello! I'm Alex, your Product Manager. I can help you with research and feature development. What would you like to work on today?"
    else:
        response = "I understand you want to work on: " + message + ". How can I help you with this?"
    
    # Add assistant response to history
    conversation_history.append({"role": "assistant", "content": response})
    
    # Convert to Gradio format
    formatted_history = []
    for i in range(0, len(conversation_history), 2):
        if i + 1 < len(conversation_history):
            user_msg = conversation_history[i]["content"]
            assistant_msg = conversation_history[i + 1]["content"]
            formatted_history.append([user_msg, assistant_msg])
    
    return formatted_history, ""

def create_interface():
    """Create the Gradio interface"""
    with gr.Blocks(
        title="Alex - Product Manager Assistant",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
            margin: auto !important;
        }
        .chatbot {
            height: 500px !important;
        }
        """
    ) as ui:
        
        # Header
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="margin: 0; font-size: 2.5em;">🤖 Alex - Product Manager Assistant</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9;">
                Your AI-powered product management partner for research and feature development
            </p>
        </div>
        """)
        
        # Create chatbot
        chatbot = gr.Chatbot(
            label="Alex, Product Manager",
            height=500,
            show_copy_button=True
        )
        
        with gr.Row():
            textbox = gr.Textbox(
                label="Your message",
                placeholder="Type your product idea here...",
                scale=4,
                lines=3,
                max_lines=5
            )
            submit_btn = gr.Button("Send", variant="primary", scale=1)
        
        # Connect the submit button and textbox
        submit_btn.click(
            simple_chat,
            inputs=[textbox, chatbot],
            outputs=[chatbot, textbox],
            show_progress=True
        )
        
        textbox.submit(
            simple_chat,
            inputs=[textbox, chatbot],
            outputs=[chatbot, textbox],
            show_progress=True
        )
    
    return ui

# Create the interface
ui = create_interface()

# Launch configuration for Hugging Face Spaces
if __name__ == "__main__":
    ui.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False
    )
