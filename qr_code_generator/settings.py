import os
from dotenv import load_dotenv

load_dotenv()

# App Theme from Pico CSS
THEME = os.environ.get('THEME', 'blue')