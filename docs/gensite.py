# Hacked together static site system
from jinja2 import Environment, FileSystemLoader, select_autoescape
import glob
import os

docs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(docs_path, 'src')

env = Environment(
    loader=FileSystemLoader(src_path),
    autoescape=select_autoescape(['html'])
)

for filepath in glob.glob(os.path.join(src_path, '*')):
    if os.path.isdir(filepath):
        continue
    filename = os.path.basename(filepath)
    template = env.get_template(filename)
    context = {}
    result = template.render(**context)
    with open(os.path.join(docs_path, filename), 'w+') as fd:
        print('Writing to %s' % filename)
        fd.write(result)

async def _py35_only(): pass # ensure syntax error
