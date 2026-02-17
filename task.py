import matplotlib.pyplot as plt

def polygon_area_and_centroid(vertices):
    n = len(vertices)
    area = 0
    cx = 0
    cy = 0

    for i in range(n):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        area += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross

    area *= 0.5
    if area == 0:
        return 0, 0, 0

    cx /= (6 * area)
    cy /= (6 * area)

    return abs(area), cx, cy


def plot_shape_with_centroid(shape):
    fig, ax = plt.subplots()

    vertices = shape["vertices"]
    xs = [v[0] for v in vertices] + [vertices[0][0]]
    ys = [v[1] for v in vertices] + [vertices[0][1]]

    ax.plot(xs, ys)
    area, cx, cy = polygon_area_and_centroid(vertices)

    ax.scatter(cx, cy)
    ax.set_title(shape["type"])
    ax.set_aspect('equal', 'box')
    plt.show()


if __name__ == "__main__":
    shapes = [
        {
            "type": "Rectangle",
            "vertices": [(0, 0), (4, 0), (4, 2), (0, 2)]
        },
        {
            "type": "Triangle",
            "vertices": [(0, 0), (4, 0), (2, 3)]
        },
        {
            "type": "Trapezoid",
            "vertices": [(0, 0), (6, 0), (4, 3), (2, 3)]
        }
    ]

    for shape in shapes:
        plot_shape_with_centroid(shape)
