# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
from __future__ import annotations

from enum import Enum
from urllib.parse import urlparse

from .errors import JujuError


class Schema(Enum):
    """Charm URL schema kinds."""

    LOCAL = "local"
    CHARM_STORE = "cs"
    CHARM_HUB = "ch"

    def matches(self, potential):
        return str(self.value) == str(potential)

    def __str__(self):
        return str(self.value)


class URL:
    """Private URL class for this library internals only.

    Should be instantiated by `URL.parse` constructor.
    """

    name: str

    def __init__(
        self,
        schema,
        user=None,
        name: str | None = None,
        revision=None,
        series=None,
        architecture=None,
    ):
        self.schema = schema
        self.user = user
        # the parse method will set the correct value later
        self.name = name  # type: ignore
        self.series = series

        # 0 can be a valid revision, hence the more verbose check.
        if revision is None:
            revision = -1
        self.revision = revision
        self.architecture = architecture

    @staticmethod
    def parse(s: str, default_store=Schema.CHARM_HUB) -> URL:
        """Parse parses the provided charm URL string into its respective
        structure.

        A missing schema is assumed to be 'ch'.

        """
        u = urlparse(s)
        if u.query != "" or u.fragment != "" or u.username or u.password:
            raise JujuError(f"charm or bundle URL {u} has unrecognized parts")

        if Schema.CHARM_STORE.matches(u.scheme) or (
            u.scheme == "" and Schema.CHARM_STORE.matches(default_store)
        ):
            c = parse_v1_url(Schema.CHARM_STORE, u, s)
        else:
            c = parse_v2_url(u, s, default_store)

        if not c or not c.schema:
            raise JujuError(f"expected schema for charm or bundle URL {u}")
        return c

    def with_revision(self, rev):
        return URL(
            self.schema, self.user, self.name, rev, self.series, self.architecture
        )

    def with_series(self, series):
        return URL(
            self.schema, self.user, self.name, self.revision, series, self.architecture
        )

    def path(self):
        parts = []
        if self.user is not None:
            parts.append(f"~{self.user}")
        if self.architecture is not None:
            parts.append(self.architecture)
        if self.series is not None:
            parts.append(self.series)
        if self.revision is not None and self.revision >= 0:
            parts.append(f"{self.name}-{self.revision}")
        else:
            parts.append(self.name)
        return "/".join(parts)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.schema == other.schema
                and self.user == other.user
                and self.name == other.name
                and self.revision == other.revision
                and self.series == other.series
                and self.architecture == other.architecture
            )
        return False

    def __str__(self):
        return f"{self.schema!s}:{self.path()}"


def parse_v1_url(schema, u, s) -> URL:
    c = URL(schema)

    parts = u.path.split("/")
    if len(parts) < 1 or len(parts) > 4:
        raise JujuError(f"charm or bundle URL has invalid form {s}")

    # ~<username>
    if parts[0].startswith("~"):
        if schema == Schema.LOCAL:
            raise JujuError(f"local charm or bundle URL with username {s}")
        c.user = parts[0][1:]
        parts = parts[1:]

    if len(parts) > 2:
        raise JujuError(f"charm or bundle URL has invalid form {s}")

    # <series>
    if len(parts) == 2:
        c.series = parts[0]
        parts = parts[1:]
        # TODO (stickupkid) - validate the series.

    if len(parts) < 1:
        raise JujuError(f"URL without charm or bundle name {s}")

    (c.name, c.revision) = extract_revision(parts[0])
    # TODO (stickupkid) - validate the name.

    return c


def parse_v2_url(u, s, default_store) -> URL:
    if not u.scheme:
        c = URL(default_store)
    elif Schema.CHARM_HUB.matches(u.scheme):
        c = URL(Schema.CHARM_HUB)
    elif Schema.LOCAL.matches(u.scheme):
        c = URL(Schema.LOCAL)
    else:
        raise JujuError(f"invalid charm url schema {u.scheme}")

    parts = u.path.split("/")
    num = len(parts)
    if num == 0 or num > 3:
        raise JujuError(f"charm or bundle URL {s} malformed")

    name = ""
    if num == 3:
        c.architecture, c.series, name = parts[0], parts[1], parts[2]
    elif num == 2:
        c.architecture, name = parts[0], parts[1]
    else:
        name = parts[0]

    (c.name, c.revision) = extract_revision(name)
    # TODO (stickupkid) - validate the name.

    return c


def extract_revision(name):
    revision = -1
    for i in range(len(name) - 1, -1, -1):
        c = name[i]
        if c.isnumeric():
            continue
        if c == "-" and i != (len(name) - 1):
            revision = int(name[(i + 1) :])
            name = name[:i]
        break
    return (name, revision)
