# SKCV-Toolkit - Santhosh Kumar Computer Vision Toolkit

A comprehensive computer vision toolkit for image processing and analysis.

## Features

- **Histogram Equalization**: Various equalization methods for image enhancement
- **Filter Operations**: High-pass and low-pass filters for image processing
- **Neighborhood Operations**: Custom filters and neighborhood analysis
- **GUI Tools**: Interactive tools for image processing

## Installation

```bash
pip install skcv-toolkit
```

## Usage

```python
import skcv

# Use histogram equalization
from skcv.he.methods import equalizers

# Use filters
from skcv.hplp.filters import filters

# Use neighborhood operations
from skcv.neigh import custom_gui_filter
```

## Requirements

- Python 3.7+
- NumPy
- OpenCV
- Matplotlib
- Pillow
- scikit-image
