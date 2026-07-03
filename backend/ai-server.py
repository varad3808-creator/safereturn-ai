from fastapi import Body
from dotenv import load_dotenv
import os
load_dotenv()
import resend
resend.api_key = os.getenv("RESEND_API_KEY")

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import insightface
import io
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading Buffalo_S model...")

model = insightface.app.FaceAnalysis(
    name="buffalo_s",
    providers=["CPUExecutionProvider"]
)

model.prepare(
    ctx_id=0,
    det_size=(320, 320)
)

print("Buffalo_S Loaded Successfully")


@app.get("/")
def root():
  return {
    "status": "running",
    "model": "Buffalo_S"
}


@app.post("/extract")
async def extract_face(file: UploadFile = File(...)):

    contents = await file.read()

    image = Image.open(
        io.BytesIO(contents)
    ).convert("RGB")

    image_np = np.array(image)

    print("Image Shape:", image_np.shape)

    faces = model.get(image_np)

    print("Faces Found:", len(faces))

    if len(faces) == 0:
        return {
            "success": False,
            "message": "No face detected"
        }

    embedding = faces[0].embedding.tolist()

    return {
        "success": True,
        "embedding_length": len(embedding),
        "embedding": embedding
    }

@app.post("/contact")
async def contact(data: dict = Body(...)):

    try:

        params = {
            "from": "onboarding@resend.dev",
            "to": ["varad3808@gmail.com"],
            "reply_to": data["email"],
            "subject": f"SafeReturn Contact: {data['subject']}",
            "html": f"""
            <h2>New Contact Message</h2>

            <p><b>Name:</b> {data['name']}</p>

            <p><b>Email:</b> {data['email']}</p>

            <p><b>Subject:</b> {data['subject']}</p>

            <hr>

            <p>{data['message']}</p>
            """
        }

        resend.Emails.send(params)

        return {
            "success": True
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )