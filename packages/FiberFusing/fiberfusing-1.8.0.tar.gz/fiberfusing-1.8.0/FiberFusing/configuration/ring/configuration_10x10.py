#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused


class FusedProfile_10x10(BaseFused):
    fusion_range = [0, 0.3]
    number_of_fibers = 10

    def initialize_structure(self):
        self.add_structure(
            structure_type='ring',
            number_of_fibers=7,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            scale_position=1.3,
            angle_shift=25,
            compute_fusing=False
        )

        self.add_structure(
            structure_type='ring',
            number_of_fibers=3,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            scale_position=1,
            compute_fusing=False
        )

        self.add_center_fiber(fiber_radius=self.fiber_radius)
