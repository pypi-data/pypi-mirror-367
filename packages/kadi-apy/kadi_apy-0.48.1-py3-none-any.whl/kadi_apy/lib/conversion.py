# Copyright 2024 Karlsruhe Institute of Technology
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
from dateutil import parser

from kadi_apy.globals import EXTRAS_MAX_INTEGER
from kadi_apy.globals import EXTRAS_MIN_INTEGER


def json_to_kadi(data, convert_invalid_ints=False, fallback_value=None):
    """Convert plain JSON to a Kadi4Mat-compatible extra metadata structure.

    :param data: The JSON data to convert as dictionary, list or singular, primitive
        value.
    :param convert_invalid_ints: (optional) Flag indicating whether to automatically
        convert integer values which are not in the value range supported by Kadi to
        strings instead.
    :param fallback_value: (optional) A fallback value to use for all ``null`` values
        instead of ignoring them.
    :return: The converted data as a list of extra metadata.
    """
    return _json_to_kadi(data, convert_invalid_ints, fallback_value)


def _json_to_kadi(data, convert_invalid_ints, fallback_value, nested_type=None):
    extras = []

    if isinstance(data, dict):
        data = data.items()
    elif isinstance(data, (list, tuple)):
        data = enumerate(data, start=1)
    else:
        data = enumerate([data], start=1)

    for key, value in data:
        if value is None:
            if fallback_value is None:
                continue

            value = fallback_value

        extra = {}

        if nested_type != "list":
            extra["key"] = str(key)

        if isinstance(value, (dict, list, tuple)):
            extra["type"] = "dict" if isinstance(value, dict) else "list"
            extra["value"] = _json_to_kadi(
                value, convert_invalid_ints, fallback_value, nested_type=extra["type"]
            )
        else:
            extra["type"] = type(value).__name__
            extra["value"] = value

            if extra["type"] == "str" and "_" not in value:
                try:
                    value = parser.isoparse(value).isoformat()
                    extra["type"] = "date"
                except:
                    pass

            if (
                extra["type"] == "int"
                and convert_invalid_ints
                and (value < EXTRAS_MIN_INTEGER or value > EXTRAS_MAX_INTEGER)
            ):
                extra["type"] = "str"
                extra["value"] = str(value)

        extras.append(extra)

    return extras


def kadi_to_json(extras):
    """Convert Kadi4Mat-compatible extra metadata to a plain JSON structure.

    :param extras: A list of extra metadata to convert.
    :return: The converted metadata as dictionary.
    """
    return _kadi_to_json(extras)


def _kadi_to_json(extras, nested_type=None):
    if nested_type == "list":
        converted_extras = []
    else:
        converted_extras = {}

    for extra in extras:
        if extra["type"] in {"dict", "list"}:
            value = _kadi_to_json(extra["value"], nested_type=extra["type"])
        else:
            value = extra["value"]

        if nested_type == "list":
            converted_extras.append(value)
        else:
            converted_extras[extra["key"]] = value

    return converted_extras
