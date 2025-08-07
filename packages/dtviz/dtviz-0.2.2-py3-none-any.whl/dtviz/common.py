import enum
import typing


class ProjectType(enum.Enum):
    PYPROJECT_TOML = 'pyproject.toml'
    PACKAGE_JSON = 'package.json'


class Project(typing.NamedTuple):
    type: ProjectType
    name: str
    version: str | None
    refs: typing.List['ProjectRef']


class ProjectRef(typing.NamedTuple):
    project: str
    version: str | None
    dev: bool
