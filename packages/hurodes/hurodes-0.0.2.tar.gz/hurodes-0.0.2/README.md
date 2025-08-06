# hurodes

hurodes (Humanoid Robot Description) is a Python toolkit for describing, converting, and processing humanoid robot models. The project introduces a custom HRDF (Humanoid Robot Description Format) that serves as a unified intermediate bridge for conversions between mainstream robot description formats such as MJCF and URDF. It provides generators, parsers, and common scripts to help users efficiently create, convert, and batch process robot models.

---

## Core Features

- **HRDF Unified Intermediate Format**: Uses a structured HRDF directory (CSV + JSON + Mesh) to describe robot information, making batch editing and analysis easy.
- **Flexible Generators/Parsers**: Supports bidirectional conversion between MJCF ⇆ HRDF ⇆ URDF to meet multi-format collaboration needs.
- **Multi-Robot Merging**: Through a name prefix mechanism, multiple robot models can be automatically merged into a single MJCF file, supporting collaborative/group simulation.
- **Scripted Batch Processing**: Built-in command-line scripts make format conversion, model merging, and other common tasks easy.
- **Modular Design**: Clear package structure for easy secondary development and feature extension.

---

## Installation

This project is based on Python 3.8 and above.

```bash
# Clone the repository
git clone https://github.com/your-org/humanoid-robot-description.git
cd humanoid-robot-description

# Standard installation
pip install .

# Developer installation (includes test dependencies)
pip install -e .[dev]
```

---

## Quick Start

The following examples demonstrate the main script usage for model conversion and visualization:

```bash
# Parse URDF or MJCF to HRDF (choose format_type: 'urdf' or 'mjcf')
python scripts/parse.py --input_path path/to/robot.urdf --robot_name your_robot_name --format_type urdf

# Generate MJCF from HRDF and visualize
python scripts/generate.py --robot_name your_robot_name

# Compose multiple robots (from HRDF) into a single MJCF and visualize
python scripts/generate_composite.py --robot_names robot1,robot2
```

---

## HRDF Format Overview

HRDF stores robot information in a directory structure:

```
assets/robots/your_robot_name/
├── actuator.csv     # Actuator parameters
├── body.csv         # Rigid body information
├── collision.csv    # Collision parameters
├── joint.csv        # Joint information
├── mesh.csv         # Mesh file index
├── meshes/          # Mesh resources
└── meta.json        # Metadata (tree structure, ground parameters, etc.)
```

- **Intermediate Bridge**: Serves as a unified data carrier during conversions between MJCF, URDF, and other formats.
- **Structured Storage**: CSV/JSON files are easy for batch reading, analysis, and version control.
- **Extensible**: Clear directory structure makes it easy to add new attributes or support new formats.
- **Project Cache**: Temporary data generated at runtime is stored in the user's home directory under `~/.hurodes`, with no manual maintenance required.