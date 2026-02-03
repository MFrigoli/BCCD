Markdown
# 🔬 AI Ematologo - Blood Cell Detection & Counting

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![YOLOv8](https://img.shields.io/badge/AI-YOLOv8-green)
![Status](https://img.shields.io/badge/Status-Completed-success)

**AI Ematologo** è un'applicazione desktop avanzata basata su Computer Vision e Deep Learning progettata per rilevare e contare automaticamente le cellule del sangue da immagini microscopiche e flussi video.

Il software identifica tre classi principali utilizzando il dataset **BCCD**:
- 🔴 **RBC** (Globuli Rossi)
- ⚪ **WBC** (Globuli Bianchi)
- 🟡 **Platelets** (Piastrine)

---

## ✨ Funzionalità Principali

- **📸 Analisi Immagini:** Supporto per formati JPG, PNG, JPEG.
- **🎥 Analisi Video LIVE:** Rilevamento in tempo reale su file video (MP4, AVI) con indicatore FPS.
- **🖱️ Drag & Drop:** Trascina i file direttamente nell'interfaccia per caricarli.
- **📊 Export Dati:** Esportazione dei risultati del conteggio in formato **Excel (.xlsx)** con data e ora.
- **🎨 Interfaccia Moderna:** GUI realizzata con `CustomTkinter` (Dark Mode).
- **🚀 Splash Screen:** Schermata di caricamento professionale all'avvio.

---

## 🧠 Il Modello AI

Il "cervello" del progetto è un modello **YOLOv8 Nano** addestrato specificamente su immagini biomediche.

- **Dataset:** BCCD (Blood Cell Count and Detection).
- **Addestramento:** Eseguito su Google Colab (GPU T4).
- **Epoche:** 100 (con Early Stopping attivato per massima precisione).
- **Metriche:** mAP50 superiore al 94%.

---

## 🛠️ Installazione

Per eseguire il progetto sul tuo computer, segui questi passaggi:

1. **Clona la repository** (o scarica lo zip):
   ```bash
   git clone [https://github.com/TUO_USERNAME/AI-Ematologo.git](https://github.com/TUO_USERNAME/AI-Ematologo.git)
   cd AI-Ematologo
2.	Installa le dipendenze: Assicurati di avere Python installato, poi esegui:
Bash
pip install -r requirements.txt
3.	Verifica il modello: Assicurati che il file best.pt sia presente nella cartella principale del progetto.
________________________________________
🚀 Utilizzo
Avvia l'applicazione con il seguente comando:
Bash
python app_ematologo.py
1.	All'avvio vedrai lo splash screen.
2.	Trascina un'immagine o un video nell'area nera a destra.
3.	Premi "▶ AVVIA ANALISI".
4.	I risultati appariranno nella barra laterale.
5.	Premi "💾 Salva Report Excel" per scaricare i dati.
________________________________________
📂 Struttura del Progetto
Plaintext
📁 AI-Ematologo
│
├── app_ematologo.py   # Codice sorgente principale (GUI + Logica)
├── best.pt            # Modello YOLOv8 addestrato
├── splash.png         # Immagine di caricamento
├── requirements.txt   # Lista delle librerie necessarie
└── README.md          # Questo file
________________________________________
📦 Creare l'eseguibile (.exe)
Se vuoi convertire lo script in un programma Windows autonomo:
Bash
pyinstaller --noconfirm --onedir --windowed --name "EmatologoAI" --splash "splash.png" --collect-all ultralytics --collect-all customtkinter --collect-all pandas --collect-all tkinterdnd2 app_ematologo.py
________________________________________
