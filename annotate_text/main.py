from fasthtml.common import *
import json

# Set up the app, including daisyui and tailwind for the chat component
tlink = Script(src="https://cdn.tailwindcss.com?plugins=typography"),
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")

# Define a global variable for total items length
total_items_length = 0


#this render function must be defined before the app is created 
def render(Item):
    messages = json.loads(Item.messages)
    card_header = Div(
        Div(
            H3(f"Sample {Item.id} out of {total_items_length}" if total_items_length else "No samples in DB", cls="text-base font-semibold leading-6 text-gray-9000"),
            Div(
                A(
                    Span("←", cls="sr-only"),
                    Span("←", cls="h-5 w-5", aria_hidden="true"),
                    hx_get=f"/{Item.id - 2}" if Item.id > 0 else "#",
                    hx_swap="outerHTML",
                    
                    cls="relative inline-flex items-center rounded-l-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600" + (" pointer-events-none opacity-50" if Item.id == 1 else "")
                ),
                A(
                    Span("→", cls="sr-only"),
                    Span("→", cls="h-5 w-5", aria_hidden="true"),
                    hx_get=f"/{Item.id}" if Item.id < total_items_length - 1 else "#",
                    hx_swap="outerHTML",
                    cls="relative -ml-px inline-flex items-center rounded-r-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600" + (" pointer-events-none opacity-50" if Item.id == total_items_length - 1 else "")
                ),
                cls="flex-shrink-0"
            ),
            cls="flex justify-between items-center mb-4"
        ),
        Div(
            Div(
                P(messages[0]['content'], cls="mt-1 text-sm text-gray-500 max-h-16 overflow-y-auto whitespace-pre-wrap"),
                cls="ml-4 mt-4"
            ),
            cls="-ml-4 -mt-4 flex flex-wrap items-center justify-between sm:flex-nowrap"
        ),
        cls="border-b border-gray-200 bg-white p-4"
    )
    card_buttons_form = Div(
        Form(
            Input(
                type="text",
                name="notes",
                value=Item.notes,
                placeholder="Additional notes?",
                cls="flex-grow p-2 my-4 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-transparent"
            ),
            Div(
                Button("Correct",  
                       name="feedback", 
                       value="correct", 
                       cls=f"btn btn-success mr-2 hover:text-white {'' if Item.feedback == 'correct' else 'btn-outline'}"
                       ),
                Button("Incorrect", 
                       name="feedback", 
                       value="incorrect", 
                        cls=f"btn btn-error hover:text-white {'' if Item.feedback == 'incorrect' else 'btn-outline'}"
                       ),
                cls="flex-shrink-0 ml-4"
            ),
            cls="flex items-center",
            method="post",
            hx_post=f"/{Item.id}", target_id=f"item_{Item.id}", hx_swap="outerHTML", hx_encoding="multipart/form-data"
            
        ),
        cls="mt-4"
    )
    
    # Card component
    card = Div(
        card_header,
        Div(
            Div(
                messages[1]['content'],
                id="main_text",
                cls="mt-2 w-full rounded-t-lg text-sm whitespace-pre-wrap h-auto marked"
            ),
            cls="bg-white shadow rounded-b-lg p-4 pt-0 pb-10 flex-grow overflow-scroll"
        ),
        card_buttons_form,
        cls="  flex flex-col h-full flex-grow overflow-auto",
        id=f"item_{Item.id}",
        style="min-height: calc(100vh - 6rem); max-height: calc(100vh - 16rem);"
    )
    return card

app, rt, texts_db, Item = fast_app('texts.db',hdrs=(tlink, dlink, picolink, MarkdownJS(), HighlightJS()), live=True, id=int, messages=list, feedback=bool, notes=str, pk='id', render=render, bodykw={"data-theme":"light"})


title = 'LLM generated text annotation tool with FastHTML (and Tailwind)'
total_items_length = len(texts_db())
if total_items_length == 0:
    print("No items found")
    import json
    with open('./data/dummy_data.jsonl', 'r') as file:
        for line in file:
            item = json.loads(line)
            texts_db.insert(messages=json.dumps(item), feedback=None, notes='')
    
    # Update total_items_length after inserting dummy data
    total_items_length = len(texts_db())
    print(f"Inserted {total_items_length} items from dummy data")


@rt("/{idx}")
def post(idx: int, feedback: str = None, notes: str = None):
    print(f"Posting feedback: {feedback} and notes: {notes} for item {idx}")
    items = texts_db()
    item = texts_db.get(idx)
    
    item.feedback = feedback
    item.notes = notes
    texts_db.update(item)
    
    # find the next item using list comprehension
    next_item = next((i for i in items if i.id > item.id), items[0])
    # next_item = items[idx + 1] if idx < len(items) - 1 else items[0]
    
    print(f"Updated item {item.id} with feedback: {feedback} and notes: {notes} moving to {next_item.id}")
    return next_item

@rt("/")
@rt("/{idx}")
def get(idx:int = 0):
    items = texts_db()
    
    index = idx 
    if index >= len(items):
        index = len(items) - 1 if items else 0

    # Container for card and buttons
    content = Div(
        H1(title,cls="text-xl font-bold text-center text-gray-800 mb-8"),
        items[index],
        cls="w-full max-w-2xl mx-auto flex flex-col max-h-full"
    )
    
    return Main(
        content,
        cls="container mx-auto min-h-screen bg-gray-100 p-8 flex flex-col",
        hx_target="this"
    )


serve()