from fasthtml.all import *
import anthropic, os, base64, uvicorn

# We'll use anthropic's Haiku model for this demo
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

# Custom JS courtesy of GPT-4o
canvas_js = """
    const canvas = document.getElementById('drawingCanvas');
    const context = canvas.getContext('2d');
    let drawing = false;

    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mousemove', draw);

    function startDrawing(e) {
      drawing = true;
      draw(e);
    }

    function stopDrawing() {
      drawing = false;
      context.beginPath();
      sendCanvasData();
    }

    function draw(e) {
      if (!drawing) return;
      context.lineWidth = 5;
      context.lineCap = 'round';
      context.strokeStyle = 'black';

      context.lineTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
      context.stroke();
      context.beginPath();
      context.moveTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
    }

    function sendCanvasData() {
      canvas.toBlob((blob) => {
        const formData = new FormData();
        formData.append('image', blob, 'canvas.png');

        fetch('/process-canvas', {
          method: 'POST',
          body: formData,
        }).then(response => response.json())
          .then(data => {
            document.getElementById('caption').innerHTML = data.caption;
            console.log(data);})
          .catch(error => console.error('Error:', error));
      });
    }
"""

canvas_css = """
canvas {
      border: 1px solid black;
      background-color: #f0f0f0;
    }
"""

pending = False
caption = "Draw something!"

app = FastHTML(hdrs=(picolink,
                     Script(canvas_js, type="module"),
                     Style(canvas_css)))

# Main page
@app.get("/")
def home():
    return Title('Drawing Demo'), Main(
        H1("Haiku Canvas Demo"), 
        Canvas(id="drawingCanvas", width="500", height="500"), 
        Div("Draw something", id="caption"), cls='container')


@app.post("/process-canvas")
async def process_canvas(request):
    form = await request.form()
    image = form.get('image')
    image_bytes = await image.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        temperature=0.5,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Write a haiku about this drawing, respond with only that."
                    }
                ],
            }
        ],
    )
    caption =  message.content[0].text
    caption = caption.replace("\n", "<br>")
    return JSONResponse({"caption": caption})

if __name__ == '__main__':
  uvicorn.run("draft1:app", host='0.0.0.0', port=8000, reload=True)
