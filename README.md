# py-stream-zip

**py-stream-zip** is a Python library for extracting ZIP files using a stream-based approach. It provides efficient access to ZIP file entries without needing to load the entire file into memory. This package is inspired by and gives credit to [node-stream-zip](https://github.com/antelle/node-stream-zip).

## Features

- Stream-based extraction of ZIP files.
- Reads the central directory and processes entries on the fly.
- Simple, synchronous API for ease of integration.


## Installation

You can install **py-stream-zip** using pip:

```bash
pip install py-stream-zip
```

## Usage

Below is an example demonstrating how to extract a file from a ZIP archive:

```python
from py_stream_zip import StreamZip

zip_path = "path/to/archive.zip"
entry_name = "document.txt"  # The name of the file inside the ZIP

# Create a StreamZip instance (ensuring entries are stored for random access)
zip_archive = StreamZip(zip_path, store_entries=True)

try:
    # Extract and read the content of the specified entry.
    data = zip_archive.entry_data_sync(entry_name)
    print(data.decode("utf-8"))

    # or save to file as binary
    with open("document.txt", "wb") as f:
        f.write(data)

except Exception as ex:
    print(f"Error processing the ZIP file: {ex}")
finally:
    # Always close the archive to free the file handle.
    zip_archive.close()
```

For further reference, check out the provided [test_unzip.py](test_unzip.py) for a complete working example.

## Credits

**py-stream-zip** is inspired by [node-stream-zip](https://github.com/antelle/node-stream-zip). Special thanks to its developers for their contributions to the streaming ZIP extraction technique.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
