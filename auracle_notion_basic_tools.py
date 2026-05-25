import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=NOTION_TOKEN)

def add_todo_notion(task_title, priority="Medium"):
    """
    Creates a new task in the specified Notion database.
    This function will serve as a 'Tool' for your future AI Agent.
    """
    try:
        new_page = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": task_title
                            }
                        }
                    ]
                },
                "Priority": {
                    "select": {
                        "name": priority
                    }
                },
                "Status": {
                    "status": {
                        "name": "Not started"
                    }
                }
            }
        )
        print(f"[Auracle]: Task '{task_title}' successfully added to Notion!")
        return new_page
    except Exception as e:
        print(f"[Error] Failed to add task to Notion: {e}")
        return None

def fetch_active_todos():
    """
    Fetches all active tasks (To Do or In Progress) from the Notion database.
    """
    try:
        db_info = notion.databases.retrieve(database_id=DATABASE_ID)
        data_source_id = db_info["data_sources"][0]["id"]
        
        response = notion.data_sources.query(
            data_source_id=data_source_id,
            filter={
                "property": "Status",
                "status": {
                    "does_not_equal": "Done"
                }
            }
        )
        
        tasks = []
        for page in response.get("results", []):
            page_id = page["id"]
            
            title_props = page["properties"].get("Name", {}).get("title", [])
            title = title_props[0]["text"]["content"] if title_props else "Untitled"
            
            status = page["properties"].get("Status", {}).get("status", {}).get("name", "Unknown")
            
            tasks.append({"id": page_id, "title": title, "status": status})
            
        print(f"[System]: Auracle fetched {len(tasks)} active tasks.")
        return tasks
    except Exception as e:
        print(f"[Error] Failed to fetch tasks: {e}")
        return {"error": str(e)}

def update_todo_status(page_id, new_status="Done"):
    """
    Updates the status of a specific task in Notion using its page_id.
    """
    try:
        notion.pages.update(
            page_id=page_id,
            properties={
                "Status": {
                    "status": {
                        "name": new_status
                    }
                }
            }
        )
        print(f"[System]: Task updated to '{new_status}'.")
        return {"success": True, "new_status": new_status}
    except Exception as e:
        print(f"[Error] Failed to update task: {e}")
        return {"error": str(e)}
    
def create_subtask(parent_page_id, subtask_title, priority="Medium"):
    """
    Creates a subtask linked to a parent task in Notion.
    Crucial for breaking down complex game mechanics into a hierarchy.
    """
    try:
        new_page = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {
                    "title": [{"text": {"content": subtask_title}}]
                },
                "Status": {
                    "status": {"name": "To-do"} 
                },
                "Priority": {
                    "select": {"name": priority}
                },
                "Parent Task": {
                    "relation": [{"id": parent_page_id}]
                }
            }
        )
        print(f"[System]: Subtask '{subtask_title}' created and linked to parent.")
        return {"success": True, "subtask_id": new_page["id"]}
    except Exception as e:
        print(f"[Error] Failed to create subtask: {e}")
        return {"error": str(e)}
    
