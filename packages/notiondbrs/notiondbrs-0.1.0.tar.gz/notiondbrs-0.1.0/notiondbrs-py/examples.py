from notion_utils import NotionClient
from dotenv import load_dotenv
import os
import uuid
import random
import time

load_dotenv()

NOTION_TOKEN = os.environ.get("NOTION_TOKEN") or "none"
DB_ID = os.environ.get("DB_ID") or "none"
PAGE_ID = os.environ.get("PAGE_ID") or "none"

client = NotionClient(NOTION_TOKEN)
databases = client.get_all_databases()

data = client.get_data_from_database(DB_ID)

data_len = 1000
upload_data = {
    "name": [f"Name_{i}" for i in range(data_len)],
    "id": [str(uuid.uuid4()) for _ in range(data_len)],
    "value": [str(random.randint(1, 100000)) for _ in range(data_len)],
}

start_time = time.time()

#client.insert_data(upload_data, PAGE_ID, new_db=True)
client.merge_data(upload_data, DB_ID)
#client.insert_data(upload_data, DB_ID)
end_time = time.time()

duration = end_time - start_time
print(f"✅ Uploaded {data_len} rows in {duration:.2f} seconds")
print(f"📈 Average time per row: {duration / data_len:.4f} seconds")

#client.merge_data(upload_data, DB_ID)
#client.insert_data(upload_data, DB_ID)