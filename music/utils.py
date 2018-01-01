from pathlib import Path

import click


class DirType(click.ParamType):
    def convert(self, value, param, ctx):
        path = Path(value)
        if not path.exists() or not path.is_dir():
            opt1, opt2, *_ = param.opts
            raise ValueError(f'Invalid value for "{opt1}" / "{opt2}": directory "{value}" does not exist.')

        return path
