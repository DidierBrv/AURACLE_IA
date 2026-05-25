from duckduckgo_search import DDGS

def search_the_web(query, max_results=3):
    """
    Effectue une recherche sur internet et renvoie les meilleurs résultats.
    Outil indispensable pour débugger du code, lire de la documentation ou trouver des tutoriels.
    """
    try:
        print(f"[Internet]: Recherche en cours pour -> '{query}'")
        
        results = DDGS().text(query, max_results=max_results)
        
        if not results:
            return {"message": "Je n'ai trouvé aucun résultat pertinent sur le web pour cette recherche."}
        
        formatted_results = "Voici les résultats de la recherche Web :\n\n"
        for i, res in enumerate(results):
            formatted_results += f"--- Résultat {i+1} ---\n"
            formatted_results += f"Titre : {res.get('title')}\n"
            formatted_results += f"Lien : {res.get('href')}\n"
            formatted_results += f"Extrait : {res.get('body')}\n\n"
            
        print(f"[Internet]: {len(results)} résultats trouvés.")
        
        return {"web_search_results": formatted_results}
        
    except Exception as e:
        print(f"[Error] Web search failed: {e}")
        return {"error": f"La recherche a échoué : {str(e)}"}