import socket
import threading
import time
import json
import os
import numpy as np
import cv2
import bettercam
import customtkinter as ctk
from PIL import Image, ImageDraw
import pystray

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "wled_masterpiece_config.json"

class LightRow(ctk.CTkFrame):
    """Enthusiast-grade configuration row with Dynamic Matrix Dimension Allocators"""
    def __init__(self, master, index, delete_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.index = index
        self.delete_callback = delete_callback

        self.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # Node ID
        self.label = ctk.CTkLabel(self, text=f"Node #{index}:", font=ctk.CTkFont(weight="bold"))
        self.label.grid(row=0, column=0, padx=4, pady=5, sticky="w")

        # Network Target
        self.ip_entry = ctk.CTkEntry(self, placeholder_text="IP / Hostname", width=110)
        self.ip_entry.insert(0, f"192.168.1.{50 + index}")
        self.ip_entry.grid(row=0, column=1, padx=4, pady=5, sticky="ew")

        # Layout Mapping profile
        self.type_dropdown = ctk.CTkOptionMenu(
            self, 
            values=["Matrix (Custom)", "Strip (Top Edge)", "Strip (Bottom Edge)", "Strip (Left Edge)", "Strip (Right Edge)", "Strip (Whole Screen)"],
            width=130,
            command=self.toggle_layout_mode
        )
        self.type_dropdown.grid(row=0, column=2, padx=4, pady=5, sticky="ew")

        # Matrix Width Frame/Input
        self.width_entry = ctk.CTkEntry(self, placeholder_text="W", width=40)
        self.width_entry.insert(0, "16")
        self.width_entry.grid(row=0, column=3, padx=2, pady=5, sticky="ew")

        # Matrix Height Frame/Input
        self.height_entry = ctk.CTkEntry(self, placeholder_text="H", width=40)
        self.height_entry.insert(0, "8")
        self.height_entry.grid(row=0, column=4, padx=2, pady=5, sticky="ew")

        # Hardware Array Constraints / LED Count
        self.led_entry = ctk.CTkEntry(self, placeholder_text="LEDs", width=50)
        self.led_entry.insert(0, "128")
        self.led_entry.grid(row=0, column=5, padx=4, pady=5, sticky="ew")

        # RGB Hardware Balance Calibration Profile
        self.calib_entry = ctk.CTkEntry(self, placeholder_text="R,G,B Balance", width=85)
        self.calib_entry.insert(0, "1.0,1.0,1.0")
        self.calib_entry.grid(row=0, column=6, padx=4, pady=5, sticky="ew")

        if index > 1:
            self.delete_btn = ctk.CTkButton(self, text="❌", width=25, fg_color="#C0392B", hover_color="#922B21", command=self.delete_self)
            self.delete_btn.grid(row=0, column=7, padx=4, pady=5)

        self.toggle_layout_mode("Matrix (Custom)")

    def toggle_layout_mode(self, choice):
        if "Matrix" in choice:
            self.width_entry.configure(state="normal")
            self.height_entry.configure(state="normal")
            self.led_entry.configure(state="disabled") 
            self.update_matrix_led_count()
            self.width_entry.bind("<KeyRelease>", lambda e: self.update_matrix_led_count())
            self.height_entry.bind("<KeyRelease>", lambda e: self.update_matrix_led_count())
        else:
            self.width_entry.configure(state="disabled")
            self.height_entry.configure(state="disabled")
            self.led_entry.configure(state="normal")

    def update_matrix_led_count(self):
        try:
            w = int(self.width_entry.get().strip())
            h = int(self.height_entry.get().strip())
            total = w * h
            self.led_entry.configure(state="normal")
            self.led_entry.delete(0, "end")
            self.led_entry.insert(0, str(total))
            self.led_entry.configure(state="disabled")
        except ValueError:
            pass

    def delete_self(self):
        self.delete_callback(self)


class WLEDMasterpieceSuite(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WLED Masterpiece Ambient Engine")
        self.geometry("780x750")
        
        self.is_syncing = False
        self.sync_thread = None
        self.camera = bettercam.create()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.light_rows = []
        self.next_index = 1
        self.tray_icon = None

        self.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)

        # UI Layout
        self.title_label = ctk.CTkLabel(self, text="🏆 WLED Masterpiece Suite", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Hardware Deployment Matrix")
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.add_button = ctk.CTkButton(self, text="➕ Link New Hardware Node", fg_color="#2E4053", hover_color="#212F3D", command=self.add_light_row)
        self.add_button.pack(pady=5)

        self.tuning_frame = ctk.CTkFrame(self)
        self.tuning_frame.pack(pady=10, fill="x", padx=20)
        
        self.gamma_label = ctk.CTkLabel(self.tuning_frame, text="Color Curve (Gamma Correction): 1.6")
        self.gamma_label.pack(anchor="w", padx=10, pady=2)
        self.gamma_slider = ctk.CTkSlider(self.tuning_frame, from_=1.0, to=3.0, number_of_steps=20, command=self.update_gamma_label)
        self.gamma_slider.set(1.6)
        self.gamma_slider.pack(fill="x", padx=10, pady=5)

        self.smooth_label = ctk.CTkLabel(self.tuning_frame, text="Temporal Processing Smoothing: 20%")
        self.smooth_label.pack(anchor="w", padx=10, pady=2)
        self.smooth_slider = ctk.CTkSlider(self.tuning_frame, from_=5, to=100, number_of_steps=19, command=self.update_smooth_label)
        self.smooth_slider.set(20)
        self.smooth_slider.pack(fill="x", padx=10, pady=5)

        self.crop_var = ctk.StringVar(value="on")
        self.crop_check = ctk.CTkCheckBox(self.tuning_frame, text="Enable Smart Cinematic Black-Bar Deflection (Auto-Crop)", variable=self.crop_var, onvalue="on", offvalue="off")
        self.crop_check.pack(anchor="w", padx=10, pady=8)

        self.sync_button = ctk.CTkButton(self, text="ENGAGE AMBIENT ENGINE", fg_color="green", hover_color="darkgreen", font=ctk.CTkFont(size=16, weight="bold"), height=45, command=self.toggle_sync)
        self.sync_button.pack(pady=15, padx=20, fill="x")

        self.status_label = ctk.CTkLabel(self, text="Status: Inactive", text_color="gray")
        self.status_label.pack(side="bottom", pady=5)

        self.load_configuration()

    def update_gamma_label(self, value):
        self.gamma_label.configure(text=f"Color Curve (Gamma Correction): {value:.1f}")

    def update_smooth_label(self, value):
        self.smooth_label.configure(text=f"Temporal Processing Smoothing: {int(value)}%")

    def add_light_row(self, ip_val=None, type_val=None, w_val="16", h_val="8", led_val="128", calib_val=None):
        row = LightRow(self.scroll_frame, self.next_index, self.remove_light_row)
        row.pack(fill="x", pady=5, padx=5)
        
        if ip_val: row.ip_entry.delete(0, "end"); row.ip_entry.insert(0, ip_val)
        if type_val: row.type_dropdown.set(type_val); row.toggle_layout_mode(type_val)
        
        row.width_entry.delete(0, "end"); row.width_entry.insert(0, str(w_val))
        row.height_entry.delete(0, "end"); row.height_entry.insert(0, str(h_val))
        
        if type_val and "Matrix" not in type_val:
            row.led_entry.configure(state="normal")
            row.led_entry.delete(0, "end")
            row.led_entry.insert(0, str(led_val))
        else:
            row.update_matrix_led_count()

        if calib_val: row.calib_entry.delete(0, "end"); row.calib_entry.insert(0, calib_val)
        
        self.light_rows.append(row)
        self.next_index += 1

    def remove_light_row(self, row_to_remove):
        row_to_remove.pack_forget()
        self.light_rows.remove(row_to_remove)
        row_to_remove.destroy()

    def save_configuration(self):
        config_data = {
            "gamma": self.gamma_slider.get(),
            "smoothing": self.smooth_slider.get(),
            "autocrop": self.crop_var.get(),
            "devices": []
        }
        for row in self.light_rows:
            config_data["devices"].append({
                "ip": row.ip_entry.get(),
                "type": row.type_dropdown.get(),
                "width": row.width_entry.get(),
                "height": row.height_entry.get(),
                "led_count": row.led_entry.get(),
                "calibration": row.calib_entry.get()
            })
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=4)

    def load_configuration(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                self.gamma_slider.set(data.get("gamma", 1.6))
                self.smooth_slider.set(data.get("smoothing", 20))
                self.crop_var.set(data.get("autocrop", "on"))
                self.update_gamma_label(self.gamma_slider.get())
                self.update_smooth_label(self.smooth_slider.get())
                
                for dev in data.get("devices", []):
                    self.add_light_row(
                        dev["ip"], dev["type"], 
                        dev.get("width", "16"), dev.get("height", "8"), 
                        dev["led_count"], dev.get("calibration", "1.0,1.0,1.0")
                    )
            except Exception:
                self.setup_defaults()
        else:
            self.setup_defaults()

    def setup_defaults(self):
        self.add_light_row(None, "Matrix (Custom)", "16", "8", "128", "1.0,1.0,1.0")
        self.add_light_row(None, "Strip (Top Edge)", "1", "1", "11", "1.0,1.0,1.0")

    def minimize_to_tray(self):
        self.withdraw()
        if not self.tray_icon:
            icon_img = Image.new('RGB', (64, 64), color=(24, 28, 36))
            d = ImageDraw.Draw(icon_img)
            d.ellipse([(14, 14), (50, 50)], fill=(230, 126, 34))
            
            menu = pystray.Menu(
                pystray.MenuItem("Open Configuration Console", self.restore_from_tray, default=True),
                pystray.MenuItem("Kill Broadcast Engine", self.close_app_completely)
            )
            self.tray_icon = pystray.Icon("wled_masterpiece", icon_img, "WLED Masterpiece Suite", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self, icon, item):
        self.tray_icon.stop()
        self.tray_icon = None
        self.deiconify()

    def close_app_completely(self, icon=None, item=None):
        self.is_syncing = False
        self.save_configuration()
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()
        os._exit(0)

    def toggle_sync(self):
        if not self.is_syncing:
            self.save_configuration()
            self.is_syncing = True
            self.sync_button.configure(text="SHUTDOWN PIPELINE ENGINE", fg_color="red", hover_color="darkred")
            self.status_label.configure(text="Status: Core Broadcasting Active", text_color="green")
            
            self.add_button.configure(state="disabled")
            for row in self.light_rows:
                row.ip_entry.configure(state="disabled")
                row.type_dropdown.configure(state="disabled")
                row.width_entry.configure(state="disabled")
                row.height_entry.configure(state="disabled")
                row.calib_entry.configure(state="disabled")

            # Take a thread-safe snapshot of all items right here on the main UI thread before spawning the stream loop
            self.safe_device_snapshot = []
            for row in self.light_rows:
                raw_ip = row.ip_entry.get().strip()
                try:
                    resolved_ip = socket.gethostbyname(raw_ip)
                except Exception:
                    resolved_ip = raw_ip

                try:
                    rgb_scales = [float(x) for x in row.calib_entry.get().split(",")]
                    if len(rgb_scales) != 3: rgb_scales = [1.0, 1.0, 1.0]
                except Exception:
                    rgb_scales = [1.0, 1.0, 1.0]

                try:
                    w_val = int(row.width_entry.get().strip())
                    h_val = int(row.height_entry.get().strip())
                    led_val = int(row.led_entry.get().strip())
                except ValueError:
                    w_val, h_val, led_val = 16, 8, 128

                self.safe_device_snapshot.append({
                    "ip": resolved_ip,
                    "type": row.type_dropdown.get(),
                    "width": w_val,
                    "height": h_val,
                    "led_count": led_val,
                    "scale": np.array(rgb_scales),
                    "prev_color": np.array([0.0, 0.0, 0.0])
                })

            self.sync_thread = threading.Thread(target=self.broadcast_loop, daemon=True)
            self.sync_thread.start()
        else:
            self.is_syncing = False
            self.sync_button.configure(text="ENGAGE AMBIENT ENGINE", fg_color="green", hover_color="darkgreen")
            self.status_label.configure(text="Status: Stopped", text_color="gray")
            
            self.add_button.configure(state="normal")
            for row in self.light_rows:
                row.ip_entry.configure(state="normal")
                row.type_dropdown.configure(state="normal")
                row.calib_entry.configure(state="normal")
                row.toggle_layout_mode(row.type_dropdown.get())

    def broadcast_loop(self):
        UDP_PORT = 21324

        def get_gamma_lut(gamma_val):
            inv_gamma = 1.0 / gamma_val
            return np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")

        while self.is_syncing:
            frame = self.camera.grab()
            if frame is None: continue

            # Get UI slider values safely
            try:
                gamma_val = self.gamma_slider.get()
                alpha = self.smooth_slider.get() / 100.0
                crop_active = (self.crop_var.get() == "on")
            except Exception:
                gamma_val, alpha, crop_active = 1.6, 0.2, True

            lut = get_gamma_lut(gamma_val)
            frame = cv2.LUT(frame, lut)
            height, width, _ = frame.shape

            if crop_active:
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                row_means = np.mean(gray, axis=1)
                th_black = 12
                non_black_rows = np.where(row_means > th_black)[0]
                if len(non_black_rows) > 0:
                    top_bound = non_black_rows[0]
                    bottom_bound = non_black_rows[-1]
                    if (bottom_bound - top_bound) > (height * 0.4):
                        frame = frame[top_bound:bottom_bound, 0:width]
                        height, width, _ = frame.shape

            zones = {
                "Strip (Whole Screen)": frame,
                "Strip (Top Edge)": frame[0:int(height * 0.12), 0:width],
                "Strip (Bottom Edge)": frame[int(height * 0.88):height, 0:width],
                "Strip (Left Edge)": frame[0:height, 0:int(width * 0.12)],
                "Strip (Right Edge)": frame[int(width * 0.88):width, 0:height]
            }
            cached_averages = {}

            # Read exclusively from our safe snapshot snapshot array
            for dev in self.safe_device_snapshot:
                packet = bytearray([2, 2])
                dtype = dev["type"]
                
                if "Matrix" in dtype:
                    matrix_img = cv2.resize(frame, (dev["width"], dev["height"]), interpolation=cv2.INTER_AREA)
                    for row_pixels in matrix_img:
                        for pixel in row_pixels:
                            r = int(min(255, pixel[0] * dev["scale"][0]))
                            g = int(min(255, pixel[1] * dev["scale"][1]))
                            b = int(min(255, pixel[2] * dev["scale"][2]))
                            packet.extend([r, g, b])
                            
                else:
                    if dtype not in cached_averages:
                        cached_averages[dtype] = np.mean(zones[dtype], axis=(0, 1))
                    
                    target_color = cached_averages[dtype]
                    smoothed_color = (target_color * alpha) + (dev["prev_color"] * (1.0 - alpha))
                    dev["prev_color"] = smoothed_color
                    
                    r = int(min(255, smoothed_color[0] * dev["scale"][0]))
                    g = int(min(255, smoothed_color[1] * dev["scale"][1]))
                    b = int(min(255, smoothed_color[2] * dev["scale"][2]))
                    
                    for _ in range(dev["led_count"]):
                        packet.extend([r, g, b])

                try:
                    self.sock.sendto(packet, (dev["ip"], UDP_PORT))
                except Exception:
                    pass

            time.sleep(0.01)

if __name__ == "__main__":
    app = WLEDMasterpieceSuite()
    app.mainloop()