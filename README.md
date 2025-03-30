# ComfyGCS

ComfyGCS is a robust read/write plugin for Google Cloud Storage, designed to simplify interaction with GCS buckets in your projects.

## Features

- Seamless integration with Google Cloud Storage.
- Read and write operations with ease.
- Lightweight and efficient.

## Installation

To install ComfyGCS, use the following command:

```bash
pip install comfygcs
```

## Usage

Here's a quick example to get started:

```python
from comfygcs import GCSClient

# Initialize the client
client = GCSClient(bucket_name="your-bucket-name")

# Upload a file
client.upload_file("local-file.txt", "remote-file.txt")

# Download a file
client.download_file("remote-file.txt", "local-file.txt")
```

## Requirements

- Python 3.7 or higher
- Google Cloud SDK installed and authenticated

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## Support

For issues or feature requests, please open an issue on the [GitHub repository](https://github.com/your-repo/comfygcs).

