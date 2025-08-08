from genstack import Genstack
from dotenv import load_dotenv
import os

load_dotenv()



client = Genstack(api_key=os.getenv("GENSTACK_API_KEY"))


res = client.get_output_text(input="3 fun facts about Ferrari", track="ultimate-track", model="gpt-4o-oai")

print(res)