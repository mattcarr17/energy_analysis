import gradio as gr

def respond(question):
    pass
    # Pass question to LLM function

gradio_interface = gr.Interface(
    fn = respond,
    inputs=[gr.Textbox(label='Enter question about U.S. Energy System')],
    outputs = [gr.Textbox(), gr.Plot()],
    title='U.S. Energy Data Q&A System'
)

gradio_interface.launch()