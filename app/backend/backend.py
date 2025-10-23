from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
import mindspore as ms
from mindspore import Tensor
from mindspore.train.serialization import load_checkpoint, load_param_into_net 
import json
import base64
from PIL import Image
import numpy as np
import io

import mobilenet_ms as mn  # your mobilenet wrapper

app = FastAPI()

# Number of rock classes
num_class = 12
rock_classes = [
    "Basalt", "Chert", "Coal", "Gneiss", "Granite", 
    "Limestone", "Marble", "Obsidian", "Pumice", 
    "Sandstone", "Slate", "Travertine"
]

# Load the MindSpore model checkpoint
param_dict = load_checkpoint("ckpt/mobilenet_v2-25_74.ckpt")  # replace with your actual checkpoint

# Create the network
net = mn.mobilenet_v2(num_class)
ms.load_param_into_net(net, param_dict)
model = ms.Model(net)

# Preprocessing function
def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = img.resize((224, 224))  # or center crop if you used that
    img = np.array(img) / 255.0
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    img = (img - mean) / std
    img = img.transpose(2, 0, 1)  # HWC -> CHW
    img = img[np.newaxis, ...]  # Add batch dim
    return Tensor(img, ms.float32)

# REST endpoint (optional)
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    input_data = preprocess_image(image_bytes)
    
    net.set_train(False)             # put network in evaluation mode
    output = net(input_data)         # forward pass
    
    predicted_class = int(np.argmax(output.asnumpy()))
    return {"class": predicted_class, "class_name": rock_classes[predicted_class]}

# WebSocket endpoint for Flet
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            image_data = base64.b64decode(json.loads(data)["data"])
            input_data = preprocess_image(image_data)
            
            net.set_train(False)          # <-- use net, not model
            output = net(input_data)      # forward pass
            predicted_class = int(np.argmax(output.asnumpy()))
            predicted_class_str = rock_classes[predicted_class]
            
            await websocket.send_text(json.dumps({
                "type": "prediction",
                "class": predicted_class_str,
                "class_index": predicted_class
            }))
    except WebSocketDisconnect:
        pass
