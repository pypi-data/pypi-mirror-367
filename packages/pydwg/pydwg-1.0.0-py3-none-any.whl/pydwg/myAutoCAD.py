import math
from pyautocad import Autocad, APoint

class myAutoCAD:
    def __init__(self, create_if_not_exists=True):
        print("Connecting to AutoCAD...")
        self.acad = Autocad(create_if_not_exists=create_if_not_exists)
        self.model = self.acad.model
        self.doc = self.acad.doc
        print(f"Connected to: {self.doc.Name}")

    def setup_layers(self, layers):
        for name, color in layers.items():
            try:
                self.doc.Layers.Item(name)
            except Exception:
                layer = self.doc.Layers.Add(name)
                layer.color = color

    @staticmethod
    def calculate_points_on_circle(center, radius, count, start_angle=0):
        points = []
        angle_step = 2 * math.pi / count
        for i in range(count):
            angle = start_angle + i * angle_step
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        return points

    def draw_circle(self, center, radius, color=7, layer=None):
        if layer:
            self.doc.ActiveLayer = self.doc.Layers.Item(layer)
        circle = self.model.AddCircle(APoint(center[0], center[1]), radius)
        circle.color = color
        return circle

    def draw_text(self, position, text, height=0.1, color=7, layer=None):
        if layer:
            self.doc.ActiveLayer = self.doc.Layers.Item(layer)
        text_obj = self.model.AddText(text, APoint(position[0], position[1]), height)
        text_obj.color = color
        return text_obj

    def draw_arched_tunnel(self, center, width, height, layer="TUNNEL_PROFILE"):
        self.doc.ActiveLayer = self.doc.Layers.Item(layer)
        half_w = width / 2
        springline_height = height - half_w
        if springline_height < 0:
            springline_height = 0
        p1 = APoint(center[0] - half_w, center[1] - (height - springline_height) / 2)
        p2 = APoint(center[0] - half_w, p1.y + springline_height)
        p3 = APoint(center[0] + half_w, p1.y + springline_height)
        p4 = APoint(center[0] + half_w, p1.y)
        self.model.AddLine(p1, p4)
        self.model.AddLine(p1, p2)
        self.model.AddLine(p4, p3)
        arc_center = APoint(center[0], p2.y)
        self.model.AddArc(arc_center, half_w, math.radians(0), math.radians(180))

    def zoom_extents(self):
        self.acad.app.ZoomExtents()