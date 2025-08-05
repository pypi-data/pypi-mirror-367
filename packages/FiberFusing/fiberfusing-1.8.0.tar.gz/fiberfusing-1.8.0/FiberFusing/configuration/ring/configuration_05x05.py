#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused


class FusedProfile_05x05(BaseFused):
    fusion_range = [0, .45]
    number_of_fibers = 5

    def initialize_structure(self):
        self.add_structure(
            structure_type='ring',
            number_of_fibers=5,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            compute_fusing=True
        )
