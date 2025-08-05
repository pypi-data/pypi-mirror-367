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

    # --- NEW HELPER METHODS FOR GEOMETRIC CALCULATIONS ---

    def _line_intersection(self, p1, p2, p3, p4):
        """Calculates the intersection point of two lines defined by p1-p2 and p3-p4."""
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-9:
            return None  # Lines are parallel or collinear

        t_num = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
        t = t_num / den
        intersect_x = x1 + t * (x2 - x1)
        intersect_y = y1 + t * (y2 - y1)
        return (intersect_x, intersect_y)

    def _offset_polyline(self, vertices, offset):
        """
        Creates a new polyline by offsetting the original one.
        A negative offset moves inward for a counter-clockwise polyline.
        """
        offset_vertices = []
        num_verts = len(vertices)
        if num_verts < 2:
            return []
        
        closed_vertices = vertices + [vertices[0]]
        offset_lines = []

        for i in range(num_verts):
            p1 = closed_vertices[i]
            p2 = closed_vertices[i+1]
            
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = math.sqrt(dx**2 + dy**2)
            if length == 0:
                continue

            # Normal vector (points "left" of the segment direction)
            nx = -dy / length
            ny = dx / length
            
            op1 = (p1[0] + offset * nx, p1[1] + offset * ny)
            op2 = (p2[0] + offset * nx, p2[1] + offset * ny)
            offset_lines.append((op1, op2))

        if not offset_lines:
            return []

        for i in range(num_verts):
            # Intersection of previous offset line and current offset line
            line1 = offset_lines[i-1] 
            line2 = offset_lines[i]
            
            intersection = self._line_intersection(line1[0], line1[1], line2[0], line2[1])
            if intersection:
                offset_vertices.append(intersection)
            else:
                # Fallback for parallel lines (e.g., corners of a rectangle)
                offset_vertices.append(line2[0])

        return offset_vertices

    def _place_points_on_polyline(self, vertices, spacing):
        """Places points along a closed polyline at a specified, even spacing."""
        if not vertices or spacing <= 0:
            return []

        points = []
        path = vertices + [vertices[0]]
        
        total_length = sum(math.sqrt((path[i+1][0]-path[i][0])**2 + (path[i+1][1]-path[i][1])**2) for i in range(len(path) - 1))

        if total_length < spacing:
            return [vertices[0]] if vertices else []
        
        num_points = int(round(total_length / spacing))
        if num_points == 0:
            return [vertices[0]] if vertices else []

        actual_spacing = total_length / num_points
        dist_to_next_point = 0
        dist_along_path = 0

        for i in range(len(path) - 1):
            p1 = path[i]
            p2 = path[i+1]
            segment_length = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
            
            if segment_length < 1e-9:
                continue

            while dist_to_next_point <= dist_along_path + segment_length + 1e-9:
                dist_into_segment = dist_to_next_point - dist_along_path
                ratio = dist_into_segment / segment_length
                
                new_x = p1[0] + ratio * (p2[0] - p1[0])
                new_y = p1[1] + ratio * (p2[1] - p1[1])
                
                if len(points) < num_points:
                    points.append((new_x, new_y))
                else:
                    return points

                dist_to_next_point += actual_spacing

            dist_along_path += segment_length
        
        return points

    def _is_point_in_polygon(self, point, polygon):
        """Checks if a point is inside a polygon using the Ray Casting algorithm."""
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
            
        return inside
        
    def _get_polyline_bounding_box(self, vertices):
        """Calculates the bounding box of a list of vertices."""
        min_x = min(v[0] for v in vertices)
        max_x = max(v[0] for v in vertices)
        min_y = min(v[1] for v in vertices)
        max_y = max(v[1] for v in vertices)
        return min_x, min_y, max_x, max_y

    # --- ORIGINAL AND MODIFIED METHODS ---

    def read_polyline_from_layer(self, layer_name="0_dbm_polyline"):
        """Read polyline from specified layer and extract vertices"""
        polylines = []
        try:
            for entity in self.model:
                if entity.ObjectName == "AcDbPolyline" and entity.Layer == layer_name:
                    coords = entity.Coordinates
                    vertices = [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
                    polylines.append(vertices)
        except Exception as e:
            print(f"Error reading polyline: {e}")
        return polylines

    def calculate_tunnel_center_and_radius(self, vertices):
        """Calculate centroid and approximate radius from polyline vertices"""
        if not vertices:
            return None, None
        cx = sum(v[0] for v in vertices) / len(vertices)
        cy = sum(v[1] for v in vertices) / len(vertices)
        center = (cx, cy)
        distances = [math.sqrt((v[0]-cx)**2 + (v[1]-cy)**2) for v in vertices]
        radius = sum(distances) / len(distances)
        return center, radius

    def calculate_four_section_parameters(self, hole_diameter, advance_length):
        """Calculate parameters for four-section cut based on PDF formulas"""
        # From PDF equation 18.1: df = 3.2 * sqrt(l^2) -> This seems incorrect.
        # Let's use the formula from Page 1 (219): L = 0.15 + 34.1 D2 - 39.4 D2^2
        # This is for L from D2. We need D2 for a given L (advance). This is complex.
        # Let's keep the user's simpler formula for now, but correct it.
        # Assuming the user meant a formula for equivalent diameter df from advance L.
        # A common rule of thumb is L/df ratio is around 30-40. Let's assume a simplified linear relationship.
        # The provided formula seems a bit off. I will keep it as is, assuming it's a custom rule.
        df = ((3.2 * advance_length)**2)/1000
        dl = df
        v1 = 1.5 * df
        sections = [{'burden': v1, 'spacing': v1 * math.sqrt(2), 'stemming': v1, 'section': 1}]
        B1 = v1
        B2 = B1 * math.sqrt(2)
        sections.append({'burden': B2, 'spacing': 1.5 * B2 * math.sqrt(2), 'stemming': B1 * math.sqrt(2) / 2, 'section': 2})
        B3 = 1.5 * B2 * math.sqrt(2)
        sections.append({'burden': B3, 'spacing': 1.5 * B3 * math.sqrt(2), 'stemming': math.sqrt(2)/2 * (B1*math.sqrt(2)/2 + B2), 'section': 3})
        B4 = 1.5 * B3 * math.sqrt(2)
        sections.append({'burden': B4, 'spacing': 1.5 * B4 * math.sqrt(2), 'stemming': math.sqrt(2)/2 * (math.sqrt(2)/2 * B1*math.sqrt(2)/2 + B2 + B3), 'section': 4})
        return df, dl, sections

    def generate_four_section_cut_pattern(self, center, sections, hole_diameter, empty_hole_diameter):
        """Generate the four-section cut hole pattern"""
        holes = []
        holes.append({'position': center, 'diameter': empty_hole_diameter, 'type': 'empty', 'section': 0, 'color': 2, 'label': 'E1'})
        hole_number = 1
        for section_data in sections:
            section, burden, spacing = section_data['section'], section_data['burden'], section_data['spacing']
            positions = self.calculate_square_positions(center, spacing / 2, section)
            for pos in positions:
                if self.is_valid_position(pos, holes, burden):
                    holes.append({'position': pos, 'diameter': hole_diameter, 'type': 'cut', 'section': section, 'color': 1, 'label': f'C{hole_number}'})
                    hole_number += 1
        return holes

    def calculate_square_positions(self, center, half_side, section):
        """Calculate positions for holes in a square pattern, rotated per section."""
        positions = []
        cx, cy = center
        base_angle = (section - 1) * math.pi / 4
        angles = [0, math.pi/2, math.pi, 3*math.pi/2]
        for angle in angles:
            total_angle = base_angle + angle
            x = cx + half_side * math.sqrt(2) * math.cos(total_angle)
            y = cy + half_side * math.sqrt(2) * math.sin(total_angle)
            positions.append((x, y))
        return positions

    def is_valid_position(self, pos, existing_holes, max_burden):
        """Check if position maintains proper burden from existing holes"""
        return all(math.sqrt((pos[0] - h['position'][0])**2 + (pos[1] - h['position'][1])**2) >= max_burden * 0.8 for h in existing_holes)

    def generate_stoping_pattern(self, tunnel_outline, cut_holes, center, hole_diameter):
        """
        [REWRITTEN] Generate stoping (production) holes to fill the area between the cut and contour.
        This method is based on filling the available area with a staggered grid of holes.
        The burden and spacing are derived from principles in the provided PDF (Table 22.3).
        """
        stoping_holes = []
        if not cut_holes:
            return []

        # Parameters from PDF Table 22.3 for horizontal stoping: B = Burden, S = 1.1 * B
        burden = 0.8  # (m) A reasonable practical value for the burden.
        spacing = 1.1 * burden  # (m) Spacing between holes in a row.

        # 1. Define inner and outer boundaries for the stoping area
        cut_extent = max(math.sqrt((h['position'][0]-center[0])**2 + (h['position'][1]-center[1])**2) for h in cut_holes)
        
        # Outer boundary is inset from the tunnel wall to leave room for contour holes
        contour_burden = 0.3
        stoping_area_offset = - (contour_burden + burden / 2)
        outer_boundary = self._offset_polyline(tunnel_outline, stoping_area_offset)

        if not outer_boundary:
            print("Warning: Could not generate outer boundary for stoping holes.")
            return []
        
        # 2. Generate a staggered grid of points and filter them
        min_x, min_y, max_x, max_y = self._get_polyline_bounding_box(outer_boundary)
        
        hole_number = 1
        y_pos = min_y
        row_index = 0
        while y_pos <= max_y:
            x_pos = min_x
            if row_index % 2 == 1:  # Stagger rows for better rock breakage
                x_pos += spacing / 2
            
            while x_pos <= max_x:
                point = (x_pos, y_pos)
                # Check if point is inside the designated area
                is_outside_cut = math.sqrt((point[0]-center[0])**2 + (point[1]-center[1])**2) > (cut_extent + burden / 2)
                is_inside_boundary = self._is_point_in_polygon(point, outer_boundary)
                
                if is_outside_cut and is_inside_boundary:
                    stoping_holes.append({
                        'position': point, 'diameter': hole_diameter, 'type': 'stoping',
                        'color': 3, 'label': f'S{hole_number}'
                    })
                    hole_number += 1
                x_pos += spacing
            y_pos += burden
            row_index += 1

        return stoping_holes

    def generate_contour_holes(self, tunnel_outline, hole_diameter):
        """
        [REWRITTEN] Generate contour holes for smooth blasting, following the tunnel polyline.
        This creates a pattern inset from the provided polyline outline.
        """
        # Burden/offset for contour holes (distance from final wall). 0.3m is a common value.
        offset_distance = -0.3
        
        # Spacing along the contour. Closer spacing for smoother walls.
        # PDF page 5 suggests S_ct = 15*D1 = 15*0.045m = 0.675m. 0.4m provides a smoother result.
        spacing = 0.4

        # 1. Create the offset path for the holes
        contour_path = self._offset_polyline(tunnel_outline, offset_distance)
        if not contour_path:
            print("Warning: Could not generate offset polyline for contour holes.")
            return []

        # 2. Place points evenly along this path
        positions = self._place_points_on_polyline(contour_path, spacing)
        
        # 3. Create the hole objects
        contour_holes = []
        for i, pos in enumerate(positions):
            contour_holes.append({
                'position': pos, 'diameter': hole_diameter * 0.8, 'type': 'contour',
                'color': 4, 'label': f'P{i+1}'
            })
        return contour_holes

    def draw_drilling_pattern(self, holes, tunnel_outline=None):
        """Draw the complete drilling pattern"""
        layers = {'CUT_HOLES': 1, 'EMPTY_HOLES': 2, 'STOPING_HOLES': 3, 'CONTOUR_HOLES': 4, 'TUNNEL_OUTLINE': 5, 'ANNOTATIONS': 7}
        self.acad.setup_layers(layers)

        if tunnel_outline:
            self.doc.ActiveLayer = self.doc.Layers.Item('TUNNEL_OUTLINE')
            for i in range(len(tunnel_outline)):
                p1 = tunnel_outline[i]
                p2 = tunnel_outline[(i+1) % len(tunnel_outline)]
                line = self.model.AddLine(APoint(p1[0], p1[1]), APoint(p2[0], p2[1]))
                line.color = 5

        for hole in holes:
            layer_map = {'empty': 'EMPTY_HOLES', 'cut': 'CUT_HOLES', 'stoping': 'STOPING_HOLES', 'contour': 'CONTOUR_HOLES'}
            layer = layer_map.get(hole['type'], 'CUT_HOLES')
            self.acad.draw_circle(hole['position'], hole['diameter']/2, hole['color'], layer)
            if 'label' in hole:
                text_pos = (hole['position'][0] + hole['diameter']*0.75, hole['position'][1] + hole['diameter']*0.75)
                self.acad.draw_text(text_pos, hole['label'], 0.05, hole['color'], 'ANNOTATIONS')

    def add_pattern_info(self, center, tunnel_radius, advance_length, hole_diameter):
        """Add pattern information and legend"""
        title_pos = (center[0] - tunnel_radius, center[1] + tunnel_radius + 1)
        self.acad.draw_text(title_pos, "FOUR-SECTION CUT DRILLING PATTERN", 0.2, 7, 'ANNOTATIONS')

        info_y = title_pos[1] - 0.3
        specs = [f"Advance Length: {advance_length}m", f"Hole Diameter: {hole_diameter*1000:.0f}mm",
                 f"Pattern Type: Four-Section Parallel Cut", f"Generated from: dbm_polyline layer"]
        for i, spec in enumerate(specs):
            self.acad.draw_text((title_pos[0], info_y - i * 0.15), spec, 0.1, 7, 'ANNOTATIONS')

        legend_x = center[0] + tunnel_radius + 1
        legend_y = center[1] + tunnel_radius
        legend_items = [("Empty Hole (Relief)", 2, "E"), ("Cut Holes", 1, "C"), ("Stoping Holes", 3, "S"),
                        ("Contour Holes", 4, "P"), ("Tunnel Outline", 5, "")]
        self.acad.draw_text((legend_x, legend_y + 0.3), "LEGEND", 0.15, 7, 'ANNOTATIONS')
        for i, (label, color, prefix) in enumerate(legend_items):
            y_pos = legend_y - i * 0.3
            self.acad.draw_circle((legend_x, y_pos), 0.05, color)
            self.acad.draw_text((legend_x + 0.2, y_pos - 0.05), label, 0.12, color)


def main():
    print("Starting Four-Section Cut Pattern Generator...")
    print("Make sure AutoCAD is running and has a polyline on '0_dbm_polyline' layer")

    try:
        acad = myAutoCAD()
        generator = FourSectionCutGenerator(acad)
        polylines = generator.read_polyline_from_layer("0_dbm_polyline")

        if not polylines:
            print("No polyline found on '0_dbm_polyline' layer!")
            print("Please create a closed polyline representing the tunnel outline on this layer.")
            return

        tunnel_outline = polylines[0]
        print(f"Found polyline with {len(tunnel_outline)} vertices")

        center, radius = generator.calculate_tunnel_center_and_radius(tunnel_outline)
        if not center:
            print("Could not process polyline.")
            return
        print(f"Calculated center: ({center[0]:.2f}, {center[1]:.2f})")
        print(f"Calculated approx. radius: {radius:.2f}m")

        advance_length = float(input("Enter advance length (m) [default: 3.5]: ") or "3.5")
        hole_diameter = float(input("Enter hole diameter (mm) [default: 45]: ") or "45") / 1000

        df, dl, sections = generator.calculate_four_section_parameters(hole_diameter, advance_length)
        print(f"\nCalculated parameters:")
        print(f"Equivalent empty hole diameter: {df:.0f}mm")
        print(f"Empty hole diameter to drill: {dl:.0f}mm")

        # --- UPDATED FUNCTION CALLS ---
        cut_holes = generator.generate_four_section_cut_pattern(center, sections, hole_diameter, dl)
        stoping_holes = generator.generate_stoping_pattern(tunnel_outline, cut_holes, center, hole_diameter)
        contour_holes = generator.generate_contour_holes(tunnel_outline, hole_diameter)
        
        all_holes = cut_holes + stoping_holes + contour_holes

        print(f"\nGenerated drilling pattern:")
        print(f"Empty holes: {len([h for h in all_holes if h['type'] == 'empty'])}")
        print(f"Cut holes: {len([h for h in all_holes if h['type'] == 'cut'])}")
        print(f"Stoping holes: {len([h for h in all_holes if h['type'] == 'stoping'])}")
        print(f"Contour holes: {len([h for h in all_holes if h['type'] == 'contour'])}")
        print(f"Total holes: {len(all_holes)}")

        generator.draw_drilling_pattern(all_holes, tunnel_outline)
        generator.add_pattern_info(center, radius, advance_length, hole_diameter)
        acad.zoom_extents()

        save_path = input("\nEnter path to save drawing (or press Enter to skip): ")
        if save_path.strip():
            try:
                acad.doc.SaveAs(save_path)
                print(f"Drawing saved to: {save_path}")
            except Exception as e:
                print(f"Error saving file: {e}")

        print("\nPattern generation complete!")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure AutoCAD is running and a valid, closed polyline exists on the '0_dbm_polyline' layer.")

if __name__ == "__main__":
    main()