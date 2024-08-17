from fastcore.parallel import threaded
from fasthtml.common import *
import os, uvicorn, requests, replicate
from PIL import Image

app = FastHTML(hdrs=(picolink,))

# Replicate setup (for image generation)
replicate_api_token = os.environ["REPLICATE_API_KEY"]
client = replicate.Client(
    api_token=replicate_api_token, headers={"User-Agent": "my-app/1.0"}
)

# Store our generations
generations = []
folder = f"gens/"
os.makedirs(folder, exist_ok=True)


# Main page
@app.get("/")
def home():
    inp = Input(id="new-prompt", name="prompt", placeholder="Enter a prompt")
    add = Form(
        Group(inp, Button("Generate")),
        hx_post="/",
        target_id="gen-list",
        hx_swap="afterbegin",
    )
    gen_list = Div(id="gen-list")
    return Title("Image Generation Demo"), Main(
        H1("Magic Image Generation"), add, gen_list, cls="container"
    )


# A pending preview keeps polling this route until we return the image preview
def generation_preview(id):
    if os.path.exists(f"gens/{id}.png"):
        return Div(Img(src=f"/gens/{id}.png"), id=f"gen-{id}")
    else:
        return Div(
            "Generating...",
            id=f"gen-{id}",
            hx_post=f"/generations/{id}",
            hx_trigger="every 1s",
            hx_swap="outerHTML",
        )


@app.post("/generations/{id}")
def get(id: int):
    return generation_preview(id)


# For images, CSS, etc.
@app.get("/{fname:path}.{ext:static}")
def static(fname: str, ext: str):
    return FileResponse(f"{fname}.{ext}")


# Generation route
@app.post("/")
def post(prompt: str):
    id = len(generations)
    generate_and_save(prompt, id)
    generations.append(prompt)
    clear_input = Input(
        id="new-prompt", name="prompt", placeholder="Enter a prompt", hx_swap_oob="true"
    )
    return generation_preview(id), clear_input


# Generate an image and save it to the folder (in a separate thread)
@threaded
def generate_and_save(prompt, id):
    output = client.run(
        "playgroundai/playground-v2.5-1024px-aesthetic:a45f82a1382bed5c7aeb861dac7c7d191b0fdf74d8d57c4a0e6ed7d4d0bf7d24",
        input={
            "width": 1024,
            "height": 1024,
            "prompt": prompt,
            "scheduler": "DPMSolver++",
            "num_outputs": 1,
            "guidance_scale": 3,
            "apply_watermark": True,
            "negative_prompt": "ugly, deformed, noisy, blurry, distorted",
            "prompt_strength": 0.8,
            "num_inference_steps": 25,
        },
    )
    Image.open(requests.get(output[0], stream=True).raw).save(f"{folder}/{id}.png")
    return True


if __name__ == "__main__":
    uvicorn.run("draft1:app", host="0.0.0.0", port=int(os.getenv("PORT", default=5000)))
