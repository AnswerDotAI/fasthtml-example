from fasthtml.common import *
import os, uvicorn
from starlette.responses import FileResponse
from starlette.datastructures import UploadFile

app = FastHTML(hdrs=(picolink,))

# Ensure the uploads directory exists
os.makedirs("uploads", exist_ok=True)

# Your image classification function goes here:
def classify(image_path): return f"not hotdog!"

@app.get("/")
def home():
    return Title("Image Classification"), Main(
        H1("Image Classification App"),
        Form(
            Input(type="file", name="image", accept="image/*", required=True),
            Button("Classify"),
            enctype="multipart/form-data",
            hx_post="/classify",
            hx_target="#result"
        ),
        Br(), Div(id="result"),
        cls="container"
    )

@app.post("/classify")
async def handle_classify(image:UploadFile):
    
    # Save the uploaded image
    image_path = f"uploads/{image.filename}"
    with open(image_path, "wb") as f:
        f.write(await image.read())
    
    # Classify the image (dummy function for this example)
    result = classify(image_path)
    
    return Div(
        P(f"Classification result: {result}"),
        Img(src=f"/uploads/{image.filename}", alt="Uploaded image", style="max-width: 300px;")
    )

@app.get("/uploads/{filename}")
async def serve_upload(filename: str):
    return FileResponse(f"uploads/{filename}")

if __name__ == '__main__': uvicorn.run("main:app", host='0.0.0.0', port=int(os.getenv("PORT", default=5000)), reload=True)
