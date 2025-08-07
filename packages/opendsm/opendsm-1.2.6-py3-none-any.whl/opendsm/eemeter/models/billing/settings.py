#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

   Copyright 2014-2025 OpenDSM contributors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""
from __future__ import annotations

from opendsm.common.base_settings import CustomField

from opendsm.eemeter.models.daily.utilities.settings import DailyLegacySettings



class BillingSettings(DailyLegacySettings):
    segment_minimum_count: int = CustomField(
        default=3,
        ge=3,
        developer=True,
        description="Minimum number of data points for HDD/CDD",
    )