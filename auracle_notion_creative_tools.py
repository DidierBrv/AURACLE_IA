import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=NOTION_TOKEN)

GDD_PAGE_ID = os.getenv("NOTION_GDD_PAGE_ID")

def append_idea_to_gdd(idea_text):
    """
    Appends a new text block to a specific Notion page (like a Game Design Document).
    Perfect for capturing random ideas, mechanics, or drawing concepts.
    """
    try:
        notion.blocks.children.append(
            block_id=GDD_PAGE_ID,
            children=[
                {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [
                            {"type": "text", "text": {"content": idea_text}}
                        ],
                        "icon": {"emoji": "💡"}
                    }
                }
            ]
        )
        print(f"[System]: Idea appended to GDD.")
        return {"success": True, "message": "Idea securely stored in GDD."}
    except Exception as e:
        print(f"[Error] Failed to append idea: {e}")
        return {"error": str(e)}

def save_drawing_concept(concept_idea, category="Character Design"):
    """
    Sauvegarde une idée de dessin, de conception visuelle ou d'architecture système.
    Catégories possibles : Character Design, UI, Environnement, Architecture.
    """
    try:
        new_page = notion.pages.create(
            parent={"database_id": "TON_ID_DE_BASE_INSPIRATIONS"},
            properties={
                "Idée": {"title": [{"text": {"content": concept_idea}}]},
                "Catégorie": {"select": {"name": category}}
            }
        )
        print(f"[System]: Concept de '{category}' sauvegardé.")
        return {"success": True, "message": "Idée de conception sécurisée."}
    except Exception as e:
        print(f"[Error] Failed to save concept: {e}")
        return {"error": str(e)}
    
def read_notion_page(page_id=None):
    """
    Lit le contenu textuel d'une page Notion (par défaut le Game Design Document).
    Permet à l'IA d'analyser les systèmes de jeu, l'histoire ou les mécaniques existantes.
    """
    try:
        target_id = page_id if page_id else os.getenv("NOTION_GDD_PAGE_ID")
        
        response = notion.blocks.children.list(block_id=target_id)
        blocks = response.get('results', [])
        
        full_text = ""
        
        for block in blocks:
            block_type = block.get('type')
            
            valid_text_blocks = [
                'paragraph', 'heading_1', 'heading_2', 'heading_3', 
                'bulleted_list_item', 'numbered_list_item', 'callout', 'quote'
            ]
            
            if block_type in valid_text_blocks:
                rich_text = block.get(block_type, {}).get('rich_text', [])
                text_content = "".join([t.get('plain_text', '') for t in rich_text])
                
                if text_content:
                    full_text += text_content + "\n"
                    
        if not full_text.strip():
            return {"message": "La page est vide ou ne contient pas de texte lisible (que des images ou des bases de données)."}
            
        print(f"[System]: Auracle a lu la page Notion ({len(full_text)} caractères).")
        
        return {"page_content": full_text[:8000]} 
        
    except Exception as e:
        print(f"[Error] Failed to read Notion page: {e}")
        return {"error": str(e)}