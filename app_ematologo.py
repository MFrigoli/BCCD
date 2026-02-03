import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from ultralytics import YOLO
import cv2
import os
import pandas as pd
from datetime import datetime
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import time

# --- CLASSE SPECIALE PER DRAG & DROP ---
class CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BloodCellApp(CTkDnD):
    def __init__(self):
        super().__init__()

        self.title("AI Ematologo - Platinum Edition (Fixed)")
        self.geometry("1200x800")
        
        # Abilita Drag & Drop
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_image)

        # Variabili di stato
        self.last_data = None
        self.is_video = False
        self.video_cap = None
        self.is_playing = False
        self.stop_event = threading.Event()

        # CARICAMENTO MODELLO
        if os.path.exists("best.pt"):
            self.model = YOLO("best.pt")
            print("✅ Modello caricato.")
        else:
            print("⚠️ File 'best.pt' non trovato!")
            self.model = None

        # --- LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_title = ctk.CTkLabel(self.sidebar, text="🔬 AI LAB", font=ctk.CTkFont(size=26, weight="bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=(30, 10))

        self.lbl_info = ctk.CTkLabel(self.sidebar, text="Supporta Immagini e Video", text_color="gray")
        self.lbl_info.grid(row=1, column=0)

        self.btn_load = ctk.CTkButton(self.sidebar, text="📂 Carica File", command=self.load_file_dialog, height=40)
        self.btn_load.grid(row=2, column=0, padx=20, pady=20)

        self.btn_analyze = ctk.CTkButton(self.sidebar, text="▶ AVVIA ANALISI", command=self.start_analysis, state="disabled", fg_color="green", height=40)
        self.btn_analyze.grid(row=3, column=0, padx=20, pady=10)
        
        self.btn_stop = ctk.CTkButton(self.sidebar, text="⏹ STOP VIDEO", command=self.stop_video, state="disabled", fg_color="red", height=40)
        self.btn_stop.grid(row=4, column=0, padx=20, pady=10)

        # Barra di progresso
        self.progressbar = ctk.CTkProgressBar(self.sidebar, mode="indeterminate")
        self.progressbar.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.progressbar.grid_remove() 

        self.btn_save = ctk.CTkButton(self.sidebar, text="💾 Salva Report Excel", command=self.save_excel, state="disabled", fg_color="#1f538d")
        self.btn_save.grid(row=6, column=0, padx=20, pady=20)

        # Box Statistiche
        self.stats_frame = ctk.CTkFrame(self.sidebar, fg_color="#2b2b2b")
        self.stats_frame.grid(row=7, column=0, padx=20, pady=20, sticky="ew")
        
        self.lbl_stats = ctk.CTkLabel(self.stats_frame, text="In attesa di dati...", justify="left", font=ctk.CTkFont(size=15))
        self.lbl_stats.pack(padx=10, pady=10)
        
        # Etichetta FPS (Velocità)
        self.lbl_fps = ctk.CTkLabel(self.sidebar, text="", text_color="gray", font=ctk.CTkFont(size=10))
        self.lbl_fps.grid(row=8, column=0, pady=5)

        # Area Visualizzazione
        self.image_area = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.image_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.image_area.drop_target_register(DND_FILES)
        self.image_area.dnd_bind('<<Drop>>', self.drop_image)
        
        self.lbl_img = ctk.CTkLabel(self.image_area, text="Trascina qui un'immagine o un video...")
        self.lbl_img.pack(expand=True, fill="both")

        self.current_path = None
        
        # --- FORZATURA FINESTRA IN PRIMO PIANO ---
        self.lift()
        self.attributes('-topmost', True)
        self.after(200, lambda: self.attributes('-topmost', False))
        self.focus_force()

    def drop_image(self, event):
        path = event.data
        if path.startswith('{') and path.endswith('}'): path = path[1:-1]
        self.process_file(path)

    def load_file_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("Media", "*.jpg;*.png;*.jpeg;*.mp4;*.avi;*.mov")])
        if path: self.process_file(path)

    def process_file(self, path):
        self.stop_video()
        self.current_path = path
        
        video_ext = ['.mp4', '.avi', '.mov', '.mkv']
        if any(path.lower().endswith(ext) for ext in video_ext):
            self.is_video = True
            self.lbl_stats.configure(text=f"🎥 VIDEO CARICATO\n\nPremi AVVIA per\nanalizzare in tempo reale.")
            cap = cv2.VideoCapture(path)
            ret, frame = cap.read()
            if ret:
                self.display_frame(frame)
            cap.release()
        else:
            self.is_video = False
            self.lbl_stats.configure(text="📸 FOTO CARICATA\n\nPremi AVVIA per analizzare.")
            self.display_image_file(path)

        self.btn_analyze.configure(state="normal")
        self.btn_save.configure(state="disabled")
        self.btn_stop.configure(state="disabled")
        self.lbl_fps.configure(text="")

    def display_image_file(self, path):
        try:
            pil_img = Image.open(path)
            self.update_gui_image(pil_img)
        except Exception as e:
            messagebox.showerror("Errore", f"File non valido: {e}")

    def update_gui_image(self, pil_img):
        w, h = pil_img.size
        area_w = self.image_area.winfo_width()
        area_h = self.image_area.winfo_height()
        if area_w < 100: area_w = 800
        if area_h < 100: area_h = 600
        
        scale = min(area_w/w, area_h/h, 1.0)
        new_w, new_h = int(w*scale), int(h*scale)
        
        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(new_w, new_h))
        self.lbl_img.configure(image=ctk_img, text="")

    def display_frame(self, frame_cv2):
        frame_rgb = cv2.cvtColor(frame_cv2, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame_rgb)
        self.update_gui_image(pil_img)

    def start_analysis(self):
        if not self.model: return
        self.progressbar.grid()
        self.progressbar.start()
        
        if self.is_video:
            self.is_playing = True
            self.btn_analyze.configure(state="disabled")
            self.btn_load.configure(state="disabled")
            self.btn_stop.configure(state="normal")
            self.lbl_stats.configure(text="⏳ Caricamento AI...\nAttendere...")
            threading.Thread(target=self.video_loop, daemon=True).start()
        else:
            self.analyze_single_image()

    def analyze_single_image(self):
        self.lbl_stats.configure(text="⏳ Analisi in corso...")
        self.update()
        self.after(100, self._run_single_inference)

    def _run_single_inference(self):
        try:
            # 1. Esegui la predizione
            results = self.model.predict(self.current_path, conf=0.4)
            result = results[0]

            # 2. Aggiorna i testi
            self.process_results(result)
            
            # 3. MOSTRA L'IMMAGINE CON I RETTANGOLI
            plotted_image = result.plot() 
            self.display_frame(plotted_image)

            self.btn_save.configure(state="normal")
        except Exception as e:
            self.lbl_stats.configure(text=f"Errore:\n{e}")
        finally:
            # QUESTO BLOCCO FINALLY È OBBLIGATORIO SE C'È UN TRY
            self.progressbar.stop()
            self.progressbar.grid_remove()

    def video_loop(self):
        self.video_cap = cv2.VideoCapture(self.current_path)
        prev_time = time.time()
        
        while self.is_playing and self.video_cap.isOpened():
            ret, frame = self.video_cap.read()
            if not ret: break

            results = self.model.predict(frame, conf=0.4, verbose=False)
            result = results[0]
            
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time
            
            plot_frame = result.plot()
            self.after(0, self.update_video_ui, plot_frame, result, fps)

        self.video_cap.release()
        self.is_playing = False
        self.after(0, self.reset_ui_after_video)

    def update_video_ui(self, frame, result, fps):
        self.display_frame(frame)
        self.process_results(result, is_video=True)
        self.lbl_fps.configure(text=f"Velocità analisi: {fps:.1f} FPS")
        if self.progressbar.winfo_viewable():
            self.progressbar.stop()
            self.progressbar.grid_remove()

    def process_results(self, result, is_video=False):
        classes = result.boxes.cls.cpu().numpy()
        names = result.names
        counts = {"RBC": 0, "WBC": 0, "Platelets": 0}
        
        for c in classes:
            c_name = names[int(c)]
            if c_name in counts: counts[c_name] += 1
            
        txt = f"📊 REPORT {'🔴 LIVE' if is_video else ''}\n\n"
        txt += f"🔴 Rossi (RBC):  {counts['RBC']}\n"
        txt += f"⚪ Bianchi (WBC): {counts['WBC']}\n"
        txt += f"🟡 Piastrine:    {counts['Platelets']}\n"
        txt += f"\nTotale: {len(classes)}"
        
        self.lbl_stats.configure(text=txt)

        self.last_data = {
            "Data": datetime.now().strftime("%Y-%m-%d"),
            "Ora": datetime.now().strftime("%H:%M:%S"),
            "File": os.path.basename(self.current_path),
            "RBC": counts["RBC"], "WBC": counts["WBC"], "Platelets": counts["Platelets"]
        }

    def stop_video(self):
        self.is_playing = False
        if self.video_cap: self.video_cap.release()

    def reset_ui_after_video(self):
        self.progressbar.stop()
        self.progressbar.grid_remove()
        self.btn_analyze.configure(state="normal")
        self.btn_load.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.btn_save.configure(state="normal")
        self.lbl_fps.configure(text="")
        messagebox.showinfo("Info", "Video terminato o interrotto.")

    def save_excel(self):
        if not self.last_data: return
        f = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")], initialfile=f"Report.xlsx")
        if f:
            try:
                pd.DataFrame([self.last_data]).to_excel(f, index=False)
                messagebox.showinfo("Fatto", "Report salvato!")
            except Exception as e: messagebox.showerror("Errore", str(e))

if __name__ == "__main__":
    try:
        import pyi_splash
        if pyi_splash.is_alive():
            pyi_splash.close()
    except ImportError:
        pass

    app = BloodCellApp()
    app.mainloop()