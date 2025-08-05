# Copyright 2025 Jonas David Stephan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
SkeletonDataPointWithName.py

This module defines a class to represent a single data point in a 3D skeleton model
with an additional "name" attribute.

Author: Jonas David Stephan
Date: 2025-01-28
License: Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
"""

import json

from typing import Dict


class SkeletonDataPointWithName:
    """
        Represents a single data point in a 3D skeleton model with an additional "name" attribute.

        Attributes:
            data (dict): A dictionary containing the point's ID, name, and 3D coordinates (x, y, z).
        """

    def __init__(self, idx: int, name: str, x: float, y: float, z: float):
        """
            Initialize a new SkeletonDataPointWithName instance.

            Args:
                idx (int): The ID of the data point.
                name (str): The name associated with the data point.
                x (float): The x-coordinate of the data point.
                y (float): The y-coordinate of the data point.
                z (float): The z-coordinate of the data point.

            Raises:
                ValueError: If any of the coordinates are invalid (e.g., None or not numeric).
            """
        if not all(isinstance(coord, (int, float)) for coord in [x, y, z]):
            raise ValueError("Coordinates x, y, and z must be numeric.")
        if not isinstance(name, str):
            raise ValueError("The name must be a string.")
        self.data: Dict[str, object]={"id": idx, "name": name, "x": x, "y": y, "z": z}

    def get_data(self) -> Dict[str, object]:
        """
            Retrieve the data point as a dictionary.

            Returns:
                dict: The dictionary representation of the data point.
            """
        return self.data

    def to_json(self) -> str:
        """
            Convert the data point to a JSON string.

            Returns:
                str: The JSON-formatted string representation of the data point.
            """
        return json.dumps(self.data, indent=4)
