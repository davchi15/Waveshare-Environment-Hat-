import tkinter as tk
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import board
import busio

# --- 1. SENSOR LIBRARIES ---
try:
    from adafruit_bme280 import basic as adafruit_bme280 # For Temp/Hum at 0x76
    import adafruit_sgp40       # Air Quality (VOC) at 0x59
    import adafruit_tsl2591     # Light (Lux) at 0x29
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
    "temp":       "#d24c34", # Red
    "hum":        "#28bcdc", # Blue
    "voc":        "#8dba76", # Green
    "lux":        "#debf17"  # Yellow
}

class SensorManager:
    def __init__(self):
        self.active = False
        if HARDWARE_AVAILABLE:
            try:
                self.i2c = busio.I2C(board.SCL, board.SDA)
                # Initialize using the addresses found in your i2cdetect
                self.bme_sensor = adafruit_bme280.Adafruit_BME280_I2C(self.i2c, address=0x76)
                self.lux_sensor = adafruit_tsl2591.TSL2591(self.i2c)
                
                # SGP40 might not appear until initialized/warmed up
                try:
                    self.voc_sensor = adafruit_sgp40.SGP40(self.i2c)
                except:
                    self.voc_sensor = None
                    print("VOC Sensor not detected at 0x59")
                
                self.active = True
            except Exception as e:
                print(f"Hardware initialization failed: {e}")

    def read_all(self):
        if not self.active:
            return 22.5, 45.0, 100, 350.0 
        
        # Read from BME280
        t = self.bme_sensor.temperature
        h = self.bme_sensor.relative_humidity
        
        # Read VOC (using T and H for compensation)
        if self.voc_sensor:
            v = self.voc_sensor.measure_index(temperature=t, relative_humidity=h)
        else:
            v = 0
            
        # Read Light
        l = self.lux_sensor.lux
        
        return round(t, 1), round(h, 1), int(v), round(l, 1)

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

        self.val_text = ctk.CTkLabel(self, text="--", text_color=COLORS["text_main"], 
                                     font=("Arial", 64, "bold"))
        self.val_text.pack(pady=(15, 0))
        
        ctk.CTkLabel(self, text=unit.upper(), text_color=COLORS["text_dim"], 
                     font=("Arial", 9, "bold")).pack()

        self.figure = Figure(figsize=(4, 2), facecolor=COLORS["card"])
        self.subplot = self.figure.add_subplot(111)
        self.subplot.set_facecolor(COLORS["card"])
        
        for s in self.subplot.spines.values(): s.set_visible(False)
        self.subplot.tick_params(colors=COLORS["text_dim"], labelsize=7, length=0)
        self.subplot.grid(True, color="#1e1e1e", linewidth=0.5)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(10, 15))
        
        self.line, = self.subplot.plot(self.history, color=color, linewidth=2.5)

    def update_display(self, new_value):
        self.smooth_val += (new_value - self.smooth_val) * self.smoothness
        self.history.append(self.smooth_val)
        self.history.pop(0)
        
        self.val_text.configure(text=str(new_value))
        self.line.set_ydata(self.history)
        self.subplot.relim()
        self.subplot.autoscale_view()
        self.canvas.draw()

class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Waveshare Environment Telemetry")
        self.geometry("1100x850")
        self.configure(fg_color=COLORS["background"])

        self.hardware = SensorManager()

        ctk.CTkLabel(self, text="// SYSTEM TELEMETRY ONLINE", 
                    text_color=COLORS["text_dim"], font=("Courier", 12)).pack(pady=20)

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        grid.grid_columnconfigure((0, 1), weight=1)
        grid.grid_rowconfigure((0, 1), weight=1)

        self.temp = SensorCard(grid, "Temperature", "Celsius", COLORS["temp"], "🌡")
        self.hum  = SensorCard(grid, "Humidity", "Relative %", COLORS["hum"], "💧")
        self.voc  = SensorCard(grid, "Air Quality", "VOC Index", COLORS["voc"], "🌿")
        self.lux  = SensorCard(grid, "Brightness", "Lux", COLORS["lux"], "☀️")

        self.temp.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.hum.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.voc.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.lux.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")

        self.run_update_loop()

    def run_update_loop(self):
        t, h, v, l = self.hardware.read_all()
        self.temp.update_display(t)
        self.hum.update_display(h)
        self.voc.update_display(v)
        self.lux.update_display(l)
        self.after(1000, self.run_update_loop)

if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()
