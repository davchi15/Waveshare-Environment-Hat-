import tkinter as tk
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import board
import busio
import random

# --- 1. SENSOR LIBRARIES ---
try:
    import adafruit_ltr390
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False

# --- 2. COLOR PALETTE ---
COLORS = {
    "background": "#080808",
    "card":       "#121212",
    "border":     "#222222",
    "text_main":  "#ffffff",
    "text_dim":   "#555555",
    "uvi":        "#b82ce3", # Bright Purple
    "uvs":        "#8b5cf6", # Soft Violet
}

class SensorManager:
    def __init__(self):
        self.active = False
        if HARDWARE_AVAILABLE:
            try:
                self.i2c = busio.I2C(board.SCL, board.SDA)
                # Initialize LTR390 at the specified I2C address
                self.uv_sensor = adafruit_ltr390.LTR390(self.i2c, address=0x53)
                self.active = True
            except Exception as e:
                print(f"Hardware initialization failed: {e}")

    def read_uv(self):
        if not self.active:
            # Simulated idle data for testing without the sensor connected
            return round(random.uniform(4.0, 4.5), 2), random.randint(300, 320)
        
        # Read strictly UV data from LTR390
        uvi = self.uv_sensor.uvi     # UV Index
        uvs = self.uv_sensor.uvs     # Raw UV counts (280nm - 430nm)
        
        return round(uvi, 2), int(uvs)

class SensorCard(ctk.CTkFrame):
    def __init__(self, master, title, unit, color, icon):
        super().__init__(master, fg_color=COLORS["card"], corner_radius=15, 
                         border_width=1, border_color=COLORS["border"])
        
        self.history = [0.0] * 50
        self.smooth_val = 0.0
        self.smoothness = 0.2

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 0))
        
        ctk.CTkLabel(header, text=icon, text_color=color, font=("Arial", 20)).pack(side="left")
        ctk.CTkLabel(header, text=title.upper(), text_color=COLORS["text_dim"], 
                     font=("Impact", 12)).pack(side="left", padx=10)

        # Scaled up font for the 2-panel layout
        self.val_text = ctk.CTkLabel(self, text="--", text_color=COLORS["text_main"], 
                                     font=("Arial", 72, "bold"))
        self.val_text.pack(pady=(25, 0))
        
        ctk.CTkLabel(self, text=unit.upper(), text_color=COLORS["text_dim"], 
                     font=("Arial", 10, "bold")).pack()

        # Scaled up graph size
        self.figure = Figure(figsize=(5, 3), facecolor=COLORS["card"])
        self.subplot = self.figure.add_subplot(111)
        self.subplot.set_facecolor(COLORS["card"])
        
        for s in self.subplot.spines.values(): s.set_visible(False)
        self.subplot.tick_params(colors=COLORS["text_dim"], labelsize=8, length=0)
        self.subplot.grid(True, color="#1e1e1e", linewidth=0.5)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(15, 20))
        
        # Thicker line for better visibility
        self.line, = self.subplot.plot(self.history, color=color, linewidth=3.0)

    def update_display(self, new_value):
        self.smooth_val += (new_value - self.smooth_val) * self.smoothness
        self.history.append(self.smooth_val)
        self.history.pop(0)
        
        self.val_text.configure(text=str(new_value))
        self.line.set_ydata(self.history)
        self.subplot.relim()
        self.subplot.autoscale_view()
        self.canvas.draw()

class UVDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LTR390 Ultraviolet Telemetry")
        # Adjusted aspect ratio for a wider, 2-panel layout
        self.geometry("1100x600")
        self.configure(fg_color=COLORS["background"])

        self.hardware = SensorManager()

        ctk.CTkLabel(self, text="// LTR390-UV-1 SPECTROMETER ONLINE", 
                    text_color=COLORS["text_dim"], font=("Courier", 12)).pack(pady=20)

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # 1x2 Grid Setup
        grid.grid_columnconfigure((0, 1), weight=1)
        grid.grid_rowconfigure(0, weight=1)

        # Initialize only the 2 UV data panels
        self.uvi_card = SensorCard(grid, "UV Index", "UVI", COLORS["uvi"], "🟣")
        self.uvs_card = SensorCard(grid, "Raw UV", "Counts (280-430nm)", COLORS["uvs"], "🔬")

        self.uvi_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.uvs_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        self.run_update_loop()

    def run_update_loop(self):
        uvi, uvs = self.hardware.read_uv()
        
        self.uvi_card.update_display(uvi)
        self.uvs_card.update_display(uvs)
        
        self.after(1000, self.run_update_loop)

if __name__ == "__main__":
    app = UVDashboard()
    app.mainloop()
