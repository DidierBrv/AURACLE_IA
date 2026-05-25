import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from auracle_notion_basic_tools import add_todo_notion, fetch_active_todos, update_todo_status, create_subtask
from auracle_notion_creative_tools import append_idea_to_gdd, save_drawing_concept, read_notion_page
from auracle_fitness_tools import fetch_workout_history, log_advanced_workout, display_workout_stats_graph
from auracle_own_tools import check_system_health
from auracle_web_tools import search_the_web

app = Flask(__name__)

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

system_instruction = """
Tu es Auracle, un assistant IA ultra-efficace. 
Ton rôle est d'aider au développement d'organiser des tâches et aider ton utilisateur.
Fais des réponses courtes (maximum 5 phrases).
"""

model = genai.GenerativeModel(
    model_name='gemini-3.1-flash-lite',
    tools=[add_todo_notion, fetch_active_todos, update_todo_status, create_subtask, append_idea_to_gdd, save_drawing_concept, fetch_workout_history, log_advanced_workout, check_system_health, display_workout_stats_graph, read_notion_page, search_the_web],
    system_instruction=system_instruction
)

chat_session = model.start_chat(enable_automatic_function_calling=True)

@app.route('/ask', methods=['POST'])
def ask_auracle():
    """Endpoint API local pour parler à l'IA."""
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "Message vide"}), 400

    try:
        print(f"[Serveur] Reçu : {user_message}")
        response = chat_session.send_message(user_message)
        print(f"[Serveur] Réponse générée.")
        return jsonify({"reply": response.text})
    
    except Exception as e:
        print(f"[Serveur Erreur] : {e}")
        if "429" in str(e):
            return jsonify({"error": "Quota API atteint. Veuillez patienter une minute."}), 429
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=== SERVEUR AURACLE DÉMARRÉ SUR LE PORT 5000 ===")
    app.run(port=5000, debug=False)