import os
from dotenv import load_dotenv
from notion_client import Client
import subprocess
import matplotlib

matplotlib.use('Agg') 
import matplotlib.pyplot as plt

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
notion = Client(auth=NOTION_TOKEN)

def log_advanced_workout(activity_name, activity_type, metric_value, duration_minutes, rpe_score):
    """
    Enregistre une séance de sport avec des métriques précises pour le suivi des performances.
    activity_type : 'Musculation', 'Cardio', 'Course', etc.
    metric_value : Nombre représentant la performance principale (poids en kg, distance en km, nombre de reps).
    rpe_score : Intensité ressentie de 1 (très facile) à 10 (effort maximal).
    """
    try:
        SPORT_DATABASE_ID = os.getenv("NOTION_SPORT_DATABASE_ID")
        
        new_page = notion.pages.create(
            parent={"database_id": SPORT_DATABASE_ID}, 
            properties={
                "Séance": {"title": [{"text": {"content": activity_name}}]},
                "Type": {"select": {"name": activity_type}},
                "Valeur": {"number": float(metric_value)},
                "Durée": {"number": int(duration_minutes)},
                "RPE / Intensité": {"number": int(rpe_score)}
            }
        )
        print(f"[Coach]: Séance '{activity_name}' correctement loggée.")
        return {"success": True, "message": "Séance enregistrée dans ton carnet d'entraînement."}
    except Exception as e:
        print(f"[Error] Failed to log workout: {e}")
        return {"error": str(e)}

def fetch_workout_history(limit=10):
    """
    Récupère les dernières séances de sport enregistrées pour permettre l'analyse des statistiques.
    """
    try:
        SPORT_DATABASE_ID = os.getenv("NOTION_SPORT_DATABASE_ID")
        
        db_info = notion.databases.retrieve(database_id=SPORT_DATABASE_ID)
        data_source_id = db_info["data_sources"][0]["id"]
        
        response = notion.data_sources.query(
            data_source_id=data_source_id,
            page_size=int(limit)
        )
        
        history = []
        for page in response.get("results", []):
            props = page["properties"]
            
            title_list = props.get("Séance", {}).get("title", [])
            name = title_list[0]["text"]["content"] if title_list else "Inconnu"
            
            act_type = props.get("Type", {}).get("select", {})
            act_type_name = act_type.get("name", "Non spécifié") if act_type else "Non spécifié"
            
            val = props.get("Valeur", {}).get("number", 0)
            dur = props.get("Durée", {}).get("number", 0)
            rpe = props.get("RPE / Intensité", {}).get("number", 0)
            
            history.append({
                "nom": name,
                "type": act_type_name,
                "performance": val,
                "duree_min": dur,
                "rpe": rpe
            })
            
        print(f"[Coach]: {len(history)} séances récupérées pour analyse.")
        return {"history": history}
    except Exception as e:
        print(f"[Error] Failed to fetch workout history: {e}")
        return {"error": str(e)}
    
def display_workout_stats_graph(metric="performance"):
    """
    Génère et affiche une fenêtre graphique de tes performances sportives.
    L'argument 'metric' indique ce que l'IA a décidé de tracer : 
    peut être 'performance' (poids/distance), 'duree_min' (temps), ou 'rpe' (intensité).
    """
    try:
        data = fetch_workout_history(limit=15)
        if "error" in data: 
            return data
            
        history = data.get("history", [])
        if len(history) < 2:
            return {"message": "Pas assez de données pour tracer une courbe. Il faut au moins deux séances !"}
        
        history.reverse()
        x_labels = [f"{s['nom'][:10]}" for s in history] 
        
        if metric == "performance":
            y_values = [s['performance'] for s in history]
            title = "Évolution de la Charge / Distance"
            ylabel = "Valeur (kg ou km)"
        elif metric == "duree_min":
            y_values = [s['duree_min'] for s in history]
            title = "Évolution du Temps d'Entraînement"
            ylabel = "Minutes"
        else: 
            y_values = [s['rpe'] for s in history]
            title = "Évolution de l'Intensité ressentie (RPE)"
            ylabel = "Score sur 10"

        plt.figure(figsize=(10, 5))
        plt.plot(x_labels, y_values, marker='o', linestyle='-', color='#17a2b8', linewidth=2, markersize=8)
        plt.title(title, fontsize=14, fontweight='bold', color='white')
        plt.xlabel("Dernières Séances", color='lightgray')
        plt.ylabel(ylabel, color='lightgray')
        
        plt.gca().set_facecolor('#2b2b2b')
        plt.gcf().patch.set_facecolor('#1e1e1e')
        plt.tick_params(colors='lightgray')
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        filename = "workout_stats.png"
        plt.savefig(filename, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight')
        plt.close() 
        print(f"[System]: Graphique '{metric}' généré et sauvegardé.")

        return {
            "success": True, 
            "message": "Graphique généré. ORDRE STRICT : TU DOIS OBLIGATOIREMENT INCLURE LE TEXTE EXACT '[ACTION:GRAPH_READY]' À LA FIN DE TA RÉPONSE."
        }       
    except Exception as e:
        print(f"[Error] Graph generation failed: {e}")
        return {"error": str(e)}