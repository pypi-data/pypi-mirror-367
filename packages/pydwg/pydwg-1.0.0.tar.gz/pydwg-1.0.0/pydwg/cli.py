#!/usr/bin/env python3
"""
Command-line interface for PyDWG drilling pattern generator.
"""

import sys
from .generator import FourSectionCutGenerator
from myAutoCAD import myAutoCAD


def main():
    """Main CLI function."""
    print("PyDWG - Drilling Pattern Generator")
    print("==================================")
    print("To use: Draw your tunnel profile using Lines and Arcs on the '0_dbm_polyline' layer in AutoCAD.")

    try:
        acad = myAutoCAD()
        generator = FourSectionCutGenerator(acad)
        
        # Read tunnel outline
        tunnel_outline_vertices = generator.read_tunnel_outline_from_layer("0_dbm_polyline")

        if not tunnel_outline_vertices:
            print("\nNo Lines, Arcs, or Polylines found on '0_dbm_polyline' layer!")
            print("Please draw a closed tunnel outline on this layer.")
            return 1

        print(f"Successfully processed tunnel outline with {len(tunnel_outline_vertices)} vertices.")

        center, radius = generator.calculate_tunnel_center_and_radius(tunnel_outline_vertices)
        if not center:
            print("Error: Could not calculate tunnel center and radius.")
            return 1

        print(f"Calculated center: ({center[0]:.2f}, {center[1]:.2f})")
        print(f"Calculated radius: {radius:.2f}m")

        # Get user input
        try:
            advance_length = float(input("Enter advance length (m) [default: 3.5]: ") or "3.5")
            hole_diameter = float(input("Enter hole diameter (mm) [default: 45]: ") or "45") / 1000
        except ValueError:
            print("Error: Invalid input. Please enter numeric values.")
            return 1

        # Calculate parameters
        df, dl, sections = generator.calculate_four_section_parameters(hole_diameter, advance_length)
        
        print(f"\nCalculated parameters:")
        print(f"Equivalent empty hole diameter: {df:.0f}mm")
        print(f"Empty hole diameter to drill: {dl:.0f}mm")
        
        # Generate patterns
        cut_holes = generator.generate_four_section_cut_pattern(center, sections, hole_diameter, dl)
        stoping_holes = generator.generate_stoping_pattern(tunnel_outline_vertices, cut_holes, center, hole_diameter)
        contour_holes = generator.generate_contour_holes(tunnel_outline_vertices, hole_diameter)
        
        all_holes = cut_holes + stoping_holes + contour_holes

        print(f"\nGenerated drilling pattern:")
        print(f"Empty holes: {len([h for h in all_holes if h['type'] == 'empty'])}")
        print(f"Cut holes: {len([h for h in all_holes if h['type'] == 'cut'])}")
        print(f"Stoping holes: {len([h for h in all_holes if h['type'] == 'stoping'])}")
        print(f"Contour holes: {len([h for h in all_holes if h['type'] == 'contour'])}")
        print(f"Total holes: {len(all_holes)}")

        # Draw the pattern
        generator.draw_drilling_pattern(all_holes, tunnel_outline_vertices)
        generator.add_pattern_info(center, radius, advance_length, hole_diameter)
        acad.zoom_extents()

        # Save option
        save_path = input("\nEnter path to save drawing (or press Enter to skip): ")
        if save_path.strip():
            try:
                acad.doc.SaveAs(save_path)
                print(f"Drawing saved to: {save_path}")
            except Exception as e:
                print(f"Error saving file: {e}")

        print("\nPattern generation complete!")
        return 0

    except ImportError as e:
        print(f"Error: Could not import required modules. {e}")
        print("Please ensure AutoCAD is running and pyautocad is installed.")
        return 1
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nAn unexpected error occurred: {e}")
        print("Please ensure AutoCAD is running.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 