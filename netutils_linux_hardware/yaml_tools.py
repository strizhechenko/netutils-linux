# coding=utf-8

import yaml


def dict2yaml(d):
    """ Converts nested dicts in pretty YAML """
    return yaml.dump(d, default_flow_style=False).strip()
