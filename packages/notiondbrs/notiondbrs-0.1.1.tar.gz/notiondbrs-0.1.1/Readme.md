# NotionDBRS 🦀

A high-performance Notion database client built with Rust and exposed to Python via PyO3. Handles bulk data operations efficiently with parallel processing.

## Features

- **Rust-powered backend** with Tokio async runtime for parallel operations
- **Smart data merging** - only uploads new/changed records
- **Bulk operations** - efficiently handle large datasets
- **Dynamic database creation** - create Notion databases programmatically
- **Type-safe** - comprehensive error handling across Python-Rust boundary

## Installation

```bash
# from pypi
pip install notiondbrs
```

```bash
# Clone and build
git clone https://github.com/yourusername/notiondbrs.git
cd notiondbrs
chmod +x run.sh
./run.sh
```

## Configuration

Create a `.env` file:

```env
NOTION_TOKEN=your_notion_integration_token
DB_ID=your_database_id
PAGE_ID=your_page_id  # For creating new databases
```

## Usage

### Basic Setup

```python
from notion_utils import NotionClient
import os
from dotenv import load_dotenv

load_dotenv()
client = NotionClient(os.environ.get("NOTION_TOKEN"))
```

### List Databases

```python
databases = client.get_all_databases()
for db_id, db_name in databases:
    print(f"{db_name}: {db_id}")
```

### Get Data from Database

```python
data = client.get_data_from_database("your-database-id")
print(f"Retrieved {len(next(iter(data.values())))} rows")
print(f"Columns: {list(data.keys())}")
```

### Bulk Data Upload

```python
import uuid
import random
import time

# Prepare data
upload_data = {
    "name": [f"Item_{i}" for i in range(1000)],
    "id": [str(uuid.uuid4()) for _ in range(1000)],
    "value": [str(random.randint(1, 1000)) for _ in range(1000)]
}

# Upload with timing
start_time = time.time()
client.insert_data(upload_data, "your-database-id")
duration = time.time() - start_time

print(f"Uploaded 1000 rows in {duration:.2f} seconds")
print(f"Throughput: {1000/duration:.0f} rows/second")
```

### Smart Data Merging

```python
# Only new records will be uploaded
merge_data = {
    "name": ["Existing_Item", "New_Item_1", "New_Item_2"],
    "id": ["existing-123", "new-456", "new-789"],
    "value": ["100", "200", "300"]
}

client.merge_data(merge_data, "your-database-id")
```

### Create New Database

```python
new_data = {
    "title": ["Entry 1", "Entry 2"],
    "status": ["Active", "Pending"],
    "date": ["2024-01-01", "2024-01-02"]
}

# Creates database and uploads data
client.insert_data(new_data, "your-page-id", new_db=True)
```

## Performance

Typical performance on standard datasets:

| Records | Time 
|---------|------|
| 100 | ~8s | 
| 1,000 | ~30s |
| Data Retrieval | <1s |


## Architecture

The Rust backend uses Tokio for async parallel processing while maintaining a simple Python interface:

```python
# Python layer - simple and clean
client.insert_data(data, db_id)

# Rust layer handles:
# - Parallel HTTP requests
# - Memory-efficient data processing
# - Error handling and retries
```

## Development

### Project Structure

```
src/                 # Rust implementation
├── lib.rs          # PyO3 module
├── notion_class.rs # Python interface
├── notion_utils.rs # Core API logic
└── utils.rs        # Data processing

notiondbrs-py/      # Python wrapper
├── examples.py         # Usage examples
└── notion_utils.py # Python interface
```

### Building

```bash
# Development build
maturin develop

# Release build (optimized)
maturin develop --release
```

## License

MIT License