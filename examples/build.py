import argparse
import ast
import sys
from pathlib import Path

import joy
import cairosvg

p = argparse.ArgumentParser()
p.add_argument("filename")
p.add_argument("-o", "--output", help="output filename")
args = p.parse_args()

if args.output is None:
    args.output = args.filename.replace(".py", ".png")

code = open(args.filename).read()

SHAPES = []

def show(*shapes):
    SHAPES.extend(shapes)

def exec_notebook(code, env):
    """Exec the code in the nodebook mode.

    In the notebook mode, the last expression is displayed.
    """
    mod = ast.parse(code)
    head = ast.Module(mod.body[:-1], [])
    tail = ast.Interactive(mod.body[-1:])

    def do_exec(node, mode):
        code_obj = compile(node, "<input>", mode)
        exec(code_obj, env)

    do_exec(head, "exec")
    do_exec(tail, "single")

_displayhook = sys.displayhook

def displayhook(obj):
    if isinstance(obj, joy.Shape):
        show(obj)
    else:
        _displayhook(obj)
sys.displayhook = displayhook

env = joy.__dict__
env['show'] = show
exec_notebook(code, env)

if SHAPES:
    shape = joy.combine(SHAPES) | joy.scale(x=1, y=-1)
    svg = shape.as_svg()
    #cairosvg.svg2png(svg, write_to=args.output)
    Path(args.output).write_text(svg)

