# PyNotiQ Client

A simple Python library to add messages to the PyNotiQ JSON queue.

## Installation

```sh
pip install pynotiq_client
```

## Usage

```python
from pynotiq_client import PyNotiQ

notifier = PyNotiQ(queue_file="queue.json")

# Add message with auto-generated ID
notifier.add_message({
    "message_field_1": "Message Field Value 1",
    "message_field_2": "Message Field Value 2",
})

# Add message with custom ID (optional)
notifier.add_message({
    "message_field_1": "Another Message",
    "message_field_2": "Another Value",
}, item_id="custom-message-id-123")

# Retrieve all messages
messages = notifier.get_messages()
print(messages)
```

## ✨ Features

### 🔄 Queue Management
- **Add Messages** - Easily add structured messages to the JSON queue
- **Retrieve Messages** - Get all messages from the queue for processing
- **Clear Queue** - Remove all messages from the queue when needed
- **Persistent Storage** - Messages are stored in a JSON file for reliability

### 🛠️ Developer Experience
- **Simple API** - Intuitive interface for quick integration
- **JSON Format** - Standard JSON structure for easy data handling
- **Flexible Schema** - Support for custom message fields and structures
- **Lightweight** - Minimal dependencies for fast installation and usage

### 📊 Data Structure
- **Unique IDs** - Each message gets a unique identifier for tracking
- **Timestamps** - Automatic timestamp generation for message ordering
- **Custom Fields** - Add any custom data fields to your message body
- **Type Safety** - Structured data format ensures consistency
