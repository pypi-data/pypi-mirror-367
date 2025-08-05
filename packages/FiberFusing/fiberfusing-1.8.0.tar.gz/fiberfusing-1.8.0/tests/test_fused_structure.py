#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
import pytest
from FiberFusing import configuration
import matplotlib.pyplot as plt


fused_structures = [
    configuration.line.FusedProfile_02x02,
    configuration.line.FusedProfile_03x03,
    configuration.line.FusedProfile_04x04,
    configuration.line.FusedProfile_05x05,
    configuration.ring.FusedProfile_02x02,
    configuration.ring.FusedProfile_03x03,
    configuration.ring.FusedProfile_04x04,
    configuration.ring.FusedProfile_05x05,
    configuration.ring.FusedProfile_06x06,
    configuration.ring.FusedProfile_07x07,
    configuration.ring.FusedProfile_10x10,
    configuration.ring.FusedProfile_12x12,
    configuration.ring.FusedProfile_19x19,
]


@pytest.mark.parametrize('fused_structure', fused_structures, ids=lambda x: x.__name__)
@patch("matplotlib.pyplot.show")
def test_building_clad_structure(mock_show, fused_structure):
    clad = fused_structure(
        fusion_degree='auto',
        fiber_radius=62.5e-6,
        index=1.4444
    )

    clad.plot()
    mock_show.assert_called_once()  # Verify that show was called exactly once
    plt.close()


def test_configuration_api():
    structure = configuration.line.FusedProfile_02x02(fusion_degree='auto', fiber_radius=100e-6, index=1)

    structure.fusion_degree = 0.3

    structure.randomize_core_position(random_factor=4e-6)

    structure.translate(shift=(-5e6, +20e-6))


def test_fail_configuration_initialization():
    with pytest.raises(AssertionError):
        configuration.ring.FusedProfile_02x02(fusion_degree=1.2, fiber_radius=1, index=1)


if __name__ == "__main__":
    pytest.main(["-W error", __file__])
