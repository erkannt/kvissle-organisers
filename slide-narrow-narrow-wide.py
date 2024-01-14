# %%
from build123d import *
from ocp_vscode import *
from copy import copy

reset_show()

depth = 245
width = 303
height = 40
magnet_diam = 6.2
magnet_depth = 6
wall = 4
major_fillet = 10
minor_fillet = 1

quarter_wall_loc = (0, width / 2 - (width - 2 * wall) / 4)


with BuildPart(Plane.XY) as slide:
    with BuildSketch(Plane.XY) as base_shape:
        perimeter = Rectangle(depth, width)
        offset(perimeter, amount=-wall, kind=Kind.INTERSECTION, mode=Mode.SUBTRACT)
        Rectangle(depth, wall * 2)
        with Locations(quarter_wall_loc):
            Rectangle(depth, wall)
    extrude(amount=height)

    fillet(slide.edges().filter_by(Axis.Z).sort_by(Axis.X)[0:2], minor_fillet)
    fillet(slide.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:], minor_fillet)

    fillet(
        slide.edges()
        .filter_by(Axis.Z)
        .filter_by_position(Axis.X, minimum=-depth / 2 + 2, maximum=depth / 2 - 2),
        major_fillet,
    )

    fillet(
        slide.edges()
        .filter_by(Plane.XY)
        .filter_by_position(Axis.Z, minimum=height, maximum=height),
        minor_fillet,
    )

    magnet_edge_offset = (1.5 + magnet_diam / 2)
    with Locations(
        [
            (0, -magnet_edge_offset),
            (0, +magnet_edge_offset),
            quarter_wall_loc,
            (0, width / 2 - magnet_edge_offset),
            (0, -width / 2 + magnet_edge_offset),
        ]
    ):
        with Locations(((depth / 2 - wall), 0), (-(depth / 2 - wall), 0)):
            Hole(radius=magnet_diam / 2, depth=magnet_diam)

show_object(slide)
slide.part.export_stl("slide-narrow-narrow-wide.stl")
# %%
