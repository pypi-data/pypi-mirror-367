import math
from myAutoCAD import myAutoCAD
from config import BASE_POINT

# Configuration
TUNNEL_WIDTH = 5.0
TUNNEL_HEIGHT = 4.5
REAMER_HOLE_DIAMETER = 0.102
BLASTHOLE_DIAMETER = 0.045
RING_RADII = [0.25, 0.5, 0.8]
HOLES_PER_RING = [4, 8, 12]
CENTER_POINT = BASE_POINT


def main():
    acad = myAutoCAD()
    # Setup layers
    layers = {
        "TUNNEL_PROFILE": 1,
        "REAMER_HOLE": 2,
        "BLASTHOLES": 3,
        "CUT": 1,
        "EMPTY": 2,
        "PRODUCTION": 3,
        "CONTOUR": 4,
        "PERIMETER": 5
    }
    acad.setup_layers(layers)
    # Draw arched tunnel
    acad.draw_arched_tunnel(CENTER_POINT, TUNNEL_WIDTH, TUNNEL_HEIGHT)
    # Draw drilling pattern
    acad.draw_drilling_pattern(
        CENTER_POINT,
        REAMER_HOLE_DIAMETER,
        BLASTHOLE_DIAMETER,
        RING_RADII,
        HOLES_PER_RING
    )
    # Optionally, draw parallel cut pattern:
    # params = {...}  # see myAutoCAD class for keys
    # acad.draw_parallel_cut_cylindrical_pattern(params)
    acad.zoom_extents()
    print("Script finished. Check your AutoCAD window!")

if __name__ == "__main__":
    main()