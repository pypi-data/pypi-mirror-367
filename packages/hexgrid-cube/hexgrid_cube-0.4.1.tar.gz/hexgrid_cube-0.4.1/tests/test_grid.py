import pytest
from hexgrid_cube.hex import Hex
from hexgrid_cube.grid import FoVGrid


@pytest.fixture
def g():
    return FoVGrid((2, 2), blocking=[])


class TestHexGrid:
    def test_grid(self, g):
        actual = g
        assert actual.grid == {(0, 0): Hex(0, 0), (1, 0): Hex(1, 0),
                               (0, 1): Hex(0, 1), (1, 1): Hex(1, 1)}

    def test_flat_grid(self, g):
        actual = g
        assert actual.flat_grid == [Hex(0, 0), Hex(0, 1), Hex(1, 0), Hex(1, 1)]

    def test_graph(self, g):
        assert g.graph == {Hex(0, 0): [Hex(1, 0), Hex(0, 1)],
                           Hex(1, 0): [Hex(1, 1), Hex(0, 1), Hex(0, 0)],
                           Hex(0, 1): [Hex(1, 1), Hex(0, 0), Hex(1, 0)],
                           Hex(1, 1): [Hex(0, 1), Hex(1, 0)]}


class TestFoVGrid:
    def test_init_blocking(self, g):
        assert g.blocking_hexes == []
        assert FoVGrid((2, 2), blocking=[Hex(1, 1)]).blocking_hexes == [Hex(1, 1)]

    def test_init_visible(self, g):
        assert all(not v for v in g.visible_grid.values())

    def test_fov_surrounded_by_walls(self):
        grid = FoVGrid((2, 2), blocking=[Hex(1, 0), Hex(0, 1), Hex(1, 1)])
        grid.compute_visible_grid(Hex(0, 0), 1)
        assert grid.visible_grid[Hex(0, 0)] # origin is visible
        assert grid.visible_grid[Hex(1, 0)] and grid.visible_grid[Hex(0, 1)]    # walls are visible
        assert not grid.visible_grid[Hex(1, 1)] # obstructed hex is not visible

    def test_fov_no_walls(self):
        grid = FoVGrid((2, 2), blocking=[])
        grid.compute_visible_grid(Hex(0, 0), 2)
        assert all(grid.visible_grid.values())
