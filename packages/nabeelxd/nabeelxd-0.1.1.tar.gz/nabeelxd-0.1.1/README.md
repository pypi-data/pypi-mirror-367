# nabeelxd

A simple Python package to fetch and run/save scripts from a GitHub folder.

## Features
- `nabeelxd.run("filename")` → Fetch & execute script (runs `main()` automatically if present)
- `nabeelxd.save("filename", "localname.py")` → Fetch & save script as a Python file

## Usage
```python
import nabeelxd

# Run a script directly
nabeelxd.run("test")

# Save a script locally
nabeelxd.save("test", "password.py")