#readme for instructions

import os
from dotenv import load_dotenv

load_dotenv()

OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')


print(OPEN_AI_KEY)
