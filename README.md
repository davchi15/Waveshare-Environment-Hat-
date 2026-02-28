# 🚀 Waveshare Telemetry Suite for Raspberry Pi

A complete, dark-mode GUI telemetry suite for the Raspberry Pi. This suite visualizes real-time data from the Waveshare Environment HAT (featuring the ICM20948, BME280, SGP40, TSL2591, and LTR390-UV-1 sensors). 

Includes three distinct interactive dashboards and a master launcher menu.

**Target System:** Raspberry Pi OS (Bookworm/Bullseye)  
**Hardware:** Pi 5 / 4B / Zero 2W  

---

## 📂 Project Structure

To use the master launcher, ensure your files are downloaded and named exactly like this inside your project folder:
* `Master_Menu.py` (The main menu UI)
* `motion_dashboard.py` (The 3D Physics & Inertia Engine)
* `dashboard.py` (The 4-panel Temperature/Humidity/VOC/Light dashboard)
* `UV Light dashboard.py` (The 2-panel UV Index & Raw Counts dashboard)

---

## 🛠️ Hardware Requirements

* **Raspberry Pi** (Tested on Pi 4 / Pi 5)
* **Waveshare Environment HAT** (An all-in-one board providing Motion, Temp, Hum, VOC, Ambient Light, and UV tracking)

All sensors communicate via the I2C protocol. If wiring the HAT manually via jumper wires instead of seating it directly on the Pi's GPIO pins, connect them as follows: 
* **SDA** to Pin 3
* **SCL** to Pin 5
* **3V3** (Power) to Pin 1
* **GND** (Ground) to Pin 6

---

## ⚡ Quickstart Setup

### 1. Enable I2C on your Raspberry Pi
The sensors communicate over I2C, which is disabled by default on a fresh Raspberry Pi OS install. Open your terminal and run the configuration tool: 

```bash
sudo raspi-config
```
* Navigate to **Interface Options** -> **I2C**.
* Select **Yes** to enable. 
* Exit the config tool and reboot your Pi if prompted.

### 2. Install System Dependencies
The Python GUI framework (Tkinter) and the virtual environment manager require system-level packages to function. Run these commands to install them:

```bash
sudo apt update
sudo apt install python3-tk python3-venv i2c-tools -y
```

### 3. Verify Hardware Connections
Check that your Pi can successfully communicate with the sensors on the HAT:

```bash
i2cdetect -y 1
```
You should see a grid of numbers output in the terminal. Look for these specific hardware addresses to confirm your HAT is online:
* `0x68` (ICM20948 Motion)
* `0x76` (BME280 Temp/Humidity)
* `0x59` (SGP40 VOC)
* `0x53` (LTR390 UV)
* `0x29` (TSL2591 Light)

### 4. Create and Activate a Virtual Environment
Newer versions of Raspberry Pi OS require Python packages to be installed in a virtual environment to avoid system conflicts. Create your project folder and activate the environment:

```bash
mkdir telemetry-suite
cd telemetry-suite
python3 -m venv env
source env/bin/activate
```
*(Note: You must run `source env/bin/activate` anytime you open a new terminal window to work on or run this project).*

### 5. Install Python Dependencies
With your virtual environment active `(env)`, you can now install all required Python libraries. 

First, install the UI and Math frameworks (CustomTkinter, Matplotlib, and Numpy):
```bash
pip install customtkinter matplotlib numpy
```

Next, install the Adafruit hardware drivers necessary for the sensors to work:
```bash
pip install adafruit-blinka adafruit-circuitpython-icm20x adafruit-circuitpython-bme280 adafruit-circuitpython-sgp40 adafruit-circuitpython-tsl2591 adafruit-circuitpython-ltr390
```

### 6. Launch the Suite
Make sure all 4 of your Python files are placed inside the `telemetry-suite` folder you created in Step 4. Then, launch the master menu:

```bash
python Master_Menu.py
```
From the menu, click **LAUNCH** on any subsystem to open its live telemetry dashboard!
