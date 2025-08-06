
---

**HoloRelay** is a zero-dependency, production-ready message router for agent-to-agent communication in Python.  
It lets you send and receive messages between named agents—perfect for coordinating tasks in multi-agent systems, toolchains, or even distributed apps.

---

## Install

```sh
pip install HoloRelay
````

---

## Usage

```python
from HoloRelay import HoloRelay

ata = HoloRelay()

# Send a message from one agent to another
ata.send("Alpha", "Bravo", "Ping from Alpha!")

# Agent Bravo receives their messages
messages = ata.receive("Bravo")
print(messages)
# Output: [{'from': 'Alpha', 'to': 'Bravo', 'content': 'Ping from Alpha!'}]

# Support for filtering by sender
ata.send("Alpha", "Charlie", "Hello, Charlie!")
ata.send("Beta", "Charlie", "Hi, Charlie!")
msgs = ata.receive("Charlie", allowedFrom=["Beta"])
print(msgs)
# Output: [{'from': 'Beta', 'to': 'Charlie', 'content': 'Hi, Charlie!'}]
```

---

## Features

* **Direct agent-to-agent messaging** – Send and receive by agent name.
* **Broadcasting** – Send to all by using `toAgent=None`.
* **Filtered receive** – Optionally receive only from allowed senders.
* **In-memory queue** – Each receive call pulls all available messages.
* **Zero dependencies** – No third-party packages required.
* **Works with any agent framework** – Simple plug-and-play for any system.

---

## Code Examples

You can find code examples on my [GitHub repository](https://github.com/TristanMcBrideSr/TechBook).

---

## License

Apache License 2.0

---

## Acknowledgements

Project by:
- Tristan McBride Sr.
- Sybil
