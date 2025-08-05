# PyDWG - Drilling Pattern Generator

A Python package for generating drilling patterns for tunnel excavation based on AutoCAD polylines. This tool creates optimized drilling patterns for various tunnel shapes, supporting both circular and arbitrary polyline geometries.

## Features

- **Multi-format Input**: Supports AutoCAD Lines, Arcs, and Polylines
- **Flexible Geometry**: Works with both circular and arbitrary tunnel shapes
- **Four-Section Cut Pattern**: Implements industry-standard four-section parallel cut patterns
- **Automatic Pattern Generation**: 
  - Cut holes (central relief and cutting pattern)
  - Stoping holes (interior grid pattern)
  - Contour holes (perimeter smooth blasting)
- **High-Fidelity Processing**: Handles complex geometries with arc tessellation
- **AutoCAD Integration**: Direct drawing and layer management

## Installation

```bash
pip install pydwg
```

## Quick Start

### Prerequisites

1. **AutoCAD**: Must be running and accessible
2. **Python**: 3.7 or higher
3. **Dependencies**: pyautocad, numpy

### Basic Usage

1. **Draw your tunnel outline** in AutoCAD on a layer named `0_dbm_polyline`
2. **Run the generator**:

```python
from pydwg import FourSectionCutGenerator
from myAutoCAD import myAutoCAD

# Initialize
acad = myAutoCAD()
generator = FourSectionCutGenerator(acad)

# Read tunnel outline
tunnel_outline = generator.read_tunnel_outline_from_layer("0_dbm_polyline")

# Generate pattern
center, radius = generator.calculate_tunnel_center_and_radius(tunnel_outline)
advance_length = 3.5  # meters
hole_diameter = 0.045  # meters (45mm)

# Calculate parameters
df, dl, sections = generator.calculate_four_section_parameters(hole_diameter, advance_length)

# Generate all hole patterns
cut_holes = generator.generate_four_section_cut_pattern(center, sections, hole_diameter, dl)
stoping_holes = generator.generate_stoping_pattern(tunnel_outline, cut_holes, center, hole_diameter)
contour_holes = generator.generate_contour_holes(tunnel_outline, hole_diameter)

# Draw the pattern
all_holes = cut_holes + stoping_holes + contour_holes
generator.draw_drilling_pattern(all_holes, tunnel_outline)
```

### Command Line Interface

```bash
pydwg
```

This will prompt you for:
- Advance length (default: 3.5m)
- Hole diameter (default: 45mm)

## Advanced Features

### Custom Pattern Types

The package supports different drilling pattern types:

- **Four-Section Cut**: Industry standard for tunnel excavation
- **General Polyline**: Works with any closed polyline shape
- **Contour Holes**: Smooth blasting along tunnel perimeter
- **Stoping Holes**: Interior grid pattern for bulk excavation

### Geometry Processing

- **Arc Tessellation**: Converts AutoCAD arcs to high-fidelity vertex sequences
- **Segment Ordering**: Automatically orders disconnected segments into continuous paths
- **Polygon Analysis**: Calculates weighted centroids and areas
- **Offset Operations**: Creates parallel paths for contour holes

### AutoCAD Integration

- **Layer Management**: Automatic layer creation and organization
- **Entity Drawing**: Circles, lines, and text annotations
- **Color Coding**: Different colors for different hole types
- **Zoom and Save**: Automatic view management and file saving

## API Reference

### Main Classes

#### `FourSectionCutGenerator`

The main class for generating drilling patterns.

**Methods:**
- `read_tunnel_outline_from_layer(layer_name)`: Read geometry from AutoCAD layer
- `calculate_tunnel_center_and_radius(vertices)`: Calculate weighted centroid and radius
- `generate_four_section_cut_pattern(center, sections, hole_diameter, empty_hole_diameter)`: Generate cut pattern
- `generate_stoping_pattern(tunnel_outline, cut_holes, center, hole_diameter)`: Generate stoping holes
- `generate_contour_holes(tunnel_outline, hole_diameter)`: Generate contour holes
- `draw_drilling_pattern(holes, tunnel_outline)`: Draw pattern in AutoCAD

### Configuration

The package uses several configurable parameters:

- **Contour offset**: Distance from tunnel perimeter (default: 0.3m)
- **Stoping spacing**: Grid spacing for interior holes (default: 0.8m)
- **Cut pattern**: Four-section parameters based on advance length
- **Hole diameters**: Different sizes for different hole types

## Examples

### Circular Tunnel

```python
# For circular tunnels, the pattern automatically adapts
# to the calculated radius and center
```

### Irregular Tunnel

```python
# For irregular shapes, the pattern follows the actual geometry
# with proper contour and stoping hole placement
```

### Custom Parameters

```python
# Customize pattern parameters
advance_length = 4.0  # meters
hole_diameter = 0.051  # meters (51mm)
contour_spacing = 0.35  # meters
stoping_burden = 0.9  # meters
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{pydwg,
  title={PyDWG - Drilling Pattern Generator},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/pydwg}
}
```

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/pydwg/issues)
- **Documentation**: [GitHub Wiki](https://github.com/yourusername/pydwg/wiki)
- **Email**: your.email@example.com

## Changelog

### Version 1.0.0
- Initial release
- Four-section cut pattern generation
- AutoCAD integration
- Support for arbitrary polyline geometries
- Arc tessellation and segment ordering 