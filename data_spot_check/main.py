from fasthtml.common import *
import uuid, os, uvicorn, random, datasets
import pandas as pd
from starlette.responses import RedirectResponse, FileResponse  

db = database('data/data_spot_check.db')

# The data to review
samples = db.t.samples
if samples not in db.t:
    samples.create(id=int, original_id=str, text=str, rated=bool, source=str, pk='id')
    samples_per_shard = 1000
    for shard in ['shard_0', 'shard_1', 'shard_2', 'shard_3', 'shard_4', 'shard_5', 'shard_6', 'shard_7', 'shard_8', 'shard_9', 'shard_10', 'shard_11', 'shard_12']:
        d = datasets.load_dataset("orionweller/dolma_20bn_cc_high_quality", split=shard, streaming=True)
        sources = []
        for i, sample in enumerate(d):
            if i >= samples_per_shard: break
            samples.insert(original_id=str(sample['id']), text=sample['text'], source=sample['source'], rated=False)
            sources.append(sample['source'])
Sample = samples.dataclass() 
print("Data loaded. Sources:", set([s.source for s in samples()]))

# Store ratings done via this app
ratings = db.t.ratings
if ratings not in db.t:
    ratings.create(id=int, sample_id=str, rating=str, rater=str, pk='id')

# The app
app = FastHTML(hdrs=(picolink,))

# Landing Page
@app.get("/")
def home():
    return Title('Home'), Main(H1('Welcome to the home page!'), 
                               P("Click this link to start rating data.", A("Rate", href="/rate")),
                               P("You can get the ratings here:", A("Download", href="/download_db")),
                               cls='container')

@app.get("/download_db")
def download_db():
    # Guess who prefers pandas to SQL...
    df = pd.DataFrame(ratings())
    df['text'] = [samples[sample_id].text for sample_id in df['sample_id']]
    df['source'] = [samples[sample_id].source for sample_id in df['sample_id']]
    # Saving to CSV and returning a FileResponse is one easy way to do this
    df.to_csv("data/ratings.csv", index=False)
    return FileResponse("data/ratings.csv", media_type='text/csv', filename="ratings.csv")

# Main page (rate samples)
@app.get("/rate")
def rate(session):
    if 'id' not in session: session['id'] = str(uuid.uuid4())
    # Pick an unrated sample
    unrated = samples(where="rated is not True")
    sample = random.choice(unrated) if unrated else None
    if not sample: return Title('All samples rated'), H1('All samples rated!'), A('Back', href="/")
    # Show
    return Title('Rate'), Main(H1('Rate the following sample'),
        H3(f"Sample {sample.original_id}"), 
        P("Source: ", sample.source),
        Div(
            "Select a label:",
            A('Good', href=f"/rate/{sample.id}/good"),
            A('Ok', href=f"/rate/{sample.id}/ok"),
            A('Bad', href=f"/rate/{sample.id}/bad"),
        ), 
        Br(), P(sample.text), cls='container')

@app.get("/rate/{id}/{label}")
def rate(id: str, label: str, session):
    if 'id' not in session: return RedirectResponse("/rate")
    sample = samples[id]
    if sample:
        sample.rated = True
        sample.rater = session['id']
        samples.update(sample)
    ratings.insert(sample_id=id, rating=label, rater=session['id'])
    return RedirectResponse("/rate")

if __name__ == '__main__': uvicorn.run("main:app", host='0.0.0.0', reload=True, port=int(os.getenv("PORT", default=5000)))