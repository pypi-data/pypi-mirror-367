# Copyright 2020 Karlsruhe Institute of Technology
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

import click
from xmlhelpy import Choice
from xmlhelpy import Path
from xmlhelpy import option

from kadi_apy.cli.decorators import apy_command
from kadi_apy.cli.decorators import search_pagination_options
from kadi_apy.cli.main import kadi_apy
from kadi_apy.globals import RESOURCE_TYPES
from kadi_apy.lib.misc import _copy_records
from kadi_apy.lib.utils import _get_record_identifiers
from kadi_apy.lib.utils import append_identifier_suffix
from kadi_apy.lib.utils import error
from kadi_apy.lib.utils import get_resource_type


@kadi_apy.group()
def misc():
    """Commands for miscellaneous functionality."""


@misc.command()
@apy_command
@search_pagination_options
@option(
    "filter",
    char="f",
    description="Filter by title or identifier.",
    default="",
)
def get_deleted_resources(manager, **kwargs):
    """Show a list of deleted resources in the trash."""

    manager.misc.get_deleted_resources(**kwargs)


@misc.command()
@apy_command
@option(
    "item-type",
    char="t",
    description="Type of the resource to restore.",
    param_type=Choice(RESOURCE_TYPES),
    required=True,
)
@option(
    "item-id",
    char="i",
    description="ID of the resource to restore.",
    required=True,
)
def restore_resource(manager, item_type, item_id):
    """Restore a resource from the trash."""

    item = get_resource_type(item_type)

    manager.misc.restore(item=item, item_id=item_id)


@misc.command()
@apy_command
@option(
    "item-type",
    char="t",
    description="Type of the resource to purge.",
    param_type=Choice(RESOURCE_TYPES),
    required=True,
)
@option(
    "item-id",
    char="i",
    description="ID of the resource to purge.",
    required=True,
)
def purge_resource(manager, item_type, item_id):
    """Purge a resource from the trash."""

    item = get_resource_type(item_type)

    manager.misc.purge(item=item, item_id=item_id)


@misc.command()
@apy_command
@search_pagination_options
@option(
    "filter",
    char="f",
    description="Filter.",
    default="",
)
def get_licenses(manager, **kwargs):
    """Show a list available licenses."""

    manager.misc.get_licenses(**kwargs)


@misc.command()
@apy_command
@option(
    "item-type",
    char="t",
    description="Show only roles of this resource.",
    param_type=Choice(["record", "collection", "template", "group"]),
)
def get_roles(manager, item_type):
    """Show a list of roles and corresponding permissions of all resources."""

    manager.misc.get_roles(item_type)


@misc.command()
@apy_command
@search_pagination_options
@option(
    "filter",
    char="f",
    description="Filter.",
    default="",
)
@option(
    "type",
    char="t",
    description="A resource type to limit the tags to.",
    default=None,
    param_type=Choice(["record", "collection"]),
)
def get_tags(manager, **kwargs):
    """Show a list available tags."""

    manager.misc.get_tags(**kwargs)


@misc.command()
@apy_command(use_kadi_manager=True)
@option(
    "path",
    char="p",
    description="Path of the ELN file to import.",
    param_type=Path(exists=True, path_type="file"),
    required=True,
)
def import_eln(manager, path):
    """Import an RO-Crate file following the "ELN" file specification."""
    manager.misc.import_eln(path)

    click.echo("File has been imported successfully.")


@misc.command()
@apy_command(use_kadi_manager=True)
@option(
    "path",
    char="p",
    description="Path of the JSON Schema file to import.",
    param_type=Path(exists=True, path_type="file"),
    required=True,
)
@option(
    "type",
    char="y",
    description="Type of the template to create from JSON Schema.",
    param_type=Choice(["extras", "record"]),
    default="extras",
    var_name="template_type",
)
def import_json_schema(manager, path, template_type):
    """Import JSON Schema file and create a template."""
    manager.misc.import_json_schema(path, template_type)

    click.echo("File has been imported successfully.")


@misc.command()
@apy_command(use_kadi_manager=True)
@option(
    "path",
    char="p",
    description="Path of the SHACl file to import.",
    param_type=Path(exists=True, path_type="file"),
    required=True,
)
@option(
    "type",
    char="y",
    description="Type of the template to create from SHACL shapes.",
    param_type=Choice(["extras", "record"]),
    default="extras",
    var_name="template_type",
)
def import_shacl(manager, path, template_type):
    """Import SHACL file and create a template."""
    manager.misc.import_shacl(path, template_type)

    click.echo("File has been imported successfully.")


