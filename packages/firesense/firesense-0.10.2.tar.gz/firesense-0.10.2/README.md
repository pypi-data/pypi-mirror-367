# FireSense

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

FireSense is a video feed analyzer that detects fires, powered by the Gemma 3N vision model.

<a href="https://youtu.be/16kw5rZLims">
  <img src="images/presentation.png" alt="FireSense Demo" width="800px">
</a>

## Pipeline

<img src="images/pipeline.png" alt="FireSense Pipeline" style="max-width: 800px;">



## Quick Start

### Installation

```bash
# Install pypi package
pip install firesense

or

# Install from source code:
uv pip install -e .
```

### Command Line Usage

```bash
# Analyze a YouTube video
firesense analyze <youtube_video_id>

# Launch demo with local server
firesense demo <youtube_video_id> --local

```



https://github.com/user-attachments/assets/b8fdba5b-bd2d-44c6-be4e-8fb6499b62a8





Ngrok Integration
```bash
# setup ngrok
ngrok config add-authtoken <your_ngrok_auth_key>

# Launch demo with local server and ngrok tunnel
firesense demo <youtube_video_id> --local --ngrok

```

### Python Usage

```python
from firesense import setup_model, infer

# Setup model
model, tokenizer = setup_model()

# Run inference
inference_result = infer(model, tokenizer, system_prompt, user_prompt, image_path)
```

## Features

- 🚀 **Fast Development**: Leverages uv for 10-100x faster dependency installation
- 📦 **Modern Packaging**: PEP 621 compliant with pyproject.toml
- 🔍 **Type Safety**: Full mypy strict mode support (uv run mypy src)
- ✅ **Testing**: Comprehensive pytest setup with coverage



## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and checks (`make check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Testing

```bash
# Install the project with development dependencies using:
uv pip install -e ".[dev]"

# Run the tests with:
uv run pytest

```

## Type Safety

```bash
# Full mypy strict mode support 
uv run mypy src
```

## Releasing

New releases are manually pushed to pypi:

```bash

make publish
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
