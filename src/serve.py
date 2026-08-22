import io
import os
from pathlib import Path
import torch
import torch.nn.functional as F
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from PIL import Image
from dataset import get_transforms
from model import get_model

app = FastAPI(title="PyTorch Model Serving API")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None
checkpoint_path = Path("/app/checkpoints/classifier_v1.pt")

@app.on_event("startup")
def load_checkpoint():
    global model
    try:
        model = get_model(num_classes=10).to(device)
        if checkpoint_path.exists():
            checkpoint = torch.load(checkpoint_path, map_location=device)
            state_dict = checkpoint.get("model_state_dict", checkpoint)
            model.load_state_dict(state_dict)
            model.eval()
            print(f"Loaded model from {checkpoint_path}")
        else:
            print(f"Checkpoint not found at {checkpoint_path}")
            model.eval()
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None

@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    if model is None:
        raise HTTPException(status_code=500, detail="Model unavailable")
    return {"status": "healthy"}

@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=500, detail="Model unavailable")
    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        transform = get_transforms(train=False)
        tensor = transform(img).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model(tensor)
            probabilities = F.softmax(outputs, dim=1).squeeze().tolist()
            predicted_class = int(torch.argmax(outputs, dim=1).item())

        return {
            "predicted_class": predicted_class,
            "probabilities": [round(p, 4) for p in probabilities]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")
