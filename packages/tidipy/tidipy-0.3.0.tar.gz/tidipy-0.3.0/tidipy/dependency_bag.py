from __future__ import annotations

from typing import Optional, Type

from .resolver import Resolver
from .dependency import Dependency, ConcreteDependency, Composer


class DependencyBag:
    def __init__(self, dependencies: dict[str, Dependency]):
        self._dependencies = dependencies

    @staticmethod
    def empty() -> DependencyBag:
        return DependencyBag({})

    def add(self, dependency: Dependency) -> DependencyBag:
        return DependencyBag(
            {
                **self._dependencies,
                dependency.get_id(): dependency
            }
        )

    def remove(self, filter_values: dict[str, str]) -> DependencyBag:
        return DependencyBag(
            {
                dependency_id: dependency
                for dependency_id, dependency in self._dependencies.items()
                if dependency.get_conditions().is_fulfilled_by(filter_values)
            }
        )

    def _get_from_dependency(self, dependency: Dependency, resolver: Resolver):
        concrete = dependency.make_concrete(resolver)

        if dependency.supports_storing():
            self._dependencies[dependency.get_id()] = concrete

        return concrete.value

    def find(
        self,
        dependency_type: Type,
        dependency_id: Optional[str],
        resolver: Resolver
    ) -> Optional[Dependency]:
        candidates = [
            dependency
            for dependency in self._dependencies.values()
            if issubclass(dependency.get_dependency_type(), dependency_type)
        ]
        if dependency_id is not None:
            candidates = [dependency for dependency in candidates if dependency.get_id() == dependency_id]
        if len(candidates) == 1:
            dependency = next(iter(candidates))
            return self._get_from_dependency(dependency, resolver)
        if len(candidates) > 1:
            raise Exception(f'More than 1 candidate for type {dependency_type}')

        return None
