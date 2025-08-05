import math
from myAutoCAD import myAutoCAD

class DBM:
    def __init__(self, acad: myAutoCAD):
        self.acad = acad
        self.model = acad.model
        self.doc = acad.doc

    def draw_drilling_pattern(self, center, reamer_diam, blasthole_diam, ring_radii, holes_per_ring, reamer_layer="REAMER_HOLE", blasthole_layer="BLASTHOLES"):
        if len(ring_radii) != len(holes_per_ring):
            print("Error: RING_RADII and HOLES_PER_RING must match in length.")
            return
        # Central reamer hole
        self.acad.draw_circle(center, reamer_diam / 2, color=2, layer=reamer_layer)
        # Rings of blast holes
        for i, radius in enumerate(ring_radii):
            num_holes = holes_per_ring[i]
            positions = self.acad.calculate_points_on_circle(center, radius, num_holes)
            for pos in positions:
                self.acad.draw_circle(pos, blasthole_diam / 2, color=3, layer=blasthole_layer)

    def draw_parallel_cut_cylindrical_pattern(self, params):
        tunnel_radius = params.get("tunnel_radius", 2.5)
        center = params.get("center", (0, 0))
        hole_diameter = params.get("hole_diameter", 0.045)
        cut_holes_radius = params.get("cut_holes_radius", 0.6)
        cut_hole_count = params.get("cut_hole_count", 6)
        empty_holes_count = params.get("empty_holes_count", 2)
        ring_count = params.get("ring_count", 3)
        holes_per_ring = params.get("holes_per_ring", [8, 12, 16])
        ring_radii = params.get("ring_radii", [1.2, 1.8, 2.3])
        contour_holes = params.get("contour_holes", 20)
        colors = params.get("colors", {
            'cut': 1, 'empty': 2, 'production': 3, 'contour': 4, 'perimeter': 5
        })

        # Draw tunnel outline
        self.acad.draw_circle(center, tunnel_radius, color=colors['perimeter'])

        # Draw cut holes (central)
        cut_positions = self.acad.calculate_points_on_circle(center, cut_holes_radius, cut_hole_count)
        cut_positions.insert(0, center)
        for i, pos in enumerate(cut_positions):
            if i < empty_holes_count:
                self.acad.draw_circle(pos, hole_diameter * 2, color=colors['empty'])
                self.acad.draw_text((pos[0] + 0.1, pos[1] + 0.1), f"E{i+1}", 0.08, colors['empty'])
            else:
                self.acad.draw_circle(pos, hole_diameter, color=colors['cut'])
                self.acad.draw_text((pos[0] + 0.1, pos[1] + 0.1), f"C{i-empty_holes_count+1}", 0.08, colors['cut'])

        # Draw production holes in rings
        hole_number = 1
        for ring_idx in range(ring_count):
            radius = ring_radii[ring_idx]
            hole_count = holes_per_ring[ring_idx]
            start_angle = (math.pi / hole_count) if ring_idx % 2 == 1 else 0
            ring_positions = self.acad.calculate_points_on_circle(center, radius, hole_count, start_angle)
            for pos in ring_positions:
                if math.sqrt((pos[0] - center[0])**2 + (pos[1] - center[1])**2) < tunnel_radius - 0.2:
                    self.acad.draw_circle(pos, hole_diameter, color=colors['production'])
                    self.acad.draw_text((pos[0] + 0.1, pos[1] + 0.1), f"P{hole_number}", 0.08, colors['production'])
                    hole_number += 1

        # Draw contour holes
        contour_radius = tunnel_radius - 0.3
        contour_positions = self.acad.calculate_points_on_circle(center, contour_radius, contour_holes)
        for i, pos in enumerate(contour_positions):
            self.acad.draw_circle(pos, hole_diameter * 0.8, color=colors['contour'])
            self.acad.draw_text((pos[0] + 0.1, pos[1] + 0.1), f"S{i+1}", 0.06, colors['contour'])

        # Add legend and annotations
        self.add_legend_and_annotations(center, tunnel_radius, hole_diameter, cut_positions, holes_per_ring, contour_holes, colors, params)

    def add_legend_and_annotations(self, center, tunnel_radius, hole_diameter, cut_positions, holes_per_ring, contour_holes, colors, params):
        # Legend
        legend_x, legend_y = tunnel_radius + 1, tunnel_radius
        legend_items = [
            ("Cut Holes", colors['cut'], "C"),
            ("Empty Holes", colors['empty'], "E"),
            ("Production Holes", colors['production'], "P"),
            ("Contour Holes", colors['contour'], "S"),
            ("Tunnel Outline", colors['perimeter'], "")
        ]
        for i, (label, color, prefix) in enumerate(legend_items):
            y_pos = legend_y - i * 0.3
            self.acad.draw_circle((legend_x, y_pos), 0.05, color)
            self.acad.draw_text((legend_x + 0.2, y_pos - 0.05), label, 0.12, color)

        # Title and specifications
        title_y = tunnel_radius + 0.5
        self.acad.draw_text((-tunnel_radius, title_y), "PARALLEL CUT CYLINDRICAL DRILLING PATTERN", 0.2, 7)
        burden = params.get("burden", 0.8)
        spacing = params.get("spacing", 0.9)
        specs = [
            f"Tunnel Radius: {tunnel_radius}m",
            f"Hole Diameter: {hole_diameter*1000:.0f}mm",
            f"Burden: {burden}m",
            f"Spacing: {spacing}m",
            f"Cut Holes: {len(cut_positions)}",
            f"Production Holes: {sum(holes_per_ring)}",
            f"Contour Holes: {contour_holes}"
        ]
        for i, spec in enumerate(specs):
            self.acad.draw_text((-tunnel_radius, title_y - 0.3 - i * 0.15), spec, 0.1, 7)