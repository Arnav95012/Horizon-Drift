import os
import subprocess
import urllib.request
import zipfile
import io
import shutil
from PyQt5.QtCore import QThread, pyqtSignal
import minecraft_launcher_lib
from core.config import config

class MinecraftLauncherThread(QThread):
    progress_update = pyqtSignal(int, int) # max, current
    status_update = pyqtSignal(str)
    error_update = pyqtSignal(str)
    
    def __init__(self, installation, account):
        super().__init__()
        self.installation = installation
        self.account = account
        
        # Base shared directory for assets/versions
        global_dir = config.get("game_directory")
        if global_dir and os.path.isdir(global_dir):
            self.shared_directory = global_dir
        else:
            self.shared_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
            
        # Specific game directory for this installation (for mods, saves, configs)
        custom_dir = self.installation.get("custom_dir")
        self.game_directory = custom_dir if custom_dir else self.shared_directory

    def run(self):
        mc_version = self.installation.get("version", "1.20.4")
        env_type = self.installation.get("type", "vanilla")
        self.status_update.emit(f"Preparing {env_type.capitalize()} {mc_version}...")
        
        callback = {
            "setStatus": lambda text: self.status_update.emit(text),
            "setProgress": lambda value: self.progress_update.emit(self.max_progress, value),
            "setMax": lambda value: setattr(self, 'max_progress', value)
        }
        self.max_progress = 100
        
        try:
            # Check for Java executable FIRST, as Forge installer needs it
            java_path = minecraft_launcher_lib.utils.get_java_executable()
            if not java_path or not os.path.exists(str(java_path)):
                # Try to find it in common locations
                common_paths = [
                    r"C:\Program Files\Java\jre1.8.0_301\bin\java.exe",
                    r"C:\Program Files (x86)\Minecraft Launcher\runtime\jre-x64\bin\java.exe",
                    r"C:\Program Files\Eclipse Adoptium\jdk-17.0.8.101-hotspot\bin\java.exe",
                    r"C:\Program Files\Java\jre-1.8\bin\java.exe",
                    r"C:\Program Files\Java\jdk-17\bin\java.exe"
                ]
                for p in common_paths:
                    if os.path.exists(p):
                        java_path = p
                        break
                else:
                    self.error_update.emit("Java not found! Please install Java (JRE 8 for 1.8.9, JDK 17+ for newer).")
                    return
            
            launch_version_id = mc_version
            
            if env_type == "fabric":
                self.status_update.emit("Installing Fabric...")
                minecraft_launcher_lib.fabric.install_fabric(mc_version, self.shared_directory, callback=callback)
                # Find the installed fabric version
                for v in minecraft_launcher_lib.utils.get_installed_versions(self.shared_directory):
                    if "fabric" in v["id"] and mc_version in v["id"]:
                        launch_version_id = v["id"]
                        break
            elif env_type == "forge":
                self.status_update.emit("Installing Forge...")
                # Forge installation requires java to run the installer jar
                minecraft_launcher_lib.forge.install_forge_version(mc_version, self.shared_directory, callback=callback, java=java_path)
                
                # Find the installed forge version
                for v in minecraft_launcher_lib.utils.get_installed_versions(self.shared_directory):
                    if "forge" in v["id"] and mc_version in v["id"]:
                        launch_version_id = v["id"]
                        break
            else:
                self.status_update.emit("Installing Vanilla...")
                minecraft_launcher_lib.install.install_minecraft_version(
                    versionid=mc_version, 
                    minecraft_directory=self.shared_directory, 
                    callback=callback
                )
            
            self.status_update.emit("Building launch command...")
            
            # Parse JVM args from config
            jvm_args_str = config.get("jvm_arguments")
            jvm_args = jvm_args_str.split() if jvm_args_str else []
            
            # Add RAM allocation (use installation specific RAM if available)
            ram_mb = self.installation.get("ram_mb", config.get("ram_mb"))
            jvm_args.insert(0, f"-Xmx{ram_mb}M")
            
            # Ely.by: redirect Minecraft's auth/session API to Ely.by servers
            # Without this, Minecraft contacts Mojang's session server and fails,
            # which causes multiplayer to appear grayed out even with a valid Ely.by token
            account_type = self.account.get("type", "offline")
            if account_type == "elyby":
                jvm_args += [
                    "-Dminecraft.api.auth.host=https://authserver.ely.by/auth",
                    "-Dminecraft.api.account.host=https://account.ely.by",
                    "-Dminecraft.api.session.host=https://session.ely.by",
                    "-Dminecraft.api.services.host=https://api.ely.by",
                ]
            
            # Mesa3D Injection for Win7/Old Intel HD
            if config.get("use_mesa3d"):
                mesa_dir = os.path.join(self.shared_directory, "mesa3d")
                os.makedirs(mesa_dir, exist_ok=True)
                mesa_dll = os.path.join(mesa_dir, "opengl32.dll")
                
                if not os.path.exists(mesa_dll):
                    self.status_update.emit("Downloading Mesa3D OpenGL driver...")
                    try:
                        # Reliable mirror for Mesa3D Windows 64-bit
                        url = "https://github.com/mmozeiko/build-mesa/releases/download/21.2.5/mesa-21.2.5-win64.zip"
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        resp = urllib.request.urlopen(req)
                        with zipfile.ZipFile(io.BytesIO(resp.read())) as z:
                            with open(mesa_dll, "wb") as f:
                                f.write(z.read("opengl32.dll"))
                    except Exception as e:
                        self.status_update.emit(f"Mesa3D Download Failed: {e}")
                
                if os.path.exists(mesa_dll):
                    jvm_args.append(f"-Dorg.lwjgl.opengl.libname={mesa_dll}")
            
            # Setup launch options
            account_type = self.account.get("type", "offline")
            
            # Determine userType: Microsoft = "msa", Ely.by/offline = "legacy"
            # Without "legacy" for non-MSA accounts, Minecraft disables multiplayer
            if account_type == "microsoft":
                user_type = "msa"
            else:
                user_type = "legacy"
            
            # Token must be a non-empty string — Minecraft rejects blank tokens
            # For offline/ely.by a placeholder is fine; Ely.by provides a real token
            token = self.account.get("token") or "0" * 32
            
            options = {
                "username": self.account.get("username", "Player"),
                "uuid": self.account.get("uuid", ""),
                "token": token,
                "userType": user_type,
                "jvmArguments": jvm_args,
                "launcherName": "Horizon-Drift",
                "launcherVersion": "1.0",
                "gameDirectory": self.game_directory,
                "executablePath": java_path
            }
            
            command = minecraft_launcher_lib.command.get_minecraft_command(
                version=launch_version_id, 
                minecraft_directory=self.shared_directory, 
                options=options
            )
            
            self.status_update.emit("Launching Minecraft...")
            # Hide console window on Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(command, startupinfo=startupinfo, cwd=self.game_directory)
            
            # Wait for game to close
            process.wait()
            self.status_update.emit("Game closed.")
            
        except Exception as e:
            self.error_update.emit(str(e))
