import gradio as gr

def simple_function(text):
    return f"You said: {text}"

# Create a minimal interface
with gr.Blocks() as demo:
    gr.Markdown("# Simple Test")
    text_input = gr.Textbox(label="Input")
    text_output = gr.Textbox(label="Output")
    text_input.change(simple_function, inputs=text_input, outputs=text_output)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, debug=False)
