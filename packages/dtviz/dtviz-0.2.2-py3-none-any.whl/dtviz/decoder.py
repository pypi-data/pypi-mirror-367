from hat import json

from packaging.requirements import Requirement

from dtviz import common


def get_project(project_type: common.ProjectType,
                name: str | None,
                data: json.Data
                ) -> common.Project:
    if name is None:
        name = _get_project_name(project_type, data)

    if name is None:
        raise Exception('name not defined')

    return common.Project(type=project_type,
                          name=name,
                          version=_get_project_version(project_type, data),
                          refs=list(_get_project_refs(project_type, data)))


def _get_project_name(project_type, data):
    if project_type == common.ProjectType.PYPROJECT_TOML:
        return data.get('project', {}).get('name')

    if project_type == common.ProjectType.PACKAGE_JSON:
        return data.get('name')


def _get_project_version(project_type, data):
    if project_type == common.ProjectType.PYPROJECT_TOML:
        return data.get('project', {}).get('version')

    if project_type == common.ProjectType.PACKAGE_JSON:
        return data.get('version')


def _get_project_refs(project_type, data):
    if project_type == common.ProjectType.PYPROJECT_TOML:
        for i in data.get('project', {}).get('dependencies', []):
            i = Requirement(i)

            yield common.ProjectRef(project=i.name,
                                    version=(str(i.specifier) if i.specifier
                                             else None),
                                    dev=False)

        for i in data.get('project', {}).get('optional-dependencies', {}).get('dev', []):  # NOQA
            i = Requirement(i)

            yield common.ProjectRef(project=i.name,
                                    version=(str(i.specifier) if i.specifier
                                             else None),
                                    dev=True)

    elif project_type == common.ProjectType.PACKAGE_JSON:
        for name, version in data['dependencies'].items():
            yield common.ProjectRef(project=name,
                                    version=version,
                                    dev=False)

        for name, version in data['devDependencies'].items():
            yield common.ProjectRef(project=name,
                                    version=version,
                                    dev=True)
