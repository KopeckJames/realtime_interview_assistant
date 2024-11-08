import tkinter as tk
from tkinter import filedialog
import speech_recognition as sr
import threading
from openai import OpenAI
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set the OPENAI_API_KEY in a .env file.")
client = OpenAI(api_key=api_key)
# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Initialize recognizer
recognizer = sr.Recognizer()
listening = False  # Flag to control the listening state

# Adjust silence threshold parameters
recognizer.pause_threshold = 2  # Increase to allow a longer pause
recognizer.phrase_time_limit = 20  # Increase the time limit for each phrase if needed

# Variables to store job description and resume content
job_description = ""
resume_content = ""

# Function to load the resume from a file
def load_resume():
    global resume_content
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "r") as file:
            resume_content = file.read()
        status_label.config(text="Resume loaded successfully.")

# Function to set the job description
def set_job_description():
    global job_description
    job_description = job_description_box.get("1.0", tk.END).strip()
    status_label.config(text="Job description updated.")

# Function to interact with OpenAI's API for LLM response
def get_llm_answer(question):
    # Construct a more conversational and natural prompt
    prompt = (
        f"You are a career advisor helping a candidate prepare for a job interview. "
        f"Consider the following job description and the candidate's resume, and provide a natural, helpful answer to the question. "
        f"Make sure to connect the candidate’s relevant experience to the job description without just reiterating the resume content.\n\n"
        f"Job Description: {job_description}\n"
        f"Candidate's Resume: {resume_content}\n\n"
        f"Question: {question}\n\n"
        "Answer in a conversational and personalized manner:"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"
# Function to continuously listen, transcribe, and process questions
def continuous_transcription():
    global listening
    listening = True
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        transcription_box.insert(tk.END, "Listening...\n")
        
        while listening:
            try:
                audio = recognizer.listen(source)
                transcription = recognizer.recognize_google(audio)
                transcription_box.insert(tk.END, transcription + '\n')
                transcription_box.see(tk.END)
                
                # Check if the transcription is a question
                if "?" in transcription or any(word in transcription.lower() for word in ["what", "why", "how", "when", "who"]):
                    answer = get_llm_answer(transcription)
                    transcription_box.insert(tk.END, f"Answer: {answer}\n")
                    transcription_box.see(tk.END)
                    
            except sr.UnknownValueError:
                transcription_box.insert(tk.END, "Could not understand the audio.\n")
            except sr.RequestError as e:
                transcription_box.insert(tk.END, f"API error: {e}\n")
            except Exception as ex:
                transcription_box.insert(tk.END, f"Error: {ex}\n")

# Function to start transcription in a separate thread
def start_transcription():
    transcription_thread = threading.Thread(target=continuous_transcription)
    transcription_thread.daemon = True
    transcription_thread.start()

# Function to stop listening
def stop_transcription():
    global listening
    listening = False
    transcription_box.insert(tk.END, "Stopped listening.\n")

# Set up the GUI
app = tk.Tk()
app.title("Real-Time Speech Transcription with LLM Responses")
app.geometry("700x600")

# Job Description Input
job_label = tk.Label(app, text="Enter Job Description:")
job_label.pack(pady=5)

job_description_box = tk.Text(app, wrap=tk.WORD, height=5, width=80)
job_description_box.pack(padx=10, pady=5)

job_desc_button = tk.Button(app, text="Set Job Description", command=set_job_description)
job_desc_button.pack(pady=5)

# Resume Upload Button
resume_button = tk.Button(app, text="Upload Resume", command=load_resume)
resume_button.pack(pady=5)

# Display status
status_label = tk.Label(app, text="")
status_label.pack(pady=5)

# Create a text box to display transcriptions and answers
transcription_box = tk.Text(app, wrap=tk.WORD, height=15, width=80)
transcription_box.pack(padx=10, pady=10)

# Create buttons to start and stop transcription
start_button = tk.Button(app, text="Start Transcription", command=start_transcription)
start_button.pack(pady=5)

stop_button = tk.Button(app, text="Stop Transcription", command=stop_transcription)
stop_button.pack(pady=5)

# Start the GUI loop
app.mainloop()
