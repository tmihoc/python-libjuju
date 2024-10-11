# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import importlib
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, TypedDict

import pytest

from juju.client.connection import client_facades, excluded_facades


class Versions(TypedDict, total=True):
    versions: List[int]


ClientFacades = Dict[str, Versions]


@pytest.fixture
def project_root(pytestconfig: pytest.Config) -> Path:
    return pytestconfig.rootpath


@pytest.fixture
def generated_code_facades(project_root: Path) -> ClientFacades:
    """Return a client_facades dictionary from generated code under project_root.
    """
    facades: Dict[str, List[int]] = defaultdict(list)
    for file in (project_root / 'juju' / 'client').glob('_client[0-9]*.py'):
        module = importlib.import_module(f'juju.client.{file.stem}')
        for cls_name in dir(module):
            cls = getattr(module, cls_name)
            try:
                cls.name
                cls.version
            except AttributeError:
                continue
            if cls.version in excluded_facades.get(cls.name, []):
                continue
            facades[cls.name].append(cls.version)
    return {name: {'versions': sorted(facades[name])} for name in sorted(facades)}


def test_client_facades(project_root: Path, generated_code_facades: ClientFacades) -> None:
    assert {
        k: v['versions'] for k, v in client_facades.items()
    } == {
        k: v['versions'] for k, v in generated_code_facades.items()
    }
