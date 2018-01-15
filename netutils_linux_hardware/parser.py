# coding: utf-8
# pylint: disable=C0111, C0103

import os

import yaml


class Parser(object):
    def __init__(self, filepath=None):
        self.result = self.parse_file_safe(filepath) if filepath else None

    def parse(text, **kwargs):
        raise NotImplementedError

    def parse_file(self, filepath, **kwargs):
        with open(filepath) as file_for_parse:
            return self.parse(file_for_parse.read().strip(), **kwargs)

    def parse_file_safe(self, filepath, **kwargs):
        if os.path.isfile(filepath):
            return self.parse_file(filepath, **kwargs)


class YAMLLike(Parser):
    @staticmethod
    def parse(text):
        return yaml.load(text)
