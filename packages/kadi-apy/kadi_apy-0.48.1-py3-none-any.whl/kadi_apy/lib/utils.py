# Copyright 2025 Karlsruhe Institute of Technology
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
import re
import sys
from datetime import datetime
from datetime import timezone

import click

from kadi_apy.lib.exceptions import KadiAPYInputError


def chunked_response(path, response):
    """Stream the data of a given response to a file.

    :param path: The file path to store the data in.
    :param response: The response object, which needs to support streaming.
    """
    with open(path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1_000_000):
            f.write(chunk)


def generate_identifier(value):
    """Generate a valid resource identifier from a given string.

    :param value: The string to create the identifier from.
    :return: The generated identifier.
    """
    value = re.sub("[^a-z0-9-_ ]+", "", value.lower())
    value = re.sub("[ ]+", "-", value)

    return value[:50]


def append_identifier_suffix(identifier, suffix):
    """Append a suffix to an existing identifier.

    :param identifier: The identifier to append the suffix to. If the combined
        identifier is longer than the maximum identifier length, the original identifier
        will be truncated accordingly.
    :param suffix: The suffix to append to the identifier, which will be formatted
        according to the usual identifier rules. If the suffix is longer than the
        maximum identifier length, it will be truncated accordingly.
    :return: The combined identifier.
    """
    suffix = generate_identifier(suffix.strip())
    # Remove leading and trailing dashes or underscores.
    suffix = re.sub(r"^[-_]+|[-_]+$", "", suffix)[:49]

    return f"{identifier[:49 - len(suffix)]}_{suffix}"


def get_resource_type(resource_type):
    """Get a resource class from a corresponding string.

    :param resource_type: The resource type as a string.
    :return: The resource class.
    :raises KadiAPYInputError: If the given resource type does not exist.
    """
    from kadi_apy.lib.resources.collections import Collection
    from kadi_apy.lib.resources.groups import Group
    from kadi_apy.lib.resources.records import Record
    from kadi_apy.lib.resources.templates import Template

    resource_types = {
        "record": Record,
        "collection": Collection,
        "group": Group,
        "template": Template,
    }

    if resource_type not in resource_types:
        raise KadiAPYInputError(f"Resource type '{resource_type}' does not exist.")

    return resource_types[resource_type]


def paginate(callback):
    """Helper to handle paginated requests.

    :param callback: A callback function that takes a single argument, which is the
        current result page, starting at ``1``. The callback function has to perform the
        actual request using the given page and has to return the parsed response data
        (containing the pagination data) after processing it.
    """
    has_next = True
    page = 1

    while has_next:
        response = callback(page)
        has_next = response["_pagination"]["total_pages"] > page
        page += 1


def _utcnow():
    """Create a timezone aware datetime object of the current time in UTC."""
    return datetime.now(timezone.utc)


def _get_record_identifiers(collection):
    """Get a dictionary mapping record IDs to their corresponding identifiers.

    :param collection: The collection to get the record identifiers from.
    :return: A dictionary mapping record IDs to their corresponding identifiers.
    """
    id_to_identifier = {}

    def _collect_record_identifiers(page):
        response = collection.get_records(page=page, per_page=100).json()
        for record in response["items"]:
            id_to_identifier[record["id"]] = record["identifier"]
        return response

    paginate(_collect_record_identifiers)

    return id_to_identifier


def error(message):
    """Display an error message in red and terminate the program.

    :parm message: The error message to display.
    """
    click.secho(message, fg="red", bold=True)
    sys.exit(1)
