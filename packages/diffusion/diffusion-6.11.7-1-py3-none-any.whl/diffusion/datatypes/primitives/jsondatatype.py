#  Copyright (c) 2024 - 2025 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

from __future__ import annotations

import typing
from typing import Optional, Union

from .primitivedatatype import T, PrimitiveDataType

JsonTypes = Union[dict, list, str, int, float]


class JsonDataType(
    PrimitiveDataType[
        JsonTypes
    ],
    typing.Generic[T]
):
    """ JSON data type implementation. """

    type_code = 15
    type_name = "json"
    raw_types = JsonTypes.__args__  # type: ignore

    def __init__(self, value: Optional[JsonTypes]) -> None:
        super().__init__(value)
