import math
import pyautocad
from pyautocad import Autocad, APoint
from myAutoCAD import myAutoCAD
from config import BASE_POINT
from dbm import DBM


class FourSectionCutGenerator:
    def __init__(self, acad: myAutoCAD):
        self.acad = acad
        self.model = acad.model
        self.doc = acad.doc
        self.dbm = DBM(acad)

    def read_polyline_from_layer(self, layer_name="0_dbm_polyline"):
        """Read polyline from specified layer and extract vertices"""
        polylines = []
        try:
            # Iterate through all entities in model space
            for entity in self.model:
                if entity.ObjectName == "AcDbPolyline" and entity.Layer == layer_name:
                    # Get polyline vertices
                    vertices = []
                    coords = entity.Coordinates
                    # Coordinates come as a flat list (x1, y1, x2, y2, ...)
                    for i in range(0, len(coords), 2):
                        vertices.append((coords[i], coords[i+1]))
                    polylines.append(vertices)
        except Exception as e:
            print(f"Error reading polyline: {e}")
        return polylines

    def calculate_tunnel_center_and_radius(self, vertices):
        """Calculate center and approximate radius from polyline vertices"""
        if not vertices:
            return None, None

        # Calculate centroid
        cx = sum(v[0] for v in vertices) / len(vertices)
        cy = sum(v[1] for v in vertices) / len(vertices)
        center = (cx, cy)

        # Calculate average radius
        distances = [math.sqrt((v[0]-cx)**2 + (v[1]-cy)**2) for v in vertices]
        radius = sum(distances) / len(distances)

        return center, radius

    def calculate_four_section_parameters(self, hole_diameter, advance_length):
        """Calculate parameters for four-section cut based on PDF formulas"""
        # From PDF equation 18.1: df = 3.2 * sqrt(l^2)
        df = ((3.2 * advance_length)**2)/1000

        # For single large hole
        dl = df

        # From PDF equation 18.3: v = 1.5 * df
        v1 = 1.5 * df  # Burden for first section

        # Calculate parameters for each section based on Table 18.2
        sections = []

        # First square cut
        B1 = v1
        X1 = B1 * math.sqrt(2)
        St1 = B1
        sections.append({
            'burden': B1,
            'spacing': X1,
            'stemming': St1,
            'section': 1
        })

        # Second square
        B2 = B1 * math.sqrt(2)
        X2 = 1.5 * B2 * math.sqrt(2)
        St2 = B1 * math.sqrt(2) / 2
        sections.append({
            'burden': B2,
            'spacing': X2,
            'stemming': St2,
            'section': 2
        })

        # Third square
        B3 = 1.5 * B2 * math.sqrt(2)
        X3 = 1.5 * B3 * math.sqrt(2)
        St3 = math.sqrt(2) / 2 * (B1 * math.sqrt(2) / 2 + B2)
        sections.append({
            'burden': B3,
            'spacing': X3,
            'stemming': St3,
            'section': 3
        })

        # Fourth square
        B4 = 1.5 * B3 * math.sqrt(2)
        X4 = 1.5 * B4 * math.sqrt(2)
        St4 = math.sqrt(2) / 2 * (math.sqrt(2) / 2 *
                                  B1 * math.sqrt(2) / 2 + B2 + B3)
        sections.append({
            'burden': B4,
            'spacing': X4,
            'stemming': St4,
            'section': 4
        })

        return df, dl, sections

    def generate_four_section_cut_pattern(self, center, sections, hole_diameter, empty_hole_diameter):
        """Generate the four-section cut hole pattern"""
        holes = []

        # Central empty hole
        holes.append({
            'position': center,
            'diameter': empty_hole_diameter,
            'type': 'empty',
            'section': 0,
            'color': 2,  # Yellow for empty hole
            'label': 'E1'
        })

        # Generate holes for each section
        hole_number = 1
        for section_data in sections:
            section = section_data['section']
            burden = section_data['burden']
            spacing = section_data['spacing']

            # Calculate positions for square pattern
            positions = self.calculate_square_positions(
                center, spacing / 2, section)

            for pos in positions:
                # Check if position is within acceptable burden from previous section
                if self.is_valid_position(pos, holes, burden):
                    holes.append({
                        'position': pos,
                        'diameter': hole_diameter,
                        'type': 'cut',
                        'section': section,
                        'color': 1,  # Red for cut holes
                        'label': f'C{hole_number}'
                    })
                    hole_number += 1

        return holes

    def calculate_square_positions(self, center, half_side, section):
        """Calculate positions for holes in a square pattern"""
        positions = []
        cx, cy = center

        # Rotate each section by 45 degrees relative to previous
        base_angle = (section - 1) * math.pi / 4

        # Four corners of the square
        angles = [0, math.pi/2, math.pi, 3*math.pi/2]

        for angle in angles:
            total_angle = base_angle + angle
            x = cx + half_side * math.sqrt(2) * math.cos(total_angle)
            y = cy + half_side * math.sqrt(2) * math.sin(total_angle)
            positions.append((x, y))

        return positions

    def is_valid_position(self, pos, existing_holes, max_burden):
        """Check if position maintains proper burden from existing holes"""
        if not existing_holes:
            return True

        for hole in existing_holes:
            dist = math.sqrt((pos[0] - hole['position'][0])**2 +
                             (pos[1] - hole['position'][1])**2)
            if dist < max_burden * 0.8:  # Allow some tolerance
                return False
        return True

    def generate_stoping_pattern(self, center, tunnel_radius, cut_holes, hole_diameter):
        """Generate stoping holes around the cut"""
        stoping_holes = []
        hole_number = 1

        # Calculate the extent of cut area
        cut_extent = max([math.sqrt((h['position'][0]-center[0])**2 +
                                    (h['position'][1]-center[1])**2)
                         for h in cut_holes if h['type'] == 'cut'])

        # Generate rings of stoping holes
        # 0.5m spacing between rings
        num_rings = int((tunnel_radius - cut_extent) / 0.5)

        for ring in range(1, num_rings + 1):
            radius = cut_extent + ring * 0.5
            num_holes = int(2 * math.pi * radius / 0.6)  # 0.6m spacing

            positions = self.acad.calculate_points_on_circle(
                center, radius, num_holes)

            for pos in positions:
                # Check if within tunnel boundary
                if math.sqrt((pos[0]-center[0])**2 + (pos[1]-center[1])**2) < tunnel_radius - 0.2:
                    stoping_holes.append({
                        'position': pos,
                        'diameter': hole_diameter,
                        'type': 'stoping',
                        'color': 3,  # Green
                        'label': f'S{hole_number}'
                    })
                    hole_number += 1

        return stoping_holes

    def generate_contour_holes(self, center, tunnel_radius, hole_diameter):
        """Generate contour holes for smooth blasting"""
        contour_holes = []

        # Contour holes at 0.3m from tunnel perimeter
        contour_radius = tunnel_radius - 0.3
        spacing = 0.4  # Closer spacing for smooth blasting
        num_holes = int(2 * math.pi * contour_radius / spacing)

        positions = self.acad.calculate_points_on_circle(
            center, contour_radius, num_holes)

        for i, pos in enumerate(positions):
            contour_holes.append({
                'position': pos,
                'diameter': hole_diameter * 0.8,  # Smaller diameter for contour
                'type': 'contour',
                'color': 4,  # Cyan
                'label': f'P{i+1}'
            })

        return contour_holes

    def draw_drilling_pattern(self, holes, tunnel_outline=None):
        """Draw the complete drilling pattern"""
        # Setup layers
        layers = {
            'CUT_HOLES': 1,
            'EMPTY_HOLES': 2,
            'STOPING_HOLES': 3,
            'CONTOUR_HOLES': 4,
            'TUNNEL_OUTLINE': 5,
            'ANNOTATIONS': 7
        }
        self.acad.setup_layers(layers)

        # Draw tunnel outline if provided
        if tunnel_outline:
            self.doc.ActiveLayer = self.doc.Layers.Item('TUNNEL_OUTLINE')
            for i in range(len(tunnel_outline)):
                p1 = tunnel_outline[i]
                p2 = tunnel_outline[(i+1) % len(tunnel_outline)]
                line = self.model.AddLine(
                    APoint(p1[0], p1[1]), APoint(p2[0], p2[1]))
                line.color = 5

        # Draw holes
        for hole in holes:
            # Select layer based on hole type
            if hole['type'] == 'empty':
                layer = 'EMPTY_HOLES'
            elif hole['type'] == 'cut':
                layer = 'CUT_HOLES'
            elif hole['type'] == 'stoping':
                layer = 'STOPING_HOLES'
            elif hole['type'] == 'contour':
                layer = 'CONTOUR_HOLES'
            else:
                layer = 'CUT_HOLES'

            # Draw hole
            self.acad.draw_circle(hole['position'], hole['diameter']/2,
                                  hole['color'], layer)

            # Add label
            if 'label' in hole:
                text_pos = (hole['position'][0] + hole['diameter']*0.75,
                            hole['position'][1] + hole['diameter']*0.75)
                self.acad.draw_text(text_pos, hole['label'], 0.05,
                                    hole['color'], 'ANNOTATIONS')

    def add_pattern_info(self, center, tunnel_radius, advance_length, hole_diameter):
        """Add pattern information and legend"""
        # Title
        title_pos = (center[0] - tunnel_radius, center[1] + tunnel_radius + 1)
        self.acad.draw_text(
            title_pos, "FOUR-SECTION CUT DRILLING PATTERN", 0.2, 7)

        # Pattern specifications
        info_y = title_pos[1] - 0.3
        specs = [
            f"Advance Length: {advance_length}m",
            f"Hole Diameter: {hole_diameter*1000:.0f}mm",
            f"Pattern Type: Four-Section Parallel Cut",
            f"Generated from: dbm_polyline layer"
        ]

        for i, spec in enumerate(specs):
            pos = (title_pos[0], info_y - i * 0.15)
            self.acad.draw_text(pos, spec, 0.1, 7)

        # Legend
        legend_x = center[0] + tunnel_radius + 1
        legend_y = center[1] + tunnel_radius
        legend_items = [
            ("Empty Hole (Relief)", 2, "E"),
            ("Cut Holes", 1, "C"),
            ("Stoping Holes", 3, "S"),
            ("Contour Holes", 4, "P"),
            ("Tunnel Outline", 5, "")
        ]

        self.acad.draw_text((legend_x, legend_y + 0.3), "LEGEND", 0.15, 7)

        for i, (label, color, prefix) in enumerate(legend_items):
            y_pos = legend_y - i * 0.3
            self.acad.draw_circle((legend_x, y_pos), 0.05, color)
            self.acad.draw_text(
                (legend_x + 0.2, y_pos - 0.05), label, 0.12, color)


