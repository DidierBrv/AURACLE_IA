import os
import time
import threading
import queue
import requests
import random
import customtkinter as ctk
from PIL import Image

import auracle_ears
from auracle_ears import listen_to_user

SERVER_URL = "http://127.0.0.1:5000/ask"
VOICE_NAME = "fr-FR-VivienneNeural"

command_queue = queue.Queue()
ui_queue = queue.Queue()
log_queue = queue.Queue()

AWAKE_DURATION = 30
awake_until = 0
mic_enabled = True
speaker_enabled = True

def voice_worker():
    global awake_until, mic_enabled
    wake_words = ["auracle", "oracle", "oracles", "miracle", "au racle", "orakel"]
    
    while True:
        if not mic_enabled:
            time.sleep(0.5)
            continue
        text = listen_to_user()
        if not text:
            time.sleep(0.5)
            continue
        if not mic_enabled:
            continue

        log_queue.put(f"[Micro] Capté : '{text}'")
        
        mot_cle_trouve = next((mot for mot in wake_words if mot in text), None)
        current_time = time.time()
        is_awake = current_time < awake_until

        if mot_cle_trouve:
            awake_until = time.time() + AWAKE_DURATION
            clean_text = text.replace(mot_cle_trouve, "Auracle").strip()
            if clean_text:
                command_queue.put(("Voix", clean_text))
            else:
                ui_queue.put(("Système", "Oui ? Je t'écoute..."))
        elif is_awake:
            awake_until = time.time() + AWAKE_DURATION
            command_queue.put(("Voix", text))

def play_audio(text, filename="temp_response.mp3"):
    global speaker_enabled, awake_until
    if not speaker_enabled: return
    try:
        auracle_ears.ignore_audio = True 
        clean_text = text.replace('"', "'").replace("\n", " ")
        clean_text = clean_text.replace("*", "").replace("#", "").replace("_", "")
        os.system(f'edge-tts --voice {VOICE_NAME} --text "{clean_text}" --write-media {filename}')
        if os.path.exists(filename) and speaker_enabled:
            os.system(f'mpg123 -q {filename}')
    except Exception as e:
        log_queue.put(f"[Erreur Audio] : {e}")
    finally:
        if os.path.exists(filename):
            try: os.remove(filename)
            except: pass
        auracle_ears.ignore_audio = False
        awake_until = time.time() + AWAKE_DURATION

def network_worker():
    human_fillers = ["Ok c'est en cours...", "Laisse-moi réfléchir...", "Voyons voir...", "Je regarde ça..."]
    while True:
        source, command = command_queue.get()
        ui_queue.put((source, command))
        
        filler = random.choice(human_fillers)
        ui_queue.put(("Auracle", f"*{filler}*"))
        threading.Thread(target=play_audio, args=(filler, "temp_filler.mp3"), daemon=True).start()
        
        try:
            log_queue.put(f"[HTTP POST] Envoi vers {SERVER_URL}")
            response = requests.post(SERVER_URL, json={"message": command, "client_type": "pc"})
            data = response.json()
            
            if response.status_code == 200:
                reply = data.get("reply", "")
                
                if "[ACTION:GRAPH_READY]" in reply:
                    reply = reply.replace("[ACTION:GRAPH_READY]", "").strip()
                    ui_queue.put(("SYSTEM_GRAPH", ""))
                
                ui_queue.put(("Auracle", reply))
                log_queue.put("[HTTP 200] Réponse reçue avec succès.")
                threading.Thread(target=play_audio, args=(reply, "temp_response.mp3"), daemon=True).start()
            else:
                error_msg = data.get("error", "Erreur inconnue")
                ui_queue.put(("Erreur Serveur", error_msg))
                log_queue.put(f"[HTTP ERREUR] {error_msg}")
        except Exception as e:
            ui_queue.put(("Erreur Réseau", str(e)))
            log_queue.put(f"[ERREUR CRITIQUE] {e}")

threading.Thread(target=voice_worker, daemon=True).start()
threading.Thread(target=network_worker, daemon=True).start()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.title("Auracle - Dashboard OS")
app.geometry("900x650")

app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

sidebar_frame = ctk.CTkFrame(app, corner_radius=0, fg_color="#1E1E1E")
sidebar_frame.grid(row=0, column=0, sticky="nsew")
sidebar_frame.grid_rowconfigure(5, weight=1)

title_label = ctk.CTkLabel(sidebar_frame, text="AURACLE", font=("Inter", 24, "bold"), text_color="#E0E0E0")
title_label.grid(row=0, column=0, padx=20, pady=(20, 30))

def select_frame(name):
    chat_frame.grid_forget()
    stats_frame.grid_forget()
    logs_frame.grid_forget()
    
    btn_chat.configure(fg_color="#333333" if name == "chat" else "transparent")
    btn_stats.configure(fg_color="#333333" if name == "stats" else "transparent")
    btn_logs.configure(fg_color="#333333" if name == "logs" else "transparent")
    
    if name == "chat": chat_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
    elif name == "stats": stats_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
    elif name == "logs": logs_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

btn_chat = ctk.CTkButton(sidebar_frame, text="💬 Assistant", anchor="w", fg_color="transparent", font=("Inter", 15), command=lambda: select_frame("chat"))
btn_chat.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

btn_stats = ctk.CTkButton(sidebar_frame, text="📊 Stats Sport", anchor="w", fg_color="transparent", font=("Inter", 15), command=lambda: select_frame("stats"))
btn_stats.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

btn_logs = ctk.CTkButton(sidebar_frame, text="🛠️ Logs Système", anchor="w", fg_color="transparent", font=("Inter", 15), command=lambda: select_frame("logs"))
btn_logs.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

status_label = ctk.CTkLabel(sidebar_frame, text="🔴 Veille", font=("Inter", 14, "bold"))
status_label.grid(row=6, column=0, pady=(10, 5))

def toggle_mic():
    global mic_enabled
    mic_enabled = not mic_enabled
    mic_btn.configure(text="🎙️ Mic", fg_color="#28a745") if mic_enabled else mic_btn.configure(text="🔇 Mute", fg_color="#dc3545")

def toggle_speaker():
    global speaker_enabled
    speaker_enabled = not speaker_enabled
    if speaker_enabled: speaker_btn.configure(text="🔊 Voix", fg_color="#17a2b8")
    else:
        speaker_btn.configure(text="🔈 Mute", fg_color="#6c757d")
        os.system("pkill mpg123")

mic_btn = ctk.CTkButton(sidebar_frame, text="🎙️ Mic", fg_color="#28a745", font=("Inter", 14, "bold"), command=toggle_mic)
mic_btn.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
speaker_btn = ctk.CTkButton(sidebar_frame, text="🔊 Voix", fg_color="#17a2b8", font=("Inter", 14, "bold"), command=toggle_speaker)
speaker_btn.grid(row=8, column=0, padx=20, pady=(5, 20), sticky="ew")
chat_frame = ctk.CTkFrame(app, fg_color="transparent")
chat_frame.grid_columnconfigure(0, weight=1)
chat_frame.grid_rowconfigure(0, weight=1)
chat_box = ctk.CTkTextbox(chat_frame, font=("Inter", 14), wrap="word", fg_color="#2B2B2B", border_width=1, border_color="#333333")
chat_box.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
chat_box.insert("0.0", "Bienvenue sur le Dashboard. L'assistant est en ligne.\n\n")
chat_box.configure(state="disabled")
entry_field = ctk.CTkEntry(chat_frame, height=45, font=("Inter", 14), placeholder_text="Tape une commande ici...")
entry_field.grid(row=1, column=0, sticky="ew", padx=(0, 10))

def send_text_command(event=None):
    text = entry_field.get()
    if text.strip():
        command_queue.put(("Clavier", text))
        entry_field.delete(0, "end")
entry_field.bind("<Return>", send_text_command)

send_btn = ctk.CTkButton(chat_frame, text="Envoyer", width=100, height=45, font=("Inter", 14, "bold"), command=send_text_command)
send_btn.grid(row=1, column=1)
stats_frame = ctk.CTkFrame(app, fg_color="transparent")
stats_frame.grid_columnconfigure(0, weight=1)
stats_frame.grid_rowconfigure(1, weight=1)
ctk.CTkLabel(stats_frame, text="Analytiques Sportives", font=("Inter", 20, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 15))
graph_label = ctk.CTkLabel(stats_frame, text="Générez un graphique en le demandant à l'IA.")
graph_label.grid(row=1, column=0, sticky="nsew")
current_graph_image = None

def load_graph_image():
    """Charge l'image sauvegardée par le serveur dans l'interface."""
    global current_graph_image
    if os.path.exists("workout_stats.png"):
        try:
            with Image.open("workout_stats.png") as img:
                current_graph_image = ctk.CTkImage(light_image=img.copy(), size=(700, 350))
                
            graph_label.configure(image=current_graph_image, text="")
            log_queue.put("[Système] Image du graphique chargée avec succès.")
        except Exception as e:
            log_queue.put(f"[Erreur Image] : {e}")

logs_frame = ctk.CTkFrame(app, fg_color="transparent")
logs_frame.grid_columnconfigure(0, weight=1)
logs_frame.grid_rowconfigure(1, weight=1)
ctk.CTkLabel(logs_frame, text="Console Système", font=("Inter", 20, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 15))
logs_box = ctk.CTkTextbox(logs_frame, font=("Consolas", 12), fg_color="#1E1E1E", text_color="#A9B7C6")
logs_box.grid(row=1, column=0, sticky="nsew")
logs_box.configure(state="disabled")

def process_queues():
    while not ui_queue.empty():
        sender, message = ui_queue.get()
        if sender == "SYSTEM_GRAPH":
            load_graph_image()
            select_frame("stats")
        else:
            chat_box.configure(state="normal")
            chat_box.insert("end", f"[{sender}] : {message}\n\n")
            chat_box.see("end")
            chat_box.configure(state="disabled")
            
    while not log_queue.empty():
        log_msg = log_queue.get()
        logs_box.configure(state="normal")
        logs_box.insert("end", f"{log_msg}\n")
        logs_box.see("end")
        logs_box.configure(state="disabled")

    if not mic_enabled:
        status_label.configure(text="🔇 Micro Coupé", text_color="#dc3545")
    elif time.time() < awake_until:
        status_label.configure(text="🟢 Écoute...", text_color="#28a745")
    else:
        status_label.configure(text="🔴 Veille", text_color="#6c757d")
        
    app.after(100, process_queues)

select_frame("chat")
app.after(100, process_queues)
app.mainloop()