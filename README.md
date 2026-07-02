# AURACLE - Hybrid AI Assistant & System Manager

Auracle is an autonomous artificial intelligence agent designed for workflow automation, productivity management, and Game Design assistance. Conceived as a true personal assistant, it listens, analyzes, and interacts directly with the user's environment (OS, Web, Notion databases).

The architecture relies on a smart hybrid router: it deploys a local neural network for PC requests (Edge Computing) and seamlessly switches to Groq's cloud API for ultra-fast execution of complex agentic tasks.

## Key Features

Auracle is structured around several modules (Tools) that the AI can chain autonomously (Chain of Thought):

* Hybrid Architecture (The Router): A Flask server that routes requests. Local Mode (Ollama) for privacy, Cloud Mode (Groq) for speed.
* Game Design & Creativity: 
  * Reads and analyzes the Game Design Document (GDD) on Notion to understand existing mechanics and hierarchies.
  * Saves design ideas on the fly (Character Design, Environment, Systems).
* Project Management (To-Do): Creates, reads, and updates tasks and subtasks directly integrated into Notion.
* Fitness Coach & Statistics: Logs workout sessions, calculates performances, and generates graphs (matplotlib) displayed live on the interface.
* Web Scraper & Search: Can search on DuckDuckGo, open links, and scrape HTML content (BeautifulSoup) to analyze complete technical documentations.
* System Monitoring: Real-time monitoring of RAM, CPU, and disk space of the host system (psutil).

## Tech Stack

* Language: Python 3.12+
* Interface (Front-end): CustomTkinter (Modern OS Dashboard)
* Server (Back-end): Flask
* LLM Models: 
  * Llama 3.3 70B (via Groq API) for ultra-fast analysis of complex requests.
  * Llama 3.2 (via Ollama) for local execution on the CPU/NPU.
* Tools & Libraries: notion-client, requests, duckduckgo-search, matplotlib, edge-tts, beautifulsoup4.

## Installation & Configuration

### 1. System Requirements
* Python installed on the host machine.
* Ollama installed for local mode (run `ollama run llama3.2` after installation).
* A Groq API key (console.groq.com).
* A Notion integration with access to your databases.

### 2. Environment
NOTION_TOKEN=your_notion_secret_token
NOTION_DATABASE_ID=todo_database_id
NOTION_SPORT_DATABASE_ID=sport_database_id
NOTION_GDD_PAGE_ID=main_gdd_page_id
GROQ_API_KEY=gsk_your_groq_key

### 3. Usage
python3 auracle_server.py

python3 auracle_app.py

