import os

dirname = os.path.abspath(os.path.dirname('sr.py'))
with open(os.path.join(dirname, 'sr.yaml'), 'r') as f:
    train = f.read()

from pylearn2.config import yaml_parse
train = yaml_parse.load(train)
train.main_loop()