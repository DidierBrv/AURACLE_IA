import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from groq import Groq

from auracle_notion_basic_tools import add_todo_notion, fetch_active_todos, update_todo_status, create_subtask
from auracle_notion_creative_tools import append_idea_to_gdd, save_drawing_concept, read_notion_page
from auracle_fitness_tools import log_advanced_workout, fetch_workout_history, display_workout_stats_graph
from auracle_own_tools import check_system_health
from auracle_web_tools import search_the_web

load_dotenv()
app = Flask(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

available_tools = {
    "append_idea_to_gdd": append_idea_to_gdd,
    "save_drawing_concept": save_drawing_concept,
    "log_advanced_workout": log_advanced_workout,
    "fetch_workout_history": fetch_workout_history,
    "display_workout_stats_graph": display_workout_stats_graph,
    "read_notion_page": read_notion_page,
    "search_the_web": search_the_web
}

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "append_idea_to_gdd",
            "description": "Ajoute une idée dans le Game Design Document sur Notion.",
            "parameters": {"type": "object", "properties": {"idea_text": {"type": "string"}}, "required": ["idea_text"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_drawing_concept",
            "description": "Sauvegarde une idée de dessin ou de conception.",
            "parameters": {"type": "object", "properties": {"concept_idea": {"type": "string"}, "category": {"type": "string"}}, "required": ["concept_idea"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_advanced_workout",
            "description": "Enregistre une séance de sport avec des statistiques.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "activity_name": {"type": "string"}, 
                    "activity_type": {"type": "string"}, 
                    "metric_value": {"type": "number"}, 
                    "duration_minutes": {"type": "number"}, 
                    "rpe_score": {"type": "number"}
                }, 
                "required": ["activity_name", "activity_type", "metric_value", "duration_minutes", "rpe_score"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "display_workout_stats_graph",
            "description": "Génère un graphique des performances sportives pour le Dashboard.",
            "parameters": {"type": "object", "properties": {"metric": {"type": "string", "enum": ["performance", "duree_min", "rpe"]}}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_notion_page",
            "description": "Lit le Game Design Document pour analyser les mécaniques existantes.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_the_web",
            "description": "Cherche des informations techniques ou des actualités sur internet.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
        }
    }
]

chat_history = [
    {
        "role": "system", 
        "content": "Tu es Auracle, un assistant IA sarcastique, direct et ultra-efficace. Fais des réponses EXTRÊMEMENT courtes. Si on te demande d'utiliser un outil, exécute-le immédiatement, sans expliquer ce que tu vas faire."
    }
]

@app.route('/ask', methods=['POST'])
def ask_auracle():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "Message vide"}), 400
    chat_history.append({"role": "user", "content": user_message})
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_history,
            tools=tools_schema,
            tool_choice="auto"
        )
        response_message = response.choices[0].message
        chat_history.append(response_message)
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"[Groq] ⚡ Exécution quasi-instantanée : {func_name} | Args: {args}")

                if func_name in available_tools:
                    try:
                        result = available_tools[func_name](**args)
                    except Exception as e:
                        result = {"error": str(e)}
                    chat_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": json.dumps(result)
                    })
            final_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=chat_history
            )
            final_text = final_response.choices[0].message.content
            chat_history.append({"role": "assistant", "content": final_text})
            return jsonify({"reply": final_text})
        final_text = response_message.content
        return jsonify({"reply": final_text})
    except Exception as e:
        print(f"[Serveur Erreur] : {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=== SERVEUR AURACLE [GROQ EDITION] DÉMARRÉ ===")
    app.run(host='0.0.0.0', port=5000, debug=False)