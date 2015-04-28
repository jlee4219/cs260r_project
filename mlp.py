import os

dirname = os.path.abspath(os.path.dirname('mlp.py'))
with open(os.path.join(dirname, 'mlp.yaml'), 'r') as f:
    train = f.read()

from pylearn2.config import yaml_parse
train = yaml_parse.load(train)
print train
train.main_loop()