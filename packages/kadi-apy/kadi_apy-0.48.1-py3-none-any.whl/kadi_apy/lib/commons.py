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
import json
from datetime import timedelta

from kadi_apy.lib.exceptions import KadiAPYRequestError
from kadi_apy.lib.utils import _utcnow
from kadi_apy.lib.utils import chunked_response


class RequestMixin:
    """Mixin class to add request-related functionality."""

    def __init__(self, manager):
        self.manager = manager

    def _get(self, endpoint, **kwargs):
        return self.manager._get(endpoint, **kwargs)

    def _post(self, endpoint, **kwargs):
        return self.manager._post(endpoint, **kwargs)

    def _patch(self, endpoint, **kwargs):
        if hasattr(self, "_meta"):
            self._meta = None
        return self.manager._patch(endpoint, **kwargs)

    def _put(self, endpoint, **kwargs):
        return self.manager._put(endpoint, **kwargs)

    def _delete(self, endpoint, **kwargs):
        if hasattr(self, "_meta"):
            self._meta = None
        return self.manager._delete(endpoint, **kwargs)


class VerboseMixin:
    """Mixin class to add basic logging functionality."""

    def error(self, text, **kwargs):
        r"""Print text for error level.

        :param text: Text to be printed via :func:`click.echo()`.
        :type text: str
        :param \**kwargs: Additional arguments to pass to :func:`click.echo()`.
        """

        self.manager.error(text=text, **kwargs)

    def warning(self, text, **kwargs):
        r"""Print text for warning level.

        :param text: Text to be printed via :func:`click.echo()`.
        :type text: str
        :param \**kwargs: Additional arguments to pass to :func:`click.echo()`.
        """

        self.manager.warning(text=text, **kwargs)

    def info(self, text, **kwargs):
        r"""Print text for info level.

        :param text: Text to be printed via :func:`click.echo()`.
        :type text: str
        :param \**kwargs: Additional arguments to pass to :func:`click.echo()`.
        """

        self.manager.info(text=text, **kwargs)

    def debug(self, text, **kwargs):
        r"""Print text for debug level.

        :param text: Text to be printed via :func:`click.echo()`.
        :type text: str
        :param \**kwargs: Additional arguments to pass to :func:`click.echo()`.
        """

        self.manager.debug(text=text, **kwargs)

    def is_verbose(self, **kwargs):
        """Check the verbose level.

        :return: See :meth:`.KadiManager.is_verbose`.
        """

        return self.manager.is_verbose(**kwargs)


class PermissionMixin:
    """Mixin class to add user and group role management functionality."""

    def add_user(self, user_id, role_name):
        """Add a user role.

        :param user_id: The ID of the user to add.
        :type user_id: int
        :param role_name: Role of the User.
        :type role_name: str
        :return: The Response object.
        """
        endpoint = f"{self.base_path}/{self.id}/roles/users"
        data = {"role": {"name": role_name}, "user": {"id": user_id}}

        return self._post(endpoint, json=data)

    def change_user_role(self, user_id, role_name):
        """Change user role.

        :param user_id: The ID of the user whose role should be changed.
        :type user_id: int
        :param role_name: Name of the new role.
        :type role_name: str
        :return: The response object.
        """

        endpoint = f"{self.base_path}/{self.id}/roles/users/{user_id}"
        data = {"name": role_name}
        return self._patch(endpoint, json=data)

    def remove_user(self, user_id):
        """Remove a user role.

        :param user_id: The ID of the user to remove.
        :type user_id: int
        :return: The response object.
        """
        endpoint = f"{self.base_path}/{self.id}/roles/users/{user_id}"
        return self._delete(endpoint, json=None)

    def add_group_role(self, group_id, role_name):
        """Add a group role.

        :param group_id: The ID of the group to add.
        :type group_id: int
        :param role_name: Role of the group.
        :type role_name: str
        :return: The response object.
        """
        endpoint = f"{self.base_path}/{self.id}/roles/groups"
        data = {"role": {"name": role_name}, "group": {"id": group_id}}

        return self._post(endpoint, json=data)

    def change_group_role(self, group_id, role_name):
        """Change group role.

        :param group_id: The ID of the group whose role should be changed.
        :type group_id: int
        :param role_name: Name of the new role.
        :type role_name: str
        :return: The response object.
        """
        endpoint = f"{self.base_path}/{self.id}/roles/groups/{group_id}"
        data = {"name": role_name}

        return self._patch(endpoint, json=data)

    def remove_group_role(self, group_id):
        """Remove a group role.

        :param group_id: The ID of the group to remove.
        :type group_id: int
        :return: The response object.
        """
        endpoint = f"{self.base_path}/{self.id}/roles/groups/{group_id}"
        return self._delete(endpoint, json=None)


class TagMixin:
    """Mixin class to add tag management functionality."""

    def get_tags(self):
        """Get tags.

        :return: A list of all tags.
        :type: list
        """
        return self.meta["tags"]

    def check_tag(self, tag):
        """Check if a certain tag is already present.

        :param tag: The tag to check.
        :type tag: str
        :return: ``True`` if tag already exists, otherwise ``False``.
        :rtype: bool
        """
        return tag.lower() in self.get_tags()

    def add_tag(self, tag):
        """Add a tag.

        :param tag: The tag to add.
        :type tag: str
        :return: The response object.
        """
        endpoint = f"{self.base_path}/{self.id}"
        tags = self.get_tags()

        return self._patch(endpoint, json={"tags": tags + [tag.lower()]})

    def remove_tag(self, tag):
        """Remove a tag.

        :param tag: The tag to remove.
        :type tag: str
        :return: The response object.
        """
        endpoint = f"{self.base_path}/{self.id}"

        tag = tag.lower()
        tags = [t for t in self.get_tags() if t != tag]

        return self._patch(endpoint, json={"tags": tags})


class ExportMixin:
    """Mixin class to add resource export functionality."""

    def export(self, path, export_type="json", pipe=False, **params):
        r"""Export a resource using a specific export type.

        :param path: The path (including name of the file) to store the exported data.
        :type path: str
        :param export_type: The export format.
        :type export_type: str
        :param pipe: If ``True``, nothing is written here.
        :type pipe: bool
        :param \**params: Additional query parameters.
        :return: The response object.
        """
        if isinstance(params.get("filter"), dict):
            params["filter"] = json.dumps(params["filter"])

        response = self._get(
            f"{self.base_path}/{self.id}/export/{export_type}",
            params=params,
            stream=True,
        )

        if not pipe and response.status_code == 200:
            chunked_response(path, response)

        return response


class ResourceMeta(RequestMixin, VerboseMixin):
    """Mixing class to add resource metadata handling functionality."""

    def __init__(self, manager):
        super().__init__(manager)
        self._meta = None
        self._last_update = None

    @property
    def meta(self):
        """Get all metadata of the resource.

        In case the previous metadata was invalidated, either manually, after a timeout
        or due to another request, a request will be sent to retrieve the possibly
        updated metadata again.

        :return: The metadata of the resource.
        :raises KadiAPYRequestError: If requesting the metadata was not successful.
        """

        if self._last_update is not None:
            # Invalidate the cached metadata automatically after 5 minutes.
            if (_utcnow() - self._last_update) > timedelta(minutes=5):
                self._meta = None

        if self._meta is None:
            response = self._get(f"{self.base_path}/{self.id}")
            if response.status_code != 200:
                raise KadiAPYRequestError(response.json())

            self._meta = response.json()
            self._last_update = _utcnow()

        return self._meta
