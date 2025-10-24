# 🪨 Rock Classification System

**CPE178P – Foundations of Artificial Intelligence**
**Mapúa University – Intramuros**

A desktop-based AI system for classifying rock images using **MobileNetV2** trained in **MindSpore**.
It features a **Flet-powered frontend** and a **FastAPI + WebSocket backend**, enabling real-time predictions directly from your desktop.

---

## 🚀 Features

* Upload rock images directly from the GUI
* Real-time prediction via WebSocket
* MobileNetV2 model trained on 12 rock classes
* Cross-platform support (Windows, Linux, macOS)
* Clean and modern interface built with Flet

Supported rock classes:

> Basalt, Chert, Coal, Gneiss, Granite, Limestone, Marble, Obsidian, Pumice, Sandstone, Slate, Travertine

---

## 🧩 System Overview

```
[Flet Frontend]  ↔  [FastAPI WebSocket Backend]  ↔  [MindSpore MobileNetV2 Model]
```

---

## 🛠️ Installation and Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/DREfr/CPE178P_E01_Project.git
cd CPE178P_E01_Project
```

### 2️⃣ Create and Activate a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS/Linux
```

### 3️⃣ Install Python Requirements

Make sure you are using **Python 3.11**.

```bash
pip install -r requirements.txt
```

---

## 🧠 MindSpore Installation

For all supported platforms (Windows / Linux / macOS):

```bash
pip install mindspore==2.7.0 -i https://repo.mindspore.cn/pypi/simple --trusted-host repo.mindspore.cn --extra-index-url https://repo.huaweicloud.com/repository/pypi/simple
```

For more details, see the official MindSpore docs:
👉 [https://www.mindspore.cn/install](https://www.mindspore.cn/install)

---

## 📦 requirements.txt

```
fastapi
uvicorn
flet
pillow
numpy
websockets
```

> ⚠️ MindSpore must be installed separately using the command above (it depends on your OS and hardware).

---

## 🧠 Model Setup

Place your trained model checkpoint inside the `ckpt/` folder:

```
ckpt/mobilenet_v2-25_74.ckpt
```

Update `backend.py` if you use a different filename:

```python
param_dict = load_checkpoint("ckpt/mobilenet_v2-25_74.ckpt")
```

---

## ▶️ Run the Application

### 1️⃣ Start the Backend Server

```bash
uvicorn backend:app --host 0.0.0.0 --port 8000
```

### 2️⃣ Launch the Frontend

```bash
python frontend.py
```

### ✅ Done!

Upload any rock image from the GUI, click **“Classify”**, and see the predicted rock type instantly.

---

## 📸 Interface Overview

* Upload button → Choose a rock image
* Image preview → Displays the selected image
* “Classify” button → Sends to backend for prediction
* Output text → Displays predicted rock type in real time

---

## 📚 Tech Stack

| Component              | Technology                 |
| ---------------------- | -------------------------- |
| **Frontend**           | Flet (Python UI Framework) |
| **Backend**            | FastAPI + WebSockets       |
| **Model Framework**    | MindSpore 2.7.0            |
| **Model Architecture** | MobileNetV2                |
| **Python Version**     | 3.11                       |

---

## 👨‍💻 Developers

Developed by:
**DREfr** and Team – CPE178P (Foundations of Artificial Intelligence)
Mapúa University – Intramuros

GitHub Repository:
🔗 [https://github.com/DREfr/CPE178P_E01_Project](https://github.com/DREfr/CPE178P_E01_Project)

---


