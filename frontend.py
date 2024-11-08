import gradio as gr
import requests

# Backend URL
backend_url = "http://localhost:5000"

# Function to set context (job description and resume)
def set_context(job_description, resume_file):
    with open(resume_file.name, "r") as file:
        resume_content = file.read()
    response = requests.post(
        f"{backend_url}/set_context",
        json={"job_description": job_description, "resume_content": resume_content}
    )
    return response.json().get("status", "Error setting context")

# Function to transcribe audio and get an answer
def transcribe_and_answer(audio_file):
    files = {'file': audio_file}
    response = requests.post(f"{backend_url}/transcribe_and_answer", files=files)
    data = response.json()
    return data.get("transcription", ""), data.get("answer", "")

# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Real-Time Job Interview Assistant")

    job_description = gr.Textbox(label="Job Description", placeholder="Enter job description here...")
    resume_file = gr.File(label="Upload Resume (.txt)")
    set_button = gr.Button("Set Context")
    
    audio_file = gr.Audio(source="upload", type="file", label="Upload an Audio Question")
    transcribed_text = gr.Textbox(label="Transcription")
    answer_text = gr.Textbox(label="LLM Answer")

    set_button.click(set_context, inputs=[job_description, resume_file], outputs=None)
    audio_file.change(transcribe_and_answer, inputs=audio_file, outputs=[transcribed_text, answer_text])

demo.launch()
