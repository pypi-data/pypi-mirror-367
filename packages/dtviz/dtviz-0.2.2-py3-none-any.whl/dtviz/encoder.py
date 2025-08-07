import io


def write_header(stream: io.TextIOBase,
                 dt_balance: str):
    stream.write('digraph {\n')
    stream.write(f'TBbalance={dt_balance}\n')
    stream.write('rankdir=BT\n')


def write_footer(stream: io.TextIOBase):
    stream.write('}\n')


def write_node(stream: io.TextIOBase,
               node_id: int,
               name: str,
               version: str | None,
               is_external: bool):
    label = f'{name}\\n{version}' if version else name

    attrs = [f'label="{label}"']

    if is_external:
        attrs.append('style=dashed')

    else:
        attrs.append('shape=box')

    stream.write(f'node{node_id} [{",".join(attrs)}];\n')


def write_edge(stream: io.TextIOBase,
               src_id: int,
               dst_id: int,
               version: str | None,
               is_dev: bool):
    attrs = []

    if version:
        attrs.append(f'label="{version}"')

    if is_dev:
        attrs.append('style=dashed')

    stream.write(f'node{src_id} -> node{dst_id} [{",".join(attrs)}];\n')
