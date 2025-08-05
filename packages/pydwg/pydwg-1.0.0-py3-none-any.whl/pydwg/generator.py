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

    # --- NEW AND ENHANCED HELPER METHODS ---

    def _calculate_polygon_area(self, vertices):
        """Calculates the signed area of a polygon.
        Positive for counter-clockwise, negative for clockwise."""
        area = 0.0
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            area += (p1[0] * p2[1]) - (p2[0] * p1[1])
        return area / 2.0

    def _tessellate_arc(self, arc_entity, num_segments=20):
        """Converts an AutoCAD Arc entity into a list of vertex points."""
        center = arc_entity.Center
        radius = arc_entity.Radius
        start_angle = arc_entity.StartAngle  # In radians
        end_angle = arc_entity.EndAngle    # In radians

        # AutoCAD arcs can have end_angle < start_angle
        if end_angle < start_angle:
            end_angle += 2 * math.pi

        points = []
        total_angle = end_angle - start_angle
        angle_step = total_angle / num_segments

        for i in range(num_segments + 1):
            angle = start_angle + i * angle_step
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        return points

    def _order_segments(self, segments, tolerance=1e-6):
        """
        [REWRITTEN] Orders a list of disconnected segments into a continuous path,
        handling arbitrary segment directions.
        """
        from collections import defaultdict

        if not segments:
            return []

        # Use an adjacency list (a dict of lists) to store all connections.
        # This correctly handles points connected to multiple segments.
        adjacency_list = defaultdict(list)
        for p1, p2 in segments:
            adjacency_list[p1].append(p2)
            adjacency_list[p2].append(p1)

        # Find a starting point. An endpoint (degree 1) is ideal for open polylines.
        # If the polyline is closed, all points have 2 connections.
        start_node = None
        for point, neighbors in adjacency_list.items():
            if len(neighbors) == 1:
                start_node = point
                break
        
        # If no endpoint is found, it's a closed loop (or multiple loops). Pick any point to start.
        if start_node is None:
            start_node = segments[0][0]

        # --- Traversal Logic ---
        ordered_vertices = []
        visited = set()
        to_visit = [start_node]

        while to_visit:
            current_node = to_visit.pop(0)
            if current_node in visited:
                continue

            visited.add(current_node)
            ordered_vertices.append(current_node)

            # Find unvisited neighbors and add them to the list to visit
            # This simple traversal works but doesn't preserve a single path order.
            # We need a smarter traversal that follows the path.

        # --- Smarter Path-Following Traversal ---
        ordered_vertices = [start_node]
        current_point = start_node
        
        # We need to traverse the entire path, which has a length equal to the number of unique vertices
        while len(ordered_vertices) < len(adjacency_list):
            neighbors = adjacency_list[current_point]
            found_next = False
            for next_point in neighbors:
                # Check if the neighbor is already in our ordered path.
                # We need to check the whole list, not just the last point, in case of tiny segments.
                is_visited = any(math.isclose(next_point[0], p[0], abs_tol=tolerance) and 
                                 math.isclose(next_point[1], p[1], abs_tol=tolerance) 
                                 for p in ordered_vertices)

                if not is_visited:
                    ordered_vertices.append(next_point)
                    current_point = next_point
                    found_next = True
                    break # Move to the next point in the path
            
            if not found_next:
                # This can happen if the path is not fully closed, and we've hit the other end.
                # Or if there's a branch. For now, we assume a single path.
                if len(ordered_vertices) == len(adjacency_list):
                    break # We have successfully visited all points of an open polyline
                else:
                    print(f"Warning: Path appears to be broken or has branches. Traversal stopped at {current_point}.")
                    break

        return ordered_vertices

    def read_tunnel_outline_from_layer(self, layer_name="0_dbm_polyline"):
        """
        [NEW] Reads Lines, Arcs, and Polylines from a layer to form a single,
        high-fidelity, counter-clockwise ordered tunnel outline.
        """
        segments = []
        try:
            for entity in self.model:
                if entity.Layer == layer_name:
                    if entity.ObjectName == 'AcDbLine':
                        p1 = (entity.StartPoint[0], entity.StartPoint[1])
                        p2 = (entity.EndPoint[0], entity.EndPoint[1])
                        segments.append((p1, p2))
                    elif entity.ObjectName == 'AcDbArc':
                        arc_points = self._tessellate_arc(entity)
                        for i in range(len(arc_points) - 1):
                            segments.append((arc_points[i], arc_points[i+1]))
                    elif entity.ObjectName == 'AcDbPolyline':
                        coords = entity.Coordinates
                        poly_points = [(coords[i], coords[i+1]) for i in range(0, len(coords), 2)]
                        for i in range(len(poly_points) - 1):
                            segments.append((poly_points[i], poly_points[i+1]))
                        # Add closing segment for closed polylines
                        if entity.Closed and len(poly_points) > 2:
                            segments.append((poly_points[-1], poly_points[0]))

            if not segments:
                return None

            # Order all collected segments into a single vertex list
            ordered_vertices = self._order_segments(segments)

            # Ensure the vertex order is counter-clockwise for predictable offsets
            area = self._calculate_polygon_area(ordered_vertices)
            if area < 0:  # If clockwise, reverse it
                ordered_vertices.reverse()

            return ordered_vertices
        except Exception as e:
            print(f"Error reading tunnel outline: {e}")
            return None

    def _line_intersection(self, p1, p2, p3, p4):
        """Calculates the intersection point of two lines defined by p1-p2 and p3-p4."""
        x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-9: return None
        t_num = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
        t = t_num / den
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

    def _offset_polyline(self, vertices, offset):
        """Creates a new polyline by offsetting the original one.
        Assumes a counter-clockwise polyline, so a negative offset moves inward."""
        offset_vertices = []
        num_verts = len(vertices)
        if num_verts < 2: return []
        
        closed_vertices = vertices + [vertices[0]]
        offset_lines = []

        for i in range(num_verts):
            p1, p2 = closed_vertices[i], closed_vertices[i+1]
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            length = math.sqrt(dx**2 + dy**2)
            if length == 0: continue
            nx, ny = -dy / length, dx / length
            op1 = (p1[0] + offset * nx, p1[1] + offset * ny)
            op2 = (p2[0] + offset * nx, p2[1] + offset * ny)
            offset_lines.append((op1, op2))

        if not offset_lines: return []

        for i in range(num_verts):
            line1 = offset_lines[i-1] 
            line2 = offset_lines[i]
            intersection = self._line_intersection(line1[0], line1[1], line2[0], line2[1])
            offset_vertices.append(intersection if intersection else line2[0])
        return offset_vertices

    def _place_points_on_polyline(self, vertices, spacing):
        """Places points along a closed polyline at a specified, even spacing."""
        if not vertices or spacing <= 0: return []
        points = []
        path = vertices + [vertices[0]]
        total_length = sum(math.dist(path[i], path[i+1]) for i in range(len(path) - 1))
        if total_length < spacing: return [vertices[0]] if vertices else []
        num_points = int(round(total_length / spacing))
        if num_points == 0: return [vertices[0]] if vertices else []
        actual_spacing = total_length / num_points
        dist_to_next_point, dist_along_path = 0, 0

        for i in range(len(path) - 1):
            p1, p2 = path[i], path[i+1]
            segment_length = math.dist(p1, p2)
            if segment_length < 1e-9: continue
            while dist_to_next_point <= dist_along_path + segment_length + 1e-9:
                ratio = (dist_to_next_point - dist_along_path) / segment_length
                new_x, new_y = p1[0] + ratio * (p2[0] - p1[0]), p1[1] + ratio * (p2[1] - p1[1])
                if len(points) < num_points: points.append((new_x, new_y))
                else: return points
                dist_to_next_point += actual_spacing
            dist_along_path += segment_length
        return points

    def _is_point_in_polygon(self, point, polygon):
        x, y = point; n = len(polygon); inside = False
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
                if p1y != p2y: xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= xinters: inside = not inside
            p1x, p1y = p2x, p2y
        return inside
        
    def _get_polyline_bounding_box(self, vertices):
        min_x = min(v[0] for v in vertices); max_x = max(v[0] for v in vertices)
        min_y = min(v[1] for v in vertices); max_y = max(v[1] for v in vertices)
        return min_x, min_y, max_x, max_y

    def calculate_tunnel_center_and_radius(self, vertices):
        """
        [REWRITTEN] Calculate a weighted centroid and average radius from polyline vertices.
        This method is crucial for irregular or arc-based shapes, as it prevents bias from
        high-density vertices created by tessellating arcs. The weight of each vertex is
        determined by the average length of its two connecting segments.
        """
        if not vertices or len(vertices) < 3:
            return None, None

        # --- Part 1: Calculate the Weighted Centroid ---
        weighted_sum_x = 0.0
        weighted_sum_y = 0.0
        total_weight = 0.0 # This will sum to the total perimeter of the polygon

        for i in range(len(vertices)):
            p_current = vertices[i]
            # Get previous and next vertices, handling loop-around for a closed polygon
            p_prev = vertices[i - 1] 
            p_next = vertices[(i + 1) % len(vertices)]

            # Calculate the length of the two segments connected to the current vertex
            len_prev = math.dist(p_prev, p_current)
            len_next = math.dist(p_current, p_next)

            # The weight for this vertex is the average length of its adjacent segments
            weight = (len_prev + len_next) / 2.0
            
            weighted_sum_x += p_current[0] * weight
            weighted_sum_y += p_current[1] * weight
            total_weight += weight
            
        if total_weight == 0:
            return None, None # Should not happen for a valid polygon

        cx = weighted_sum_x / total_weight
        cy = weighted_sum_y / total_weight
        center = (cx, cy)

        # --- Part 2: Calculate the Weighted Average Radius ---
        # Now that we have the true center, we calculate the weighted average distance
        # of each vertex to that center.
        weighted_sum_of_distances = 0.0
        
        for i in range(len(vertices)):
            p_current = vertices[i]
            p_prev = vertices[i - 1]
            p_next = vertices[(i + 1) % len(vertices)]
            
            # Recalculate the same weight as before
            weight = (math.dist(p_prev, p_current) + math.dist(p_current, p_next)) / 2.0
            
            # Get the distance from the current vertex to the calculated center
            distance_to_center = math.dist(p_current, center)

            weighted_sum_of_distances += distance_to_center * weight

        # The weighted average radius is the weighted sum of distances divided by the total weight
        radius = weighted_sum_of_distances / total_weight

        return center, radius

    # --- MAIN GENERATION LOGIC (largely unchanged, but now more reliable) ---
    
    def generate_four_section_cut_pattern(self, center, sections, hole_diameter, empty_hole_diameter):
        # This function remains the same as it's based on the calculated center.
        holes = [{'position': center, 'diameter': empty_hole_diameter, 'type': 'empty', 'section': 0, 'color': 2, 'label': 'E1'}]
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
        positions = []
        cx, cy = center
        base_angle = (section - 1) * math.pi / 4
        for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
            total_angle = base_angle + angle
            positions.append((cx + half_side * math.sqrt(2) * math.cos(total_angle), cy + half_side * math.sqrt(2) * math.sin(total_angle)))
        return positions

    def is_valid_position(self, pos, existing_holes, max_burden):
        return all(math.dist(pos, h['position']) >= max_burden * 0.8 for h in existing_holes)

    def generate_stoping_pattern(self, tunnel_outline_vertices, cut_holes, center, hole_diameter):
        """Generate stoping holes to fill the area between the cut and contour."""
        stoping_holes = []
        burden, spacing = 0.8, 1.1 * 0.8  # Based on PDF Table 22.3 principles (B, 1.1B)
        
        # Define boundaries. Outer boundary is INSIDE the contour holes' path.
        cut_extent = max(math.dist(center, h['position']) for h in cut_holes) if cut_holes else 0
        contour_burden = 0.3

        # *** FIX: Use a positive value for an inward offset ***
        # The offset is the contour burden plus half the stoping burden to ensure
        # stoping holes are well inside the contour line.
        stoping_area_offset = contour_burden + (burden / 2.0)
        
        outer_boundary = self._offset_polyline(tunnel_outline_vertices, stoping_area_offset)

        if not outer_boundary: return []
        
        min_x, min_y, max_x, max_y = self._get_polyline_bounding_box(outer_boundary)
        hole_number, row_index, y_pos = 1, 0, min_y
        while y_pos <= max_y:
            x_pos = min_x + (spacing / 2 if row_index % 2 == 1 else 0)
            while x_pos <= max_x:
                point = (x_pos, y_pos)
                if math.dist(center, point) > (cut_extent + burden/2) and self._is_point_in_polygon(point, outer_boundary):
                    stoping_holes.append({'position': point, 'diameter': hole_diameter, 'type': 'stoping', 'color': 3, 'label': f'S{hole_number}'})
                    hole_number += 1
                x_pos += spacing
            y_pos += burden
            row_index += 1
        return stoping_holes

    def generate_contour_holes(self, tunnel_outline_vertices, hole_diameter):
        """Generate contour holes by offsetting the high-fidelity tunnel outline."""
        # *** FIX: Use a positive value for the inward offset distance ***
        offset_distance = 0.3
        spacing = 0.4  # Spacing along path

        contour_path = self._offset_polyline(tunnel_outline_vertices, offset_distance)
        if not contour_path: return []
        
        positions = self._place_points_on_polyline(contour_path, spacing)
        return [{'position': pos, 'diameter': hole_diameter*0.8, 'type': 'contour', 'color': 4, 'label': f'P{i+1}'} for i, pos in enumerate(positions)]

    def draw_drilling_pattern(self, holes, tunnel_outline_vertices=None):
        layers = {'CUT_HOLES': 1, 'EMPTY_HOLES': 2, 'STOPING_HOLES': 3, 'CONTOUR_HOLES': 4, 'TUNNEL_OUTLINE': 5, 'ANNOTATIONS': 7}
        self.acad.setup_layers(layers)

        if tunnel_outline_vertices:
            # Draw the outline from the ordered vertices for consistency
            self.acad.doc.ActiveLayer = self.doc.Layers.Item('TUNNEL_OUTLINE')
            path = tunnel_outline_vertices + [tunnel_outline_vertices[0]]
            for i in range(len(path)-1):
                p1, p2 = path[i], path[i+1]
                self.model.AddLine(APoint(p1[0], p1[1]), APoint(p2[0], p2[1])).color = 5

        for hole in holes:
            layer_map = {'empty': 'EMPTY_HOLES', 'cut': 'CUT_HOLES', 'stoping': 'STOPING_HOLES', 'contour': 'CONTOUR_HOLES'}
            self.acad.draw_circle(hole['position'], hole['diameter']/2, hole['color'], layer_map.get(hole['type'], 'CUT_HOLES'))
            if 'label' in hole:
                text_pos = (hole['position'][0] + 0.07, hole['position'][1] + 0.07)
                self.acad.draw_text(text_pos, hole['label'], 0.05, hole['color'], 'ANNOTATIONS')

    def add_pattern_info(self, center, tunnel_radius, advance_length, hole_diameter):
        # This function remains the same.
        title_pos = (center[0] - tunnel_radius, center[1] + tunnel_radius + 1)
        self.acad.draw_text(title_pos, "FOUR-SECTION CUT DRILLING PATTERN", 0.2, 7, 'ANNOTATIONS')
        info_y = title_pos[1] - 0.3
        specs = [f"Advance Length: {advance_length}m", f"Hole Diameter: {hole_diameter*1000:.0f}mm", "Pattern Type: Four-Section Parallel Cut"]
        for i, spec in enumerate(specs): self.acad.draw_text((title_pos[0], info_y - i * 0.15), spec, 0.1, 7, 'ANNOTATIONS')
        legend_x, legend_y = center[0] + tunnel_radius + 1, center[1] + tunnel_radius
        legend_items = [("Empty Hole (Relief)", 2, "E"), ("Cut Holes", 1, "C"), ("Stoping Holes", 3, "S"), ("Contour Holes", 4, "P"), ("Tunnel Outline", 5, "")]
        self.acad.draw_text((legend_x, legend_y + 0.3), "LEGEND", 0.15, 7, 'ANNOTATIONS')
        for i, (label, color, prefix) in enumerate(legend_items):
            y_pos = legend_y - i * 0.3
            self.acad.draw_circle((legend_x, y_pos), 0.05, color)
            self.acad.draw_text((legend_x + 0.2, y_pos - 0.05), label, 0.12, color)

    # Calculate_four_section_parameters is unchanged.
    def calculate_four_section_parameters(self, hole_diameter, advance_length):
        df = ((3.2 * advance_length)**2)/1000; dl = df; v1 = 1.5 * df
        sections = [{'burden': v1, 'spacing': v1 * math.sqrt(2), 'stemming': v1, 'section': 1}]
        B1 = v1; B2 = B1 * math.sqrt(2)
        sections.append({'burden': B2, 'spacing': 1.5 * B2 * math.sqrt(2), 'stemming': B1 * math.sqrt(2) / 2, 'section': 2})
        B3 = 1.5 * B2 * math.sqrt(2)
        sections.append({'burden': B3, 'spacing': 1.5 * B3 * math.sqrt(2), 'stemming': math.sqrt(2)/2 * (B1*math.sqrt(2)/2 + B2), 'section': 3})
        B4 = 1.5 * B3 * math.sqrt(2)
        sections.append({'burden': B4, 'spacing': 1.5 * B4 * math.sqrt(2), 'stemming': math.sqrt(2)/2 * (math.sqrt(2)/2 * B1*math.sqrt(2)/2 + B2 + B3), 'section': 4})
        return df, dl, sections 