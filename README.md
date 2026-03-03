## Horizon Glint

Horizon Glint is a high-performance, minimalist Minecraft Java launcher designed to provide a seamless, "enchanted" gateway to your game worlds. Built with a focus on aesthetic clarity and technical efficiency, it bridges the gap between complex mod management and a clean, modern user interface.

**Link to project:** [http://recruiters-love-seeing-live-demos.com/](http://recruiters-love-seeing-live-demos.com/)

---

## How It's Made:

**Tech used:** Python 3.8, PySide6/PyQt5, Google AI Studio (Gemini 3.1 Pro Preview)

This project was developed using a **vibe-coding** workflow within **Google AI Studio**. By focusing on the high-level logic and the specific "shimmer" aesthetic I wanted to achieve, I used AI to help architect a robust backend in **Python 3.8**. The goal was to create a tool that felt as powerful as an enchanted item in-game, handling complex tasks like Ely.By authentication and automated asset downloading without the typical overhead found in bulkier launchers.

The front end utilizes a highly customized UI layer to achieve the signature "Glint" effect—a subtle, shifting purple gradient that identifies the active instance. By using Python for the core logic, I was able to keep the codebase clean and maintainable while ensuring deep integration with system-level file operations.

---

## Optimizations

Horizon Glint is engineered to be **extremely lightweight**. By utilizing **Python 3.8** and optimizing the way the application handles sub-processes, I ensured the launcher has a minimal memory footprint, leaving more resources available for the game itself.

Key technical optimizations include:

* 
**Zero-Bloat Architecture:** Unlike Electron-based launchers that bundle a full browser, this Python implementation stays under **50MB of RAM** during idle.


* 
**Asynchronous Version Parsing:** I refactored the directory scanning logic to run asynchronously, allowing the UI to remain fully responsive while the launcher verifies hundreds of local game files.


* 
**Smart JVM Injection:** The launcher dynamically calculates the best heap size and garbage collection flags for your specific hardware, significantly reducing "stutter" during Minecraft gameplay.

---
