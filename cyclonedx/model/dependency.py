# This file is part of CycloneDX Python Library
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
#
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) OWASP Foundation. All Rights Reserved.


from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Optional, Set

import serializable
from sortedcontainers import SortedSet

from .._internal.compare import ComparableTuple as _ComparableTuple
from ..exception.serialization import SerializationOfUnexpectedValueException
from ..serialization import BomRefHelper
from .bom_ref import BomRef


class _DependencyRepositorySerializationHelper(serializable.helpers.BaseHelper):
    """  THIS CLASS IS NON-PUBLIC API  """

    @classmethod
    def serialize(cls, o: Any) -> List[str]:
        if isinstance(o, (SortedSet, set)):
            return [str(i.ref) for i in o]
        raise SerializationOfUnexpectedValueException(
            f'Attempt to serialize a non-DependencyRepository: {o!r}')

    @classmethod
    def deserialize(cls, o: Any) -> Set['Dependency']:
        dependencies = set()
        if isinstance(o, list):
            for v in o:
                dependencies.add(Dependency(ref=BomRef(value=v)))
        return dependencies


@serializable.serializable_class
class Dependency:
    """
    Models a Dependency within a BOM.

    .. note::
        See:
        1. https://cyclonedx.org/docs/1.6/xml/#type_dependencyType
        2. https://cyclonedx.org/docs/1.6/json/#dependencies
    """

    def __init__(
        self,
        ref: BomRef,
        dependencies: Optional[Iterable['Dependency']] = None,
        provides: Optional[Iterable['Dependency']] = None
    ) -> None:
        self.ref = ref
        self.dependencies = dependencies or []  # type:ignore[assignment]
        self.provides = provides or []  # type:ignore[assignment]

    @property
    @serializable.type_mapping(BomRefHelper)
    @serializable.xml_attribute()
    def ref(self) -> BomRef:
        return self._ref

    @ref.setter
    def ref(self, ref: BomRef) -> None:
        self._ref = ref

    @property
    @serializable.json_name('dependsOn')
    @serializable.type_mapping(_DependencyRepositorySerializationHelper)
    @serializable.xml_array(serializable.XmlArraySerializationType.FLAT, 'dependency')
    def dependencies(self) -> 'SortedSet[Dependency]':
        return self._dependencies

    @dependencies.setter
    def dependencies(self, dependencies: Iterable['Dependency']) -> None:
        self._dependencies = SortedSet(dependencies)

    @property
    @serializable.json_name('provides')
    @serializable.type_mapping(_DependencyRepositorySerializationHelper)
    @serializable.xml_array(serializable.XmlArraySerializationType.FLAT, 'provides')
    def provides(self) -> 'SortedSet[Dependency]':
        return self._provides

    @provides.setter
    def provides(self, provides: Iterable['Dependency']) -> None:
        self._provides = SortedSet(provides)

    def dependencies_as_bom_refs(self) -> Set[BomRef]:
        return set(map(lambda d: d.ref, self.dependencies))

    def provides_as_bom_refs(self) -> Set[BomRef]:
        return set(map(lambda d: d.ref, self.provides))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Dependency):
            return hash(other) == hash(self)
        return False

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Dependency):
            return _ComparableTuple((
                self.ref,
                _ComparableTuple(self.dependencies),
                _ComparableTuple(self.provides)
            )) < _ComparableTuple((
                other.ref,
                _ComparableTuple(other.dependencies),
                _ComparableTuple(other.provides)
            ))
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.ref, tuple(self.dependencies), tuple(self.provides)))

    def __repr__(self) -> str:
        return (
            f'<Dependency ref={self.ref!r}'
            f', targets={len(self.dependencies)}'
            f', provides={len(self.provides)}>'
        )


class Dependable(ABC):
    """
    Dependable objects can be part of the Dependency Graph
    """

    @property
    @abstractmethod
    def bom_ref(self) -> BomRef:
        ...  # pragma: no cover
