# Skope SDK

A Python SDK for interacting with the Skope API.

## Installation

```bash
pip install skope-sdk
```

## Usage

```python
from skope_sdk import SkopeClient, Item

# Initialize the client
client = SkopeClient(
    api_key="your_api_key_here",
    base_url="https://api.skope.io"  # Optional, defaults to localhost:8000
)

# Create a single item
item = Item(
    name="Example Item",
    url="https://example.com",
)

result = client.create_item(item)
print(f"Created item: {result}")

# Create multiple events
events = [
    Item(name="Item 1"),
    Item(name="Item 2")
]

results = client.create_items(items)
print(f"Created items: {results}")
```

## Error Handling

The SDK will raise `SkopeError` if any API requests fail:

```python
from skope_sdk import SkopeError

try:
    result = client.create_item(item)
except SkopeError as e:
    print(f"Failed to create item: {e}")
```

## API Reference

### SkopeClient

#### `__init__(api_key: str, base_url: str = "http://localhost:8000")`

Initialize a new Skope client.

- `api_key`: Your Skope API key
- `base_url`: The base URL of the Skope API (optional)

#### `create_item(item: Item) -> Dict[str, Any]`

Create a single item.

- `item`: An Item object with the item details
- Returns: The created item data

#### `create_items(items: List[Item]) -> Dict[str, Any]`

Create multiple items in one request.

- `items`: A list of Item objects
- Returns: The response data containing created items

### Item

A dataclass representing an item in Skope.

#### Fields:

- `name`: str (required)
