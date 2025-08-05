#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused


class FusedProfile_03x03(BaseFused):
    fusion_range = [0.1, .35]
    number_of_fibers = 3

    def initialize_structure(self):
        self.add_structure(
            structure_type='line',
            number_of_fibers=3,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            compute_fusing=True
        )
