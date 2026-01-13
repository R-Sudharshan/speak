# Real-time Speech-to-Text with Vosk

This project provides low-latency offline speech recognition using Vosk, Flask, and sounddevice.

## Prerequisites

1.  **Python 3.x** installed.
2.  **Vosk Model**: You must download a Vosk model manually.
    -   Go to [Vosk Models](https://alphacephei.com/vosk/models).
    -   Download a lightweight model like `vosk-model-small-en-us-0.15`.
    -   Extract the downloaded zip file in this project directory.
    -   **Rename the extracted folder to `model`** (so the folder structure is `speak/model/`).

## Installation

Install the required Python packages:

```bash
pip install vosk sounddevice flask
```

If you are on Linux, you might need `libportaudio2`. On Windows/macOS, it is usually included.

## Usage

1.  Ensure your microphone is connected and set as the default recording device.
2.  Run the application:

    ```bash
    python app.py
    ```

3.  Open your browser and navigate to:
    [http://127.0.0.1:5000](http://127.0.0.1:5000)

4.  Click **Start** to begin captioning.
5.  Click **Stop** to halt immediately.

## Troubleshooting

-   **"Model not found"**: Ensure the folder is named exactly `model` and contains the files (not a nested folder like `model/vosk-model...`).
-   **Audio errors**: Check your default microphone in system settings.
