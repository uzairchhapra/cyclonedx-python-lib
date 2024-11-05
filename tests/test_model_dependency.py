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

from unittest import TestCase

from cyclonedx.model.bom_ref import BomRef
from cyclonedx.model.dependency import Dependency
from tests import reorder


class TestDependency(TestCase):

    def test_sort(self) -> None:
        # expected sort order: (value)
        expected_order = [3, 2, 0, 1]
        deps = [
            Dependency(ref=BomRef(value='be2c6502-7e9a-47db-9a66-e34f729810a3'), dependencies=[
                Dependency(ref=BomRef(value='0b049d09-64c0-4490-a0f5-c84d9aacf857')),
                Dependency(ref=BomRef(value='17e3b199-dc0b-42ef-bfdd-1fa81a1e3eda'))
            ]),
            Dependency(ref=BomRef(value='cd3e9c95-9d41-49e7-9924-8cf0465ae789')),
            Dependency(ref=BomRef(value='17e3b199-dc0b-42ef-bfdd-1fa81a1e3eda')),
            Dependency(ref=BomRef(value='0b049d09-64c0-4490-a0f5-c84d9aacf857'), dependencies=[
                Dependency(ref=BomRef(value='cd3e9c95-9d41-49e7-9924-8cf0465ae789'))
            ])
        ]
        sorted_deps = sorted(deps)
        expected_deps = reorder(deps, expected_order)
        self.assertEqual(sorted_deps, expected_deps)

    def test_dependency_with_provides(self) -> None:
        # Create test data
        ref1 = BomRef(value='be2c6502-7e9a-47db-9a66-e34f729810a3')
        ref2 = BomRef(value='0b049d09-64c0-4490-a0f5-c84d9aacf857')
        provides_ref1 = BomRef(value='cd3e9c95-9d41-49e7-9924-8cf0465ae789')
        provides_ref2 = BomRef(value='17e3b199-dc0b-42ef-bfdd-1fa81a1e3eda')

        # Create dependencies with provides
        dep1 = Dependency(ref=ref1, provides=[Dependency(ref=provides_ref1)])
        dep2 = Dependency(ref=ref2, provides=[Dependency(ref=provides_ref2)])

        # Verify provides field
        self.assertEqual(len(dep1.provides), 1)
        self.assertEqual(len(dep2.provides), 1)

        # Check provides_as_bom_refs
        self.assertEqual(dep1.provides_as_bom_refs(), {provides_ref1})
        self.assertEqual(dep2.provides_as_bom_refs(), {provides_ref2})

        # Verify comparison and hashing
        self.assertNotEqual(hash(dep1), hash(dep2))
        self.assertNotEqual(dep1, dep2)
