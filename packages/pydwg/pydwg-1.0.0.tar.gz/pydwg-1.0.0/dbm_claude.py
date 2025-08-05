import math
import pyautocad
from pyautocad import Autocad, APoint
from myAutoCAD import myAutoCAD
from config import BASE_POINT
from dbm import DBM

def main():
    print("Starting AutoCAD Drilling Pattern Generator...")
    print("Make sure AutoCAD is installed and accessible.")
    try:
        acad = myAutoCAD()
        dbm = DBM(acad)
        # Pattern parameters (can be adjusted based on requirements)
        params = {
            'tunnel_radius': 2.5,
            'center': BASE_POINT,
            'hole_diameter': 0.045,
            'burden': 0.8,
            'spacing': 0.9,
            'cut_holes_radius': 0.6,
            'cut_hole_count': 6,
            'empty_holes_count': 2,
            'ring_count': 3,
            'holes_per_ring': [8, 12, 16],
            'ring_radii': [1.2, 1.8, 2.3],
            'contour_holes': 20,
            'colors': {
                'cut': 1, 'empty': 2, 'production': 3, 'contour': 4, 'perimeter': 5
            }
        }
        dbm.draw_parallel_cut_cylindrical_pattern(params)
        acad.zoom_extents()
        # Save the drawing
        save_path = input("Enter path to save drawing (or press Enter to skip): ")
        if save_path.strip():
            try:
                acad.doc.SaveAs(save_path)
                print(f"Drawing saved to: {save_path}")
            except Exception as e:
                print(f"Error saving file: {e}")
        print("\nPattern generation complete!")
        print("Legend:")
        print("- Red circles (C): Cut holes")
        print("- Yellow circles (E): Empty holes (relief)")
        print("- Green circles (P): Production holes")
        print("- Cyan circles (S): Contour/smooth holes")
        print("- Blue circle: Tunnel outline")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure AutoCAD is running and pyautocad is installed:")
        print("pip install pyautocad")

if __name__ == "__main__":
    main()