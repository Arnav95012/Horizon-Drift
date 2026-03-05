import json
import os
import psutil

def get_appdata_dir():
    appdata = os.getenv('APPDATA')
    if not appdata:
        appdata = os.path.expanduser("~")
    config_dir = os.path.join(appdata, "Horizon-Drift")
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

CONFIG_FILE = os.path.join(get_appdata_dir(), "horizon_config.json")

def get_total_ram_mb():
    return int(psutil.virtual_memory().total / (1024 * 1024))

DEFAULT_CONFIG = {
    "ram_mb": min(4096, get_total_ram_mb() // 2),  # Default to half of system RAM or 4GB
    "game_directory": "",  # Empty means default OS directory
    "jvm_arguments": "-XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M",
    "use_mesa3d": False,
    "installations": [
        {"id": "default", "name": "Latest Release", "type": "vanilla", "version": "1.21.11", "ram_mb": min(4096, get_total_ram_mb() // 2)}
    ],
    "selected_installation": "default",
    "accounts": [],
    "selected_account_index": -1
}

class ConfigManager:
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
                    
                    # Migration: Update old default 1.20.4 to 1.21.11
                    needs_save = False
                    for inst in self.config.get("installations", []):
                        if inst.get("id") == "default" and inst.get("version") == "1.20.4":
                            inst["version"] = "1.21.11"
                            needs_save = True
                    
                    if needs_save:
                        self.save()
                        
            except Exception as e:
                print(f"Failed to load config: {e}")

    def save(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()

# Global instance
config = ConfigManager()