@misc.command()
@apy_command(use_kadi_manager=True)
@option("collection-id", char="c", description="ID of the collection.", required=True)
@option("suffix", char="s", description="Suffix to append to identifiers.")
@option(
    "linked_records",
    char="l",
    description="Specify the record IDs to be linked"
    "into the new collection without modifying them",
)
@option(
    "records",
    char="r",
    description="Specify 'all' to modify all records without selection. Alternatively,"
    " provide record IDs separated by commas (e.g. 101,205).",
)
@option(
    "interactive",
    char="i",
    is_flag=True,
    default=False,
    description="Run the command in interactive mode for record selection and prompts.",
)
@option(
    "extras_value",
    char="v",
    is_flag=True,
    default=False,
    description="Preserve all values in extra metadata of the record (skip cleaning).",
)
def reuse_collection(
    manager,
    collection_id,
    suffix=None,
    records=None,
    linked_records=None,
    interactive=False,
    extras_value=False,
):
    """Reuse an existing collection by creating a new one.

    Creates a new collection by reusing records from an existing collection.
    It allows users to modify selected records by appending a specified suffix to
    their identifiers, while optionally linking other records without modification.
    All relationships between records are preserved in the new collection.
    """

    def valid_numeric_input(user_input, allow_ranges=False):
        allowed_chars = ",-" if allow_ranges else ","
        cleaned_input = user_input.translate(str.maketrans("", "", allowed_chars))
        return cleaned_input.isdigit()

    def valid_selection_input(user_input, max_index):
        selected_numbers = set()
        for part in user_input.split(","):
            if "-" in part:
                start, end = part.split("-")
                start = int(start) if start else 1
                end = int(end) if end else max_index
                if start > end or start < 1 or end > max_index:
                    error(
                        f"Invalid range '{part}'."
                        f"Ensure numbers are in order and within 1 to {max_index}."
                    )
                selected_numbers.update(range(start, end + 1))
            else:
                number = int(part)
                if number < 1 or number > max_index:
                    error(
                        f"Invalid number: {number}."
                        f"Please enter numbers within 1 to {max_index}."
                    )

                selected_numbers.add(number)
        return selected_numbers

    def valid_record_ids(input_str, valid_ids):
        if not valid_numeric_input(input_str, allow_ranges=False):
            error("Invalid input format.")
        ids = {int(x.strip()) for x in input_str.split(",")}
        invalid = [rid for rid in ids if rid not in valid_ids]
        if invalid:
            error(f"Invalid record IDs: {invalid}.")
        return ids

    collection = manager.collection(id=collection_id)
    id_to_identifier = _get_record_identifiers(collection)
    all_record_identifiers = list(id_to_identifier.values())
    selected_record_identifiers = []
    if records:
        if records.lower() == "all":
            selected_record_identifiers = all_record_identifiers
        else:
            selected_ids = valid_record_ids(records, id_to_identifier.keys())
            selected_record_identifiers = [id_to_identifier[id] for id in selected_ids]
    elif interactive:
        click.echo("Records available in the collection:")
        for idx, identifier in enumerate(all_record_identifiers, start=1):
            click.echo(f"{idx}: {identifier}")
        if click.confirm("Do you want to modify all records?", default=True):
            selected_record_identifiers = all_record_identifiers
        else:
            selected_input = click.prompt(
                "Enter record numbers or ranges separated by a comma (e.g. 1-3,5),"
                " or press Enter to skip modifying records",
                default="",
                show_default=False,
            )
            if selected_input.strip() == "":
                selected_record_identifiers = []
            else:
                if not valid_numeric_input(selected_input, allow_ranges=True):
                    error("Invalid input format.")

                selected_numbers = valid_selection_input(
                    selected_input, len(all_record_identifiers)
                )
                selected_record_identifiers = [
                    all_record_identifiers[num - 1] for num in selected_numbers
                ]
    click.echo(f"Selected records for modification: {selected_record_identifiers}")
    remaining_identifiers = [
        i for i in all_record_identifiers if i not in selected_record_identifiers
    ]
    remaining_ids = [
        rid
        for rid, identifier in id_to_identifier.items()
        if identifier not in selected_record_identifiers
    ]
    linked_record_map = {}
    if linked_records:
        reuse_ids = valid_record_ids(linked_records, remaining_ids)
        for id in reuse_ids:
            identifier = id_to_identifier[id]
            linked_record_map[identifier] = identifier
    elif (
        interactive
        and remaining_identifiers
        and click.confirm(
            "Do you also want to link some records "
            "to the collection without modification?",
            default=False,
        )
    ):
        click.echo("Records available for linking:")
        for idx, identifier in enumerate(remaining_identifiers, start=1):
            click.echo(f"{idx}: {identifier}")
        reuse_input = click.prompt(
            "Enter record numbers or ranges to link, separated by commas (e.g. 1-3,5)",
            default="",
            show_default=False,
        )
        if not valid_numeric_input(reuse_input, allow_ranges=True):
            error("Invalid input format for reuse records.")

        reuse_numbers = valid_selection_input(reuse_input, len(remaining_identifiers))
        for num in reuse_numbers:
            identifier = remaining_identifiers[num - 1]
            linked_record_map[identifier] = identifier
    click.echo(f"Selected records for linkage: {list(linked_record_map.keys())}")
    # Validate suffix for characters and length of the identifier.
    if not selected_record_identifiers and not linked_record_map:
        if not interactive:
            error(
                "No records provided. "
                "Use --records or --linked_records in non-interactive mode."
            )
        else:
            error("No records were selected for linkage or modification.")
    if interactive and not extras_value:
        extras_value = click.confirm(
            "Do you want to copy values from record extra metadata?", default=False
        )
    if not suffix:
        if not interactive:
            error("Suffix is required in non-interactive mode.")
        suffix = click.prompt(
            "Enter a suffix to append to identifiers of modified records and collection"
        )

    new_collection_identifier = append_identifier_suffix(
        collection.meta["identifier"], suffix
    )
    new_collection = manager.collection(
        title=collection.meta["title"],
        identifier=new_collection_identifier,
        description=collection.meta["description"],
        tags=collection.meta["tags"],
        visibility=collection.meta["visibility"],
        create=True,
    )

    combined_identifiers = list(
        dict.fromkeys(selected_record_identifiers + list(linked_record_map.keys()))
    )
    _copy_records(
        manager,
        new_collection,
        combined_identifiers,
        suffix,
        linked_record_map,
        extras_value,
    )
    collection.add_collection_link(collection_id=new_collection.id)
    click.echo(
        f"A new collection '{new_collection_identifier}' "
        f"with {len(combined_identifiers)} records has been created."
    )
