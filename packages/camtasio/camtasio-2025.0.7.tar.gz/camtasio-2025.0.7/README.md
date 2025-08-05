# Camtasio

A modern Python API and CLI for programmatically working with Camtasia projects.

## Overview

Camtasio provides a comprehensive toolkit for manipulating Camtasia project files (`.cmproj` directories containing `.tscproj` JSON files). It combines high-level object-oriented APIs with powerful low-level JSON manipulation capabilities for complete control over Camtasia projects.

### Key Features

- **📁 Project Management**: Read, modify, and save Camtasia projects (.tscproj files)
- **🎬 Timeline Operations**: List tracks, analyze clips, and manage markers
- **📐 Spatial Scaling**: Resize projects to different resolutions (`xyscale`)
- **⏱️ Temporal Scaling**: Change playback speed with audio preservation (`timescale`)
- **📁 Media Management**: List, clean, and replace media files (`media-ls`, `media-rm`, `media-replace`)
- **🎯 Batch Processing**: Apply operations across multiple projects (`batch`)
- **🔧 Rich CLI Tools**: Command-line interface with beautiful terminal output
- **📊 Project Analysis**: Detailed statistics, complexity scoring, and recommendations
- **✅ Version Compatibility**: Support for Camtasia 2018-2025+ (v1.0-v9.0)

## Installation

```bash
pip install camtasio
```

For development:
```bash
git clone https://github.com/yourusername/camtasio.git
cd camtasio
uv venv
uv sync
```

## Quick Start

### Command Line Interface

```bash
# Get project information
camtasio info my_project.tscproj --detailed

# Scale project spatially by 1.5x
camtasio xyscale my_project.tscproj 1.5 scaled_project.tscproj

# Scale timeline temporally (double speed)
camtasio timescale my_project.tscproj 2.0 fast_project.tscproj

# List and clean media
camtasio media_ls my_project.tscproj --detailed
camtasio media_rm my_project.tscproj  # Remove unused media

# Batch process multiple projects
camtasio batch "projects/*.tscproj" info --detailed

# List timeline tracks and markers
camtasio track_ls my_project.tscproj --detailed
camtasio marker_ls my_project.tscproj

# Generate comprehensive analysis report
camtasio analyze my_project.tscproj
```

### Python API

```python
from camtasio import ProjectLoader, ProjectSaver, PropertyTransformer, TransformConfig, TransformType
from camtasio.serialization import load_json_file

# Load a project (low-level JSON approach)
project_data = load_json_file("my_project.tscproj")

# Scale spatially using transform engine
config = TransformConfig(TransformType.SPATIAL, factor=1.5)
transformer = PropertyTransformer(config)
scaled_data = transformer.transform_dict(project_data)

# Save result
saver = ProjectSaver()
saver.save_dict(scaled_data, "scaled_project.tscproj")

# Alternative: Using high-level Project model
from camtasio import Project

# Load using model-based approach  
loader = ProjectLoader()
project_data = loader.load("my_project.tscproj")
project = Project.from_dict(project_data)

# Scale the project
scaled_project = project.scale_spatial(1.5)

# Convert back to dict and save
scaled_data = scaled_project.to_dict()
saver.save_dict(scaled_data, "scaled_project.tscproj")
```

## Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `info` | Show project information and statistics | `camtasio info project.tscproj --detailed` |
| `validate` | Check project integrity | `camtasio validate project.tscproj` |
| `xyscale` | Scale project dimensions | `camtasio xyscale project.tscproj 1.5` |
| `timescale` | Scale timeline duration | `camtasio timescale project.tscproj 0.5` |
| `media_ls` | List media bin contents | `camtasio media_ls project.tscproj --detailed` |
| `media_rm` | Remove unused media | `camtasio media_rm project.tscproj` |
| `media_replace` | Replace media paths | `camtasio media_replace project.tscproj old.mp4 new.mp4` |
| `track_ls` | List timeline tracks | `camtasio track_ls project.tscproj --detailed` |
| `marker_ls` | List timeline markers | `camtasio marker_ls project.tscproj` |
| `analyze` | Generate analysis report | `camtasio analyze project.tscproj` |
| `batch` | Process multiple files | `camtasio batch "*.tscproj" info` |
| `version` | Show version info | `camtasio version` |

