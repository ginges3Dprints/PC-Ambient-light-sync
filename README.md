# 🏆 WLED Masterpiece Ambient Suite

An enthusiast-grade, ultra-low latency ambient desktop lighting synchronization engine written in Python. This suite captures your screen in real-time and broadcasts dynamic color data frames directly to **WLED-enabled hardware arrays** (LED strips and custom matrix panels) over UDP.

Designed for gamers and cinephiles who demand zero-lag performance, seamless color physics, and hardware flexibility.
WLED Masterpiece Suite is a high-performance Windows desktop ambient lighting controller designed to bridge the gap between your monitor and your room's physical environment. By utilizing the Windows Desktop Duplication API via BetterCam, it captures screen data with virtually zero CPU overhead, making it perfectly suited for high-frame-rate gaming.Unlike rigid commercial alternatives, this suite features a fully unlocked architecture—allowing users to define custom matrix grid dimensions ($W \times H$), map distinct spatial edge-sampling zones (Top, Bottom, Left, Right), calibrate independent hardware white balances, and automatically deflect cinematic letterbox black bars on the fly. It runs quietly in the system tray, automatically backing up your entire layout configuration to a local JSON file.
---
## 🗺️ Future Roadmap

We are actively pushing this suite to become the ultimate ambient lighting engine on the internet. Upcoming milestones include:
- [ ] **Standalone Installer:** Compiling into a single `.exe` via PyInstaller for zero-dependency execution.
- [ ] **Matrix Wiring Topologies:** Adding native support for Serpentine (Zig-Zag) physical matrix layouts directly via a GUI toggle.
- [ ] **Stream Deck Plugin:** Launching a dedicated plugin to toggle profiles and ignition switches via physical macro keys.
- [ ] **Visual Layout Mapping:** An interactive drag-and-drop desk layout canvas built directly into the CustomTkinter core dashboard.

## ✨ Key Features

* **⚡ Ultra-Fast Screen Capture:** Driven by `BetterCam` utilizing the Windows Desktop Duplication API (DXGI) for near-zero CPU overhead and maximum frame rates.
* **🧩 Dynamic Matrix Resizing:** Unlocked grid allocation allows you to input custom Width (`W`) and Height (`H`) dimensions directly in the GUI to support any size LED matrix panel.
* **📐 Advanced Spatial Edge Mapping:** Divide and conquer your desktop real estate. Assign specific hardware nodes to sample the **Top**, **Bottom**, **Left**, or **Right** edges, or the **Whole Screen**.
* **📺 Cinematic Black-Bar Deflection:** Automatically detects and dynamically crops out letterbox black bars from movies and cinematic 21:9 ultrawide games so your lighting never goes dark.
* **🎨 Per-Device Hardware Calibration:** Built-in RGB scaling entries allow you to fine-tune white balance individually per strip to match different LED manufacturing tints.
* **📈 Temporal Transition Smoothing:** Features an exponential low-pass filter slider to cushion aggressive frame color changes, eliminating harsh strobing and reducing eye strain.
* **🕶️ Background Stealth Mode:** Minimizes completely out of sight to the Windows System Tray (`pystray`) to stay out of your way while gaming.
* **💾 Architecture Auto-Saving:** Automatically backs up your entire complex desk network arrangement and custom calibration curves to a local JSON file on execution.

---
🚀 How To Use
Prep WLED: Ensure your ESP8266/ESP32 is turned on and connected to your network. Go to WLED Config -> Sync Interfaces, scroll down to Realtime UDP, check Receive UDP Realtime, and ensure the port is set to 21324.

Launch the Suite: Fire up the desktop application by running: python game_light_sync.py

Deploy Your Nodes: * Click ➕ Link New Hardware Node for every fixture on your desk.

Input either the device's network IP address or its mDNS address (e.g., wled-matrix.local).

Pick its profile alignment. If choosing Matrix (Custom), input your grid dimensions (e.g., 16 x 8).

Tweak & Calibrate: Move the sliders to adjust your personal Gamma curves and linear temporal smoothing weights. If an LED strip looks a little too green, dial back its calibration matrix to something like 1.0, 0.85, 1.0.

Ignition: Hit ENGAGE AMBIENT ENGINE and watch your room transform! Minimize the panel to let it run quietly in your system tray.

🛠️ Built With
CustomTkinter - Modern UI Design System

BetterCam - High-performance Windows Screen Duplication

OpenCV - Computer vision and color space manipulation matrix calculations

## ⚙️ Installation Requirements

### 1. Prerequisites
* **Operating System:** Windows 10 / 11 (Required for the `BetterCam` DXGI engine)
* **Python:** Python 3.10 or higher installed

### 2. Dependencies Setup
Clone this repository or download the source files into a folder. Open your command prompt/terminal inside that directory and execute:

```bash
pip install -r requirements.txt
