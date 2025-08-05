#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused


class FusedProfile_01x01(BaseFused):
    fusion_range = None
    number_of_fibers = 1

    def initialize_structure(self):
        self.add_center_fiber(fiber_radius=self.fiber_radius)

        self._clad_structure = self.fiber_list[0]
