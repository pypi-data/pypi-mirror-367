from pathlib import Path
import itertools
import logging.config
import sys

from hat import json

from dtviz import common
from dtviz import decoder
from dtviz import encoder
from dtviz.args import parse_args


def main():
    args = parse_args(sys.argv)

    if args.log:
        _set_logging(args.log)

    projects = {}
    aliases = {}
    data = {}

    for project_args in args.projects:
        project_type = (project_args.type or
                        common.ProjectType(project_args.path.name))
        project_data = json.decode_file(project_args.path)

        project = decoder.get_project(project_type, project_args.name,
                                      project_data)

        projects[project.name] = project
        data[project.name] = data
        for alias in project_args.aliases:
            aliases[alias] = project

    externals = set()
    name_ids = {name: i for i, name in enumerate(projects.keys())}
    next_name_ids = itertools.count(len(name_ids))

    for alias, project in aliases.items():
        name_ids[alias] = name_ids[project.name]

    for project in projects.values():
        for ref in project.refs:
            if ref.project in projects or ref.project in aliases:
                continue

            if ref.project in externals:
                continue

            externals.add(ref.project)
            name_ids[ref.project] = next(next_name_ids)

    output_stream = (open(args.output, 'w', encoding='utf-8')
                     if args.output != Path('-') else sys.stdout)
    try:
        encoder.write_header(stream=output_stream,
                             dt_balance=args.dt_balance)

        for project in projects.values():
            encoder.write_node(stream=output_stream,
                               node_id=name_ids[project.name],
                               name=project.name,
                               version=project.version,
                               is_external=False)

        if not args.skip_external:
            for name in externals:
                encoder.write_node(stream=output_stream,
                                   node_id=name_ids[name],
                                   name=name,
                                   version=None,
                                   is_external=True)

        for project in projects.values():
            for ref in project.refs:
                if args.skip_external and ref.project not in projects:
                    continue

                if args.skip_dev and ref.dev:
                    continue

                encoder.write_edge(stream=output_stream,
                                   src_id=name_ids[project.name],
                                   dst_id=name_ids[ref.project],
                                   version=ref.version,
                                   is_dev=ref.dev)

        encoder.write_footer(output_stream)

    finally:
        if output_stream != sys.stdout:
            output_stream.close()


def _set_logging(log_level):
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'formater': {
                'format': '[%(asctime)s %(levelname)s %(name)s] %(message)s'}},
        'handlers': {
            'handler': {
                'class': 'logging.StreamHandler',
                'formatter': 'formater',
                'level': log_level}},
        'root': {
            'level': log_level,
            'handlers': ['handler']},
        'disable_existing_loggers': False})


if __name__ == '__main__':
    sys.argv[0] = 'dtviz'
    sys.exit(main())