## Project Structure

A Camtasia project (`.cmproj`) is a directory containing:
- `project.tscproj` - Main JSON project file
- `media/` - Imported media files
- macOS metadata files (bookmarks.plist, docPrefs)

The `.tscproj` file contains:
- Canvas dimensions and frame rate
- Source media bin with imported files
- Timeline with scenes, tracks, and clips
- Effects and annotations

## Advanced Usage

### Spatial Scaling

Resize projects while maintaining relative positions and proportions:

```python
from camtasio import ProjectLoader, ProjectSaver, Project

# Load project
loader = ProjectLoader()
project_data = loader.load("tutorial.tscproj")
project = Project.from_dict(project_data)

# Calculate scale factor for 1080p to 4K conversion
current_width = project.canvas.width  # e.g., 1920
target_width = 3840
scale_factor = target_width / current_width

# Scale the project
scaled_project = project.scale_spatial(scale_factor)

# Save result
saver = ProjectSaver()
saver.save_dict(scaled_project.to_dict(), "tutorial_4k.tscproj")
```

### Timeline Manipulation

```python
from camtasio.serialization import load_json_file

# Load project data for analysis
project_data = load_json_file("tutorial.tscproj")

# Analyze timeline structure
timeline = project_data.get("timeline", {})
scene_track = timeline.get("sceneTrack", {})
scenes = scene_track.get("scenes", [])

for scene_idx, scene in enumerate(scenes):
    print(f"Scene {scene_idx}: {scene.get('csml', {}).get('duration', 0)} duration")
    
    # Analyze tracks within scene
    tracks = scene.get("csml", {}).get("tracks", [])
    for track_idx, track in enumerate(tracks):
        track_id = track.get("trackId", "unknown")
        print(f"  Track {track_idx} (ID: {track_id})")
        
        # Analyze media clips
        for media_clip in track.get("medias", []):
            clip_name = media_clip.get("_name", "unnamed")
            start = media_clip.get("_start", 0)
            duration = media_clip.get("_duration", 0)
            print(f"    Clip: {clip_name} (start: {start}, duration: {duration})")
```

### Media Management

```python
from pathlib import Path
from camtasio.serialization import load_json_file

# Load and analyze media bin
project_data = load_json_file("tutorial.tscproj")
source_bin = project_data.get("sourceBin", [])

print(f"Total media items: {len(source_bin)}")

# List all media files and check existence
missing_files = []
for item in source_bin:
    name = item.get("_name", "unnamed")
    media_type = item.get("_type", "unknown")
    
    if "src" in item:
        media_path = Path(item["src"])
        exists = media_path.exists()
        status = "✓" if exists else "✗"
        
        print(f"{status} {name} ({media_type}): {media_path}")
        
        if not exists:
            missing_files.append(str(media_path))
    else:
        print(f"? {name} ({media_type}): No source path")

if missing_files:
    print(f"\nWarning: {len(missing_files)} files not found!")
```

## Architecture

Camtasio provides both high-level and low-level APIs:

- **High-Level API**: Object-oriented interface with `Project`, `Timeline`, `Track`, and `Clip` classes
- **Low-Level API**: Direct JSON manipulation for advanced operations
- **Domain Models**: Structured representations of project components
- **Operations Engine**: Recursive traversal for complex transformations

## Compatibility

- ✅ **Camtasia 2018-2025+**: Full support for v1.0-v9.0 formats
- ✅ **Cross-platform**: Windows, macOS, Linux
- ✅ **Python 3.11+**: Modern Python with type hints
- ✅ **Format versions**: v1.0, v4.0, v9.0 and future versions

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with modern Python tooling:
- 📦 `uv` and `hatch` for packaging
- 🔍 `ruff` for linting and formatting
- 🧪 `pytest` for testing
- 🎨 `rich` for beautiful CLI output
- 📝 `loguru` for structured logging