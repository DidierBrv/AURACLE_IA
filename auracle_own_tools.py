import psutil

def check_system_health():
    """
    Vérifie l'état de santé actuel de l'ordinateur (CPU, RAM, Disque).
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        
        status = {
            "CPU_Usage_Percent": cpu_usage,
            "RAM_Usage_Percent": ram_usage,
            "Disk_Usage_Percent": disk_usage,
            "Warning": "Alerte ! RAM presque saturée." if ram_usage > 90 else "Système stable."
        }
        
        print(f"[System]: Check-up matériel effectué.")
        return status
    except Exception as e:
        return {"error": str(e)}