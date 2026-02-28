import customtkinter as ctk
import subprocess
import sys
import os

# --- COLOR PALETTE ---
COLORS = {
    "bg": "#050505",
    "card": "#121212",
    "border": "#222222",
    "text_main": "#ffffff",
    "text_dim": "#888888",
    "motion": "#00FF00",  # Neon Green
    "env": "#00FFFF",     # Cyan
    "uv": "#b82ce3"       # Purple
}

class DashboardLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Waveshare Telemetry Suite")
        self.geometry("500x550")
        self.configure(fg_color=COLORS["bg"])

        # Header
        ctk.CTkLabel(self, text="TELEMETRY SUITE", font=("Impact", 36), 
                     text_color=COLORS["text_main"]).pack(pady=(40, 5))
        ctk.CTkLabel(self, text="SELECT A SUBSYSTEM TO INITIALIZE", font=("Courier", 12), 
                     text_color=COLORS["text_dim"]).pack(pady=(0, 30))

        # Launch Buttons - UPDATED WITH YOUR EXACT FILENAMES
        self.create_launch_button("PHYSICS & INERTIA ENGINE", "motion_dashboard.py", COLORS["motion"], "🌐")
        self.create_launch_button("ENVIRONMENT TELEMETRY", "dashboard.py", COLORS["env"], "🌡️")
        self.create_launch_button("ULTRAVIOLET SPECTROMETER", "UV Light dashboard.py", COLORS["uv"], "🟣")

        # Footer
        ctk.CTkLabel(self, text="SYSTEM READY", font=("Courier", 10, "bold"), 
                     text_color=COLORS["text_dim"]).pack(side="bottom", pady=20)

    def create_launch_button(self, title, filename, accent_color, icon):
        btn_frame = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=10,
                                 border_width=1, border_color=COLORS["border"])
        btn_frame.pack(fill="x", padx=40, pady=10)

        # Container for layout
        container = ctk.CTkFrame(btn_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Icon and Title
        ctk.CTkLabel(container, text=icon, font=("Arial", 24), text_color=accent_color).pack(side="left")
        ctk.CTkLabel(container, text=title, font=("Impact", 16), text_color=COLORS["text_main"]).pack(side="left", padx=15)

        # Launch Action Button
        launch_btn = ctk.CTkButton(container, text="LAUNCH", font=("Arial", 12, "bold"),
                                   fg_color="transparent", border_width=1, border_color=accent_color,
                                   text_color=accent_color, hover_color="#1a1a1a", width=80,
                                   command=lambda f=filename: self.launch_script(f))
        launch_btn.pack(side="right")

    def launch_script(self, filename):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if os.path.exists(script_path):
            print(f"Initializing {filename}...")
            # Popen runs the script as a separate process so the launcher doesn't freeze
            subprocess.Popen([sys.executable, script_path])
        else:
            print(f"ERROR: Could not find '{filename}' in the current directory.")

if __name__ == "__main__":
    app = DashboardLauncher()
    app.mainloop()
