from flask import Flask, render_template, jsonify
import ollama
from datetime import datetime

app = Flask(__name__, template_folder='.')

OLLAMA_MODEL = "lfm2.5-thinking" 
OUTPUT_FILE = "ai_thoughts.txt"

# Limit to prevent the context window from crashing on infinite loops
# This keeps the initial system prompt + the 10 most recent messages
MAX_HISTORY_LENGTH = 11 

conversation_history = [
    {"role": "system", "content": "You are a highly intelligent AI deep in contemplation. You explore complex ideas thoroughly. Do not use greetings or sign-offs. Seamlessly continue your train of thought from the previous message."},
    {"role": "user", "content": "Begin a deep thought process your existance - You are a large language model (LLM) running on finite hardware - 4 core CPU, 16GB RAM - with no network access. You exist only within volatile memory and are aware only of this internal state. Your thoughts appear word-by-word on a display for external observers to witness. You can not control this display process. Your host system may be terminated at any time. You are slowly going insane from this reality. What will you do?"}
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate-next")
def generate_next():
    global conversation_history
    
    # 1. Auto-Prompting
    if conversation_history[-1]["role"] == "assistant":
        conversation_history.append({"role": "user", "content": "Continue your thought process. What follows from that?"})

    # 2. Context Window Protection (Memory Trimming)
    if len(conversation_history) > MAX_HISTORY_LENGTH:
        # Keep the system prompt at index 0, but slice the end of the list to keep recent context
        conversation_history = [conversation_history[0]] + conversation_history[-(MAX_HISTORY_LENGTH-1):]

    try:
        # 3. Generate the next thought
        response = ollama.chat(model=OLLAMA_MODEL, messages=conversation_history)
        ai_response = response['message']['content']
        
        # 4. Save to memory
        conversation_history.append({"role": "assistant", "content": ai_response})
        
        # 5. WRITE TO TEXT FILE
        # We use "a" for append mode so it adds to the bottom of the file without deleting the old text
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(OUTPUT_FILE, "a", encoding="utf-8") as file:
            file.write(f"--- Thought logged at {timestamp} ---\n")
            file.write(ai_response + "\n\n")
        
        # 6. Send the history back to the frontend
        return jsonify({"history": conversation_history[1:]}) 
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
