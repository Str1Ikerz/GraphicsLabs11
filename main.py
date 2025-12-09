import tkinter as tk
import math


class PolyhedronViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Проективные преобразования — гексаэдр и додекаэдр")
        self.root.geometry("900x700")

        self.vertices = []
        self.edges = []

        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0

        self.center_x = 450
        self.center_y = 350
        self.scale = 130

        self.orthographic = True
        self.figure_type = "Гексаэдр"

        self.create_widgets()
        self.create_figure()
        self.draw()

        self.canvas.bind("<Button-1>", self.on_mouse_click)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)

    def create_figure(self):
        if self.figure_type == "Гексаэдр":
            self.create_hexahedron()
        elif self.figure_type == "Додекаэдр":
            self.create_dodecahedron()

    def create_hexahedron(self):
        """Гексаэдр = куб: 8 вершин, 12 рёбер"""
        self.vertices = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
        ]
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

    def create_dodecahedron(self):
        """Додекаэдр: 20 вершин, 30 рёбер (на основе золотого сечения)"""
        phi = (1 + math.sqrt(5)) / 2
        inv_phi = 1 / phi

        cube_vertices = [
            (x, y, z)
            for x in (-1, 1)
            for y in (-1, 1)
            for z in (-1, 1)
        ]

        extra_vertices = [
            (0,  inv_phi,  phi), (0,  inv_phi, -phi), (0, -inv_phi,  phi), (0, -inv_phi, -phi),
            ( inv_phi,  phi, 0), ( inv_phi, -phi, 0), (-inv_phi,  phi, 0), (-inv_phi, -phi, 0),
            ( phi, 0,  inv_phi), ( phi, 0, -inv_phi), (-phi, 0,  inv_phi), (-phi, 0, -inv_phi)
        ]

        self.vertices = cube_vertices + extra_vertices  # 8 + 12 = 20
        self.vertices = [self.normalize(v) for v in self.vertices]

        self.edges = [
            (0, 1), (0, 2), (0, 4),
            (1, 3), (1, 9),
            (2, 3), (2, 6),
            (3, 11),
            (4, 5), (4, 6),
            (5, 7), (5, 10),
            (6, 14),
            (7, 12), (7, 15),
            (8, 9), (8, 10), (8, 12),
            (9, 13),
            (10, 18),
            (11, 16), (11, 19),
            (12, 13),
            (13, 15),
            (14, 16), (14, 18),
            (15, 17),
            (16, 17),
            (17, 19),
            (18, 19)
        ]

    def normalize(self, v):
        x, y, z = v
        length = math.sqrt(x*x + y*y + z*z)
        if length == 0:
            return (0, 0, 0)
        return (x/length, y/length, z/length)

    def rotate(self, v):
        x, y, z = v

        y, z = (
            y * math.cos(self.rotation_x) - z * math.sin(self.rotation_x),
            y * math.sin(self.rotation_x) + z * math.cos(self.rotation_x)
        )

        x, z = (
            x * math.cos(self.rotation_y) + z * math.sin(self.rotation_y),
            -x * math.sin(self.rotation_y) + z * math.cos(self.rotation_y)
        )

        x, y = (
            x * math.cos(self.rotation_z) - y * math.sin(self.rotation_z),
            x * math.sin(self.rotation_z) + y * math.cos(self.rotation_z)
        )

        return (x, y, z)

    def project(self, v):
        x, y, z = v

        if self.orthographic:
            xp, yp = x, y
        else:
            d = 3.0
            if abs(d - z) < 1e-6:
                f = 1.0
            else:
                f = d / (d - z)
            xp, yp = x * f, y * f

        return (
            self.center_x + xp * self.scale,
            self.center_y - yp * self.scale
        )

    def create_widgets(self):
        top = tk.Frame(self.root)
        top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.proj_var = tk.BooleanVar(value=True)
        tk.Radiobutton(top, text="Ортогональная", variable=self.proj_var, value=True,
                       command=self.update_projection).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(top, text="Центральная", variable=self.proj_var, value=False,
                       command=self.update_projection).pack(side=tk.LEFT, padx=5)

        self.fig_var = tk.StringVar(value="Гексаэдр")
        tk.OptionMenu(top, self.fig_var, "Гексаэдр", "Додекаэдр",
                      command=self.change_figure).pack(side=tk.LEFT, padx=20)

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def update_projection(self):
        self.orthographic = self.proj_var.get()
        self.draw()

    def change_figure(self, value):
        self.figure_type = value
        self.create_figure()
        self.draw()

    def on_mouse_click(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def on_mouse_drag(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y

        self.rotation_y += dx * 0.01
        self.rotation_x += dy * 0.01

        self.last_x = event.x
        self.last_y = event.y

        self.draw()

    def draw(self):
        self.canvas.delete("all")

        projected = []
        for v in self.vertices:
            rv = self.rotate(v)
            pv = self.project(rv)
            projected.append(pv)

        for i, j in self.edges:
            self.canvas.create_line(
                projected[i][0], projected[i][1],
                projected[j][0], projected[j][1],
                width=2, fill="blue"
            )

        for x, y in projected:
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="red", outline="darkred")

        proj_name = "Ортогональная" if self.orthographic else "Центральная"
        txt = f"Фигура: {self.figure_type} | Проекция: {proj_name}"
        self.canvas.create_text(10, 10, anchor=tk.NW, text=txt, font=("Arial", 10))


def main():
    root = tk.Tk()
    PolyhedronViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()