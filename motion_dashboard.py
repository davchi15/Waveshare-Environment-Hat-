import tkinter as tk
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import board
import busio
from adafruit_icm20x import ICM20948 as ICM_Sensor

# --- EXACT VIDEO COLOR PALETTE ---
COLORS = {
    "bg": "#000000",
    "card": "#050505",
    "border": "#1a1a1a",
    "header_green": "#00FF00", # Pure Green
    "title_tilt": "#FFFF00",   # Pure Yellow
    "title_cyan": "#00FFFF",   # Pure Cyan
    "title_pink": "#FF00FF",   # Pure Magenta
    "text_main": "#ffffff",    # Default Values
    "accent_green": "#00FF00", # Pure Green for the Globe Dot
    "flash_bg": "#3a0000"      # Deep red for impact flash
}

class NewtonianEngine:
    def __init__(self):
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.icm = ICM_Sensor(self.i2c, address=0x68)
            self.active = True
        except Exception as e:
            print(f"Motion Sensor Error: {e}")
            self.active = False

    def get_telemetry(self):
        if not self.active: 
            # Simulated idle data for testing without the HAT connected
            return -0.05, +0.35, 0.98, +0.6, 368.3
        
        ax, ay, az = self.icm.acceleration
        gx, gy, gz = self.icm.gyro # Degrees per second
        mx, my, mz = self.icm.magnetic
        
        # Calculate raw telemetry
        total_g = np.sqrt(ax**2 + ay**2 + az**2) / 9.806
        tilt_x = ax / 9.806
        tilt_y = ay / 9.806
        mag_strength = np.sqrt(mx**2 + my**2 + mz**2)
        
        return tilt_x, tilt_y, total_g, gz, mag_strength

class MotionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ICM20948 Newtonian Engine")
        self.geometry("850x900")
        self.configure(fg_color=COLORS["bg"])
        
        # Initialize the hardware engine
        self.engine = NewtonianEngine()
        
        # 1. Header
        ctk.CTkLabel(self, text="PHYSICS & INERTIA ENGINE", 
                     font=("Impact", 40), text_color=COLORS["header_green"]).pack(pady=(40, 10))

        # 2. 3D Globe Visualization
        self.fig = Figure(figsize=(5, 5), facecolor=COLORS["bg"])
        
        # Remove all padding to make the globe bigger
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor(COLORS["bg"])
        self.ax.axis('off') 
        
        # Lock limits to exactly the sphere size to maximize zoom
        self.ax.set_xlim([-1, 1])
        self.ax.set_ylim([-1, 1])
        self.ax.set_zlim([-1, 1])
        
        # --- RECOVERED 7-LINE GLOBE GRAPHIC ---
        t = np.linspace(0, 2 * np.pi, 100)
        
        # Line 1: Equator (Horizontal line)
        self.ax.plot(np.cos(t), np.zeros_like(t), np.sin(t), color="#1a1a1a", linewidth=1.5)
        
        # Lines 2-7: Meridians (Outer circle, Vertical line, and the 4 curves)
        for angle in [0, 30, 60, 90]:
            rad = np.radians(angle)
            x = np.sin(t) * np.cos(rad)
            y = np.cos(t)
            z = np.sin(t) * np.sin(rad)
            self.ax.plot(x, y, z, color="#1a1a1a", linewidth=1.5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(pady=5)
        
        # Draw the dynamic 3D Vector Line and the Dot
        self.vector_line, = self.ax.plot([0, 0], [0, 0], [0, 1], color=COLORS["accent_green"], linewidth=2)
        self.vector_dot, = self.ax.plot([0], [0], [1], color=COLORS["accent_green"], 
                                        marker='o', markersize=12, 
                                        markeredgecolor="white", markeredgewidth=1, linestyle="None")

        # Set fixed viewing angle looking perfectly top-down
        self.ax.view_init(elev=90, azim=-90)

        # 3. Telemetry Grid
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="x", padx=30, pady=20)
        self.grid_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        # --- UPDATED TITLES AND COLORS ---
        self.tilt_val  = self.make_stat_box("TILT (STATIC G)", 0, COLORS["accent_green"])
        self.force_val = self.make_stat_box("TOTAL FORCE (Gs)", 1, COLORS["title_tilt"])
        self.rot_val   = self.make_stat_box("ROTATION (DPS)", 2, COLORS["title_cyan"])
        self.mag_val   = self.make_stat_box("MAG STRENGTH (uT)", 3, COLORS["title_pink"]) # Removed 4th arg so value defaults to white

        # 4. Status Bottom Label
        self.status_lbl = ctk.CTkLabel(self, text="STABLE INERTIA", 
                                       font=("Courier", 20, "bold"), 
                                       text_color=COLORS["text_main"])
        self.status_lbl.pack(pady=20)

        self.update_loop()

    def make_stat_box(self, title, col, title_color, val_color="#ffffff"):
        box = ctk.CTkFrame(self.grid_frame, fg_color=COLORS["card"], 
                           border_width=1, border_color=COLORS["border"], corner_radius=2)
        box.grid(row=0, column=col, padx=4, sticky="nsew")
        
        ctk.CTkLabel(box, text=title, font=("Arial", 10, "bold"), 
                     text_color=title_color).pack(pady=(12, 0))
        
        lbl = ctk.CTkLabel(box, text="0.00", font=("Arial", 18, "bold"), 
                           text_color=val_color)
        lbl.pack(pady=(5, 15))
        return lbl

    def update_loop(self):
        tx, ty, g, rot, mag = self.engine.get_telemetry()
        
        # 1. Update 3D Globe Vector 
        gx = np.clip(tx, -1.0, 1.0)
        # Corrected inversion so physical tilt matches visual movement
        gy = np.clip(-ty, -1.0, 1.0) 
        gz = np.sqrt(max(0, 1 - gx**2 - gy**2)) 
        
        # Update both the line array (origin to point) and the dot array (just the point)
        self.vector_line.set_data_3d([0, gx], [0, gy], [0, gz])
        self.vector_dot.set_data_3d([gx], [gy], [gz])
        
        # 2. Update Data Strings
        self.tilt_val.configure(text=f"X: {tx:+.2f}\nY: {ty:+.2f}")
        self.force_val.configure(text=f"{g:.2f} G")
        self.rot_val.configure(text=f"{rot:+.1f}°/s")
        self.mag_val.configure(text=f"{mag:.1f}")
        
        # 3. Status & Impact Flash Logic
        is_impact = abs(g - 1.0) > 0.4 or abs(rot) > 20.0
        
        if is_impact:
            self.configure(fg_color=COLORS["flash_bg"]) 
            self.status_lbl.configure(text="KINETIC DISRUPTION", text_color="#ff4444")
        else:
            self.configure(fg_color=COLORS["bg"])       
            self.status_lbl.configure(text="STABLE INERTIA", text_color=COLORS["text_main"])
        
        self.canvas.draw_idle()
        self.after(50, self.update_loop)

if __name__ == "__main__":
    app = MotionApp()
    app.mainloop()
