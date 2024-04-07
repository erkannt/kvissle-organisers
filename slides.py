# %%
from build123d import *
from ocp_vscode import *

reset_show()

depth = 245
width = 303
height = 40
magnet_diam = 6.1
magnet_depth = 6
magnet_hole_inset = 4.2
mouse_ear_diam = 5
mouse_ear_thickness = 0.4
mouse_ear_overlap = 1.5
wall = 4
outer_corner_fillet = 2
inner_corner_fillet = 10
top_edge_fillet = wall / 3

quarter_wall_loc = (0, width / 2 - (width - 2 * wall) / 4)

full_width = Rectangle(width=width, height=wall, align=Align.MIN)
full_depth = Rectangle(width=wall, height=depth, align=Align.MIN)

sketch = (
    full_width
    + Pos(0, depth - wall) * full_width
    + full_depth
    + Pos(width - wall, 0) * full_depth
)
slide_center = sketch.bounding_box().center()
slide_outer_corners = sketch.vertices().sort_by_distance(slide_center)[-4:]
sketch = fillet(
    slide_outer_corners,
    radius=outer_corner_fillet,
)
sketch = sketch + Pos(width / 2 - wall / 2, 0) * full_depth
sketch = sketch + Pos(width / 4 - wall / 2, 0) * full_depth
sketch = fillet(sketch.vertices(), radius=inner_corner_fillet)
sacrificial_helper_to_avoid_fillet_issue = extrude(sketch, amount=-top_edge_fillet)
slide = extrude(sketch, amount=height) + sacrificial_helper_to_avoid_fillet_issue
slide = (
    fillet(slide.edges(), radius=top_edge_fillet)
    - sacrificial_helper_to_avoid_fillet_issue
)

magnet_holes = [
    Plane.XY
    * Pos(
        pos.X + (magnet_hole_inset if pos.X < slide_center.X else -magnet_hole_inset),
        pos.Y + (magnet_hole_inset if pos.Y < slide_center.Y else -magnet_hole_inset),
        0,
    )
    * Cylinder(
        radius=magnet_diam / 2,
        height=magnet_depth * 2,
        align=[Align.CENTER, Align.CENTER, Align.MIN],
    )
    for pos in slide_outer_corners
]

slide = slide - magnet_holes

def corner_mouse_ears(shape):
    center = shape.bounding_box().center()
    outer_corners = Solid.from_bounding_box(shape.bounding_box()).faces().group_by(Axis.Z)[0].vertices()
    print(outer_corners)
    mouse_ear_shift = (mouse_ear_diam / 2 - mouse_ear_overlap) / 1.4
    mouse_ears = [
        Plane.XY
        * Pos(
            pos.X + (-mouse_ear_shift if pos.X < center.X else mouse_ear_shift),
            pos.Y + (-mouse_ear_shift if pos.Y < center.Y else mouse_ear_shift),
            0,
        )
        * Cylinder(
            radius=mouse_ear_diam / 2,
            height=mouse_ear_thickness,
            align=[Align.CENTER, Align.CENTER, Align.MIN],
        )
        for pos in outer_corners
    ]
    return mouse_ears

right = Pos(50,0,0) * split(slide, Plane.YZ.offset(width / 2), keep=Keep.TOP)
left = split(slide, Plane.YZ.offset(width / 2), keep=Keep.BOTTOM)
right = right + corner_mouse_ears(right)
left = left + corner_mouse_ears(left)
show_object(left)
show_object(right)
left.export_stl("slide-quarter-quarter-half--left.stl")
right.export_stl("slide-quarter-quarter-half--right.stl")

# %%
