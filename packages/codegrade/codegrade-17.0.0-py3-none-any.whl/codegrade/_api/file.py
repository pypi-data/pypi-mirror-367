"""The endpoints for file objects.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

from __future__ import annotations

import os
import typing as t

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from .. import parsers, utils

if t.TYPE_CHECKING or os.getenv("CG_EAGERIMPORT", False):
    from .. import client
    from ..models.mirror_file_result import MirrorFileResult


_ClientT = t.TypeVar("_ClientT", bound="client._BaseClient")


class FileService(t.Generic[_ClientT]):
    __slots__ = ("__client",)

    def __init__(self, client: _ClientT) -> None:
        self.__client = client

    def download(
        self,
        *,
        filename: str,
        mime: Maybe[str] = Nothing,
        as_attachment: bool = False,
        name: Maybe[str] = Nothing,
    ) -> bytes:
        """Serve some specific file in the uploads folder.

        Warning: The file will be deleted after you download it!

        :param filename: The filename of the file to get.
        :param mime: The mime type header to set on the response.
        :param as_attachment: If truthy the response will have a
            `Content-Disposition: attachment` header set.
        :param name: The filename for the attachment, defaults to the second
            part of the url.

        :returns: The requested file.
        """

        url = "/api/v1/files/{filename}".format(filename=filename)
        params: t.Dict[str, t.Any] = {
            "as_attachment": utils.to_dict(as_attachment),
        }
        maybe_from_nullable(t.cast(t.Any, mime)).if_just(
            lambda val: params.__setitem__("mime", val)
        )
        maybe_from_nullable(t.cast(t.Any, name)).if_just(
            lambda val: params.__setitem__("name", val)
        )

        with self.__client as client:
            resp = client.http.get(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            return parsers.ResponsePropertyParser("content", bytes).try_parse(
                resp
            )

        from ..models.any_error import AnyError

        raise utils.get_error(
            resp,
            (
                (
                    (400, 409, 401, 403, 404, 429, 500),
                    utils.unpack_union(AnyError),
                ),
            ),
        )

    def upload(
        self: FileService[client.AuthenticatedClient],
        *,
        max_age: Maybe[int] = Nothing,
        filename: str = "uploaded_file",
        ephemeral: bool = False,
    ) -> MirrorFileResult:
        """Temporarily store some data on the server.

        :param max_age: The maximum amount of time (in seconds) this file will
            stay valid and can be retrieved.
        :param filename: The name of the uploaded file.
        :param ephemeral: If set this file will be never saved to persistent
            storage. The maximum size of file that can be uploaded like this is
            1mb.

        :returns: The data for the file you can download on our server.
        """

        url = "/api/v1/files/"
        params: t.Dict[str, t.Any] = {
            "filename": utils.to_dict(filename),
            "ephemeral": utils.to_dict(ephemeral),
        }
        maybe_from_nullable(t.cast(t.Any, max_age)).if_just(
            lambda val: params.__setitem__("max_age", val)
        )

        with self.__client as client:
            resp = client.http.post(url=url, params=params)
        utils.log_warnings(resp)

        if utils.response_code_matches(resp.status_code, 200):
            from ..models.mirror_file_result import MirrorFileResult

            return parsers.JsonResponseParser(
                parsers.ParserFor.make(MirrorFileResult)
            ).try_parse(resp)

        from ..models.any_error import AnyError

        raise utils.get_error(
            resp,
            (
                (
                    (400, 409, 401, 403, 404, 429, 500),
                    utils.unpack_union(AnyError),
                ),
            ),
        )
