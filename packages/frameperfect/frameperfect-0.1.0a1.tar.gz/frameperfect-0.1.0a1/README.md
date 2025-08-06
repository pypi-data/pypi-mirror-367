# FramePerfect

A lightweight GUI application for precise frame-by-frame video analysis and screenshot extraction, built with PySide/PyQt and OpenCV.

## Why This Tool?

- **Perfect for**: Video editors, forensic analysts, researchers, and anyone needing precise frame analysis
- **Advantages over media players**: 
  - Guaranteed frame accuracy (no skipped frames)
  - Dedicated screenshot workflow
  - Clean interface without unnecessary features
- **Multi-file sequential processing**: Provide multiple video files and automatically advance to the next when closing (New!)

## Key Features

- **Frame-accurate navigation**: Move through videos one frame at a time with perfect precision
- **Instant screenshot capture**: Save any frame as PNG/JPEG with customizable paths
- **Simple workflow**: Open -> Navigate -> Capture -> Repeat
- **Visual timeline**: Quickly jump to any frame using the position slider
- **Compatibility**: Supports Python 2+ and PyQt4/PyQt5/PyQt6/PySide/PySide2/PySide6

## Installation

```bash
pip install frameperfect
```

## Usage

### Option 1: Interactive Mode

```bash
python -m frameperfect
```

1. Click "Open Video" and select your video file
2. Use navigation controls:
   - **Previous/Next Frame**: Move precisely through frames
   - **Slider**: Jump to any position
   - **Save Frame**: Capture current frame

### Option 2: Sequential Batch Mode (New!)

```bash
python -m frameperfect video1.mp4 video2.mp4 video3.mp4
```
- 
- Automatically opens `video1.mp4` first
- When window closes, immediately opens `video2.mp4`
- Process repeats until all videos are processed
- Perfect for reviewing multiple clips in one session

### Basic Workflow

1. Click "Open Video" and select your video file
2. Use these controls:
   - **Previous/Next Frame**: Move precisely through frames
   - **Slider**: Jump to any position in the video
   - **Save Frame**: Capture the current frame to your Pictures folder

## Troubleshooting

- If video doesn't open: Try converting to MP4 with H.264 codec
- For large videos: Consider splitting files for better performance

## Contributing

Contributions are welcome! Please submit pull requests or open issues on GitHub.

## License

AGPL-3.0 - See [LICENSE](LICENSE) for details.