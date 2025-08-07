from pathlib import Path
import getopt
import sys
import typing

from dtviz import common


class ProjectArgs(typing.NamedTuple):
    path: str
    type: common.ProjectType | None = None
    name: str | None = None
    aliases: list[str] = []


class Args(typing.NamedTuple):
    output: Path = Path('-')
    skip_external: bool = False
    skip_dev: bool = False
    dt_balance: str = 'max'
    log: str | None = None
    projects: typing.List[ProjectArgs] = []


usage = r"""Usage:
  dtviz [<global_option>]... [<project_path> [<project_option>]...]...

Dependency tree visualizer

Supported project paths:
  * local file path

Global options:
  --help             show usage
  --output           output path or '-' for stdout (default '-')
  --skip-external    skip external dependencies
  --skip-dev         skip development dependencies
  --dt-balance {min,max}
                     graphviz DTbalance attribute
  --log {CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET}
                     enable logging with provided minimal level
Project options:
  --type {pyproject.toml|package.json}
                     project type (override automatic detection)
  --name NAME        project name (override file definition)
  --alias ALIAS      project alias name (can occure multiple times)
"""


def fatal(msg: str | None):
    if msg:
        print(msg, file=sys.stderr)

    print(usage, file=sys.stderr)
    sys.exit(1)


def parse_args(argv: typing.List[str]
               ) -> Args:
    names = ['help', 'output=', 'skip-external', 'skip-dev', 'dt-balance=',
             'log=']

    try:
        result, rest = getopt.getopt(argv[1:], '', names)

    except getopt.GetoptError as e:
        fatal(str(e))

    args = Args(projects=[])
    for name, value in result:
        if name == '--help':
            fatal(None)

        elif name == '--output':
            args = args._replace(output=Path(value))

        elif name == '--skip-external':
            args = args._replace(skip_external=True)

        elif name == '--skip-dev':
            args = args._replace(skip_dev=True)

        elif name == '--dt-balance':
            if value not in {'min', 'max'}:
                fatal('invalid DTbalance')

            args = args._replace(dt_balance=value)

        elif name == '--log':
            if value not in {'CRITICAL', 'ERROR', 'WARNING', 'INFO',
                             'DEBUG', 'NOTSET'}:
                fatal('invalid log level')

            args = args._replace(log=value)

        else:
            raise ValueError('unsupported name')

    while rest:
        project_args, rest = _parse_project_args(rest)
        args.projects.append(project_args)

    return args


def _parse_project_args(argv):
    path = Path(argv[0])
    if not path.exists():
        fatal(f'invalid path: {argv[0]}')

    names = ['help', 'type=', 'name=', 'alias=']

    try:
        result, rest = getopt.getopt(argv[1:], '', names)

    except getopt.GetoptError as e:
        fatal(str(e))

    args = ProjectArgs(path=path,
                       aliases=[])
    for name, value in result:
        if name == '--help':
            fatal(None)

        elif name == '--type':
            try:
                args = args._replace(type=common.ProjectType(value))

            except Exception as e:
                fatal(str(e))

        elif name == '--name':
            args = args._replace(name=value)

        elif name == '--path':
            args = args._replace(path=Path(value))

        elif name == '--alias':
            args.aliases.append(value)

        raise ValueError('unsupported name')

    return args, rest