def main():
    print("Starting Four-Section Cut Pattern Generator...")
    print("Make sure AutoCAD is running and has a polyline on '0_dbm_polyline' layer")

    try:
        # Initialize AutoCAD connection
        acad = myAutoCAD()
        generator = FourSectionCutGenerator(acad)

        # Read polyline from layer
        polylines = generator.read_polyline_from_layer("0_dbm_polyline")

        if not polylines:
            print("No polyline found on '0_dbm_polyline' layer!")
            print(
                "Please create a closed polyline representing the tunnel outline on this layer.")
            return

        # Use first polyline found
        tunnel_outline = polylines[0]
        print(f"Found polyline with {len(tunnel_outline)} vertices")

        # Calculate tunnel center and radius
        center, radius = generator.calculate_tunnel_center_and_radius(
            tunnel_outline)
        print(f"Calculated center: ({center[0]:.2f}, {center[1]:.2f})")
        print(f"Calculated radius: {radius:.2f}m")

        # Get drilling parameters from user
        advance_length = float(
            input("Enter advance length (m) [default: 3.5]: ") or "3.5")
        hole_diameter = float(
            input("Enter hole diameter (mm) [default: 45]: ") or "45") / 1000

        # Calculate four-section cut parameters
        df, dl, sections = generator.calculate_four_section_parameters(
            hole_diameter, advance_length)

        print(f"\nCalculated parameters:")
        print(f"Equivalent empty hole diameter: {df:.0f}mm")
        print(f"Empty hole diameter to drill: {dl:.0f}mm")

        # Generate cut pattern
        cut_holes = generator.generate_four_section_cut_pattern(center, sections,
                                                                hole_diameter, dl)

        # Generate stoping pattern
        stoping_holes = generator.generate_stoping_pattern(center, radius, cut_holes,
                                                           hole_diameter)

        # Generate contour holes
        contour_holes = generator.generate_contour_holes(
            center, radius, hole_diameter)

        # Combine all holes
        all_holes = cut_holes + stoping_holes + contour_holes

        print(f"\nGenerated drilling pattern:")
        print(
            f"Empty holes: {len([h for h in all_holes if h['type'] == 'empty'])}")
        print(
            f"Cut holes: {len([h for h in all_holes if h['type'] == 'cut'])}")
        print(
            f"Stoping holes: {len([h for h in all_holes if h['type'] == 'stoping'])}")
        print(
            f"Contour holes: {len([h for h in all_holes if h['type'] == 'contour'])}")
        print(f"Total holes: {len(all_holes)}")

        # Draw the pattern
        generator.draw_drilling_pattern(all_holes, tunnel_outline)

        # Add pattern information
        generator.add_pattern_info(
            center, radius, advance_length, hole_diameter)

        # Zoom to extents
        acad.zoom_extents()

        # Save option
        save_path = input(
            "\nEnter path to save drawing (or press Enter to skip): ")
        if save_path.strip():
            try:
                acad.doc.SaveAs(save_path)
                print(f"Drawing saved to: {save_path}")
            except Exception as e:
                print(f"Error saving file: {e}")

        print("\nPattern generation complete!")
        print("\nTo use this script:")
        print("1. Draw a closed polyline representing your tunnel outline")
        print("2. Place it on a layer named '0_dbm_polyline'")
        print("3. Run this script")
        print("\nThe script will generate a proper four-section cut pattern based on")
        print("the formulas and principles from the Underground Excavation handbook.")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure:")
        print("1. AutoCAD is running")
        print("2. A polyline exists on '0_dbm_polyline' layer")
        print("3. pyautocad is installed (pip install pyautocad)")


if __name__ == "__main__":
    main()
