#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused


class FusedProfile_04x04(BaseFused):
    fusion_range = [0, 0.4]
    number_of_fibers = 4

    def initialize_structure(self):
        self.add_structure(
            structure_type='ring',
            number_of_fibers=4,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            compute_fusing=True
        )
