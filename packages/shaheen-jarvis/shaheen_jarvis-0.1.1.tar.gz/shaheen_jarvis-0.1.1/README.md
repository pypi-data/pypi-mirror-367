# Shaheen-Jarvis Framework

## Overview

Shaheen-Jarvis is a modular, extensible Python assistant framework with core functionality and plugin support. It includes predefined functions across categories, voice I/O capabilities, configuration management, and AI integration via OpenRouter.

## Installation

You can install Shaheen-Jarvis from PyPI:

```bash
pip install shaheen-jarvis
```

## Quick Start

### CLI Usage

Launch the Jarvis CLI:

```bash
jarvis --help
jarvis time
jarvis weather London
```

### Python Script Usage

```python
from jarvis.core.jarvis_engine import Jarvis

# Initialize Jarvis
jarvis = Jarvis()

# Use built-in functions
print(jarvis.call("tell_time"))
print(jarvis.call("tell_joke"))
print(jarvis.call("get_weather", "London"))

# Use AI functions (requires API key)
print(jarvis.call("chat_with_ai", "Hello, how are you?"))
```

## Features

- **Core Engine**: Function registration, alias support, and dynamic dispatch
- **Predefined Functions**: Time, date, jokes, email sending, weather updates, etc.
- **Plugin Support**: Load plugins from local paths
- **Voice I/O**: Speech recognition and text-to-speech capabilities
- **Intuitive CLI**: Interactive mode, history, and color output
- **AI Integration**: OpenRouter API for AI-driven capabilities
- **Web Functions**: Weather, news, translation, etc.
- **System Utilities**: System and network information, process management
- **Productivity Tools**: To-do lists, alarms, email functions

## Configuration

Configuration is managed through a YAML file (`jarvis_config.yaml`) and environment variables. Here's a sample:

```yaml
api_keys:
  news_api_key: ${NEWS_API_KEY}
  openai_api_key: ${OPENAI_API_KEY}
  weather_api_key: ${WEATHER_API_KEY}
email:
  email_address: ${EMAIL_ADDRESS}
  email_password: ${EMAIL_PASSWORD}
logging:
  level: INFO
  log_to_file: true
memory:
  notes_file: jarvis_notes.json
  store_context: true
  todos_file: jarvis_todos.json
plugins:
  auto_load: []
  plugin_directories:
  - ./jarvis/plugins
voice:
  enable_voice: false
  stt_backend: whisper
  tts_backend: pyttsx3
```

Ensure that all environment variables are set correctly.

## Examples

### Advanced Use

You can explore more advanced usages such as voice-controlled commands or more complex AI interactions in the sample scripts provided in the repository.

```bash
python example_advanced.py
python example_voice.py
```

### Speech Recognition Feature

To enable speech recognition, ensure your microphone is set up correctly. Below is a simple example:

```python
from jarvis.core.jarvis_engine import Jarvis
from jarvis.core.voice_io import VoiceIO

# Initialize Jarvis and VoiceIO
jarvis = Jarvis(enable_voice=True)
voice_io = VoiceIO(jarvis.config)

# Listen for a command
command = voice_io.listen()
if command:
    print(f"You said: {command}")
    response = jarvis.dispatch(command)
    print(f"Jarvis says: {response}")
    voice_io.speak(response)
```

## Contribution

For any contributions or feature requests, please check the issues on the GitHub repository.

## License

Shaheen-Jarvis is licensed under the MIT License.

---
