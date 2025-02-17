import sys
from py_stream_zip.stream_zip import StreamZip


def main():
    zip_path = "test.zip"  # Path to the ZIP file.
    entry_name = "document.txt"  # Name of the file entry in the ZIP.

    try:
        # Create a StreamZip instance.
        zip_archive = StreamZip(zip_path, store_entries=True)
    except Exception as e:
        print(f"Error opening ZIP file: {e}")
        sys.exit(1)

    try:
        # Read the uncompressed data of the specified entry into a variable.
        data = zip_archive.entry_data_sync(entry_name)
        # data now contains the uncompressed bytes of "document.txt".
        print(f"Content of '{entry_name}':")
        print(data.decode("utf-8"))
    except Exception as e:
        raise e
        print(f"Error reading entry '{entry_name}': {e}")
    finally:
        zip_archive.close()


if __name__ == "__main__":
    main()
