from fasthtml.common import *
from todos import create_app

# actual app creation process moved to todos.py
# this way we can support different modes of the app (i.e. dev, test)
# you can further extend create_app to support a more fine-grained configuration 
app, _ = create_app()
serve()
