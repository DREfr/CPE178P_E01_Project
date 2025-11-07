from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, Form
import mindspore as ms
from mindspore import Tensor
from mindspore.train.serialization import load_checkpoint, load_param_into_net
import json, base64, io
from PIL import Image
import numpy as np
import mobilenet_ms as mn
import os

app = FastAPI()

# --- Setup ---
num_class = 12
rock_classes = [
    "Basalt", "Chert", "Coal", "Gneiss", "Granite", 
    "Limestone", "Marble", "Obsidian", "Pumice", 
    "Sandstone", "Slate", "Travertine"
]

# Initialize global variables
net = None
model = None
current_ckpt = "ckpt/mobilenet_v2-25_74.ckpt"

def load_model(ckpt_path):
    global net, model, current_ckpt
    print(f"Loading model from: {ckpt_path}")
    param_dict = load_checkpoint(ckpt_path)
    net = mn.mobilenet_v2(num_class)
    load_param_into_net(net, param_dict)
    model = ms.Model(net)
    current_ckpt = ckpt_path

# Load default model initially
load_model(current_ckpt)


# --- Preprocessing ---
def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = img.resize((224, 224))
    img = np.array(img) / 255.0
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    img = (img - mean) / std
    img = img.transpose(2, 0, 1)
    img = img[np.newaxis, ...]
    return Tensor(img, ms.float32)


# --- Prediction REST ---
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    input_data = preprocess_image(image_bytes)
    net.set_train(False)
    output = net(input_data)
    predicted_class = int(np.argmax(output.asnumpy()))
    return {"class": predicted_class, "class_name": rock_classes[predicted_class]}


# --- Change Model REST ---
@app.post("/change_model")
async def change_model(ckpt_path: str = Form(...)):
    # 1. Check file existence
    if not os.path.isfile(ckpt_path):
        return {"status": "error", "message": "File does not exist."}

    # 2. Check file extension
    if not ckpt_path.endswith(".ckpt"):
        return {"status": "error", "message": "Invalid file type. Only .ckpt files allowed."}

    # 3. Try loading the model
    try:
        load_model(ckpt_path)  # your existing function that loads MindSpore checkpoint
        return {"status": "success", "message": f"Model changed to {ckpt_path}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to load checkpoint: {str(e)}"}


# --- WebSocket ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            image_data = base64.b64decode(json.loads(data)["data"])
            input_data = preprocess_image(image_data)
            net.set_train(False)
            output = net(input_data)
            predicted_class = int(np.argmax(output.asnumpy()))
            predicted_class_str = rock_classes[predicted_class]
            await websocket.send_text(json.dumps({
                "type": "prediction",
                "class": predicted_class_str,
                "class_index": predicted_class
            }))
    except WebSocketDisconnect:
        pass
