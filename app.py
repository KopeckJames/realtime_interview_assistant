from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import speech_recognition as sr

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

recognizer = sr.Recognizer()
job_description = ""
resume_content = ""

# Endpoint to set job description and resume
@app.route('/set_context', methods=['POST'])
def set_context():
    global job_description, resume_content
    data = request.json
    job_description = data.get('job_description', "")
    resume_content = data.get('resume_content', "")
    return jsonify({"status": "Context set successfully"})

# Endpoint to transcribe audio and get LLM answer
@app.route('/transcribe_and_answer', methods=['POST'])
def transcribe_and_answer():
    # Get audio file from request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    audio_file = request.files['file']
    
    try:
        # Process audio file
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        transcription = recognizer.recognize_google(audio)
        
        # Generate LLM response
        prompt = (
            f"You are a career advisor helping a candidate prepare for a job interview. "
            f"Consider the following job description and the candidate's resume, and provide a natural, helpful answer to the question. "
            f"Make sure to connect the candidate’s relevant experience to the job description without just reiterating the resume content.\n\n"
            f"Job Description: {job_description}\n"
            f"Candidate's Resume: {resume_content}\n\n"
            f"Question: {transcription}\n\n"
            "Answer in a conversational and personalized manner:"
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()
        
        return jsonify({"transcription": transcription, "answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
