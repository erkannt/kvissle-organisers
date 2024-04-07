# %%
from build123d import *
from ocp_vscode import *

reset_show()

DEPTH = 245
WIDTH = 303
HEIGHT = 40
MAGNET_DIAM = 6.1
MAGNET_DEPTH = 6
MAGNET_HOLE_INSET = 4.2
MOUSE_EAR_DIAM = 5
MOUSE_EAR_THICKNESS = 0.4
MOUSE_EAR_OVERLAP = 1.5
WALL = 4
OUTER_CORNER_FILLET = 2
INNER_CORNER_FILLET = 10


def corner_mouse_ears(shape):
    center = shape.bounding_box().center()
    outer_corners = (
        Solid.from_bounding_box(shape.bounding_box())
        .faces()
        .group_by(Axis.Z)[0]
        .vertices()
    )
    mouse_ear_shift = (MOUSE_EAR_DIAM / 2 - MOUSE_EAR_OVERLAP) / 1.4
    mouse_ears = [
        Plane.XY
        * Pos(
            pos.X + (-mouse_ear_shift if pos.X < center.X else mouse_ear_shift),
            pos.Y + (-mouse_ear_shift if pos.Y < center.Y else mouse_ear_shift),
            0,
        )
        * Cylinder(
            radius=MOUSE_EAR_DIAM / 2,
            height=MOUSE_EAR_THICKNESS,
            align=[Align.CENTER, Align.CENTER, Align.MIN],
        )
        for pos in outer_corners
    ]
    return mouse_ears


def extrude_and_fillet(sk):
    top_edge_fillet = WALL / 3
    sacrificial_helper_to_avoid_fillet_issue = extrude(sk, amount=-top_edge_fillet)
    body = extrude(sk, amount=HEIGHT) + sacrificial_helper_to_avoid_fillet_issue
    body = (
        fillet(body.edges(), radius=top_edge_fillet)
        - sacrificial_helper_to_avoid_fillet_issue
    )
    return body


full_width = Rectangle(width=WIDTH, height=WALL, align=Align.MIN)
full_depth = Rectangle(width=WALL, height=DEPTH, align=Align.MIN)

base_sketch = (
    full_width
    + Pos(0, DEPTH - WALL) * full_width
    + full_depth
    + Pos(WIDTH - WALL, 0) * full_depth
)
slide_center = base_sketch.bounding_box().center()
slide_outer_corners = base_sketch.vertices().sort_by_distance(slide_center)[-4:]
base_sketch = fillet(
    slide_outer_corners,
    radius=OUTER_CORNER_FILLET,
)

magnet_holes = [
    Plane.XY
    * Pos(
        pos.X + (MAGNET_HOLE_INSET if pos.X < slide_center.X else -MAGNET_HOLE_INSET),
        pos.Y + (MAGNET_HOLE_INSET if pos.Y < slide_center.Y else -MAGNET_HOLE_INSET),
        0,
    )
    * Cylinder(
        radius=MAGNET_DIAM / 2,
        height=MAGNET_DEPTH * 2,
        align=[Align.CENTER, Align.CENTER, Align.MIN],
    )
    for pos in slide_outer_corners
]

sketch1 = base_sketch
sketch1 = sketch1 + Pos(WIDTH / 2 - WALL / 2, 0) * full_depth
sketch1 = sketch1 + Pos(WIDTH / 4 - WALL / 2, 0) * full_depth
sketch1 = fillet(sketch1.vertices(), radius=INNER_CORNER_FILLET)

slide1 = extrude_and_fillet(sketch1) - magnet_holes
right = Pos(50, 0, 0) * split(slide1, Plane.YZ.offset(WIDTH / 2), keep=Keep.TOP)
left = split(slide1, Plane.YZ.offset(WIDTH / 2), keep=Keep.BOTTOM)
right = right + corner_mouse_ears(right)
left = left + corner_mouse_ears(left)
show_object(left)
show_object(right)
left.export_stl("slide-quarter-quarter-half--left.stl")
right.export_stl("slide-quarter-quarter-half--right.stl")

# %%
