# Copyright (C) 2025 codimoc, codimoc@prismoid.uk

from . import rules
from ply import lex, yacc


class Parser:
    paths: rules.Paths = []

    def parse(self, data: str):
        "parse method to parse the grammar written in data"
        rules.paths = []
        lex.lex(module=rules)
        parser = yacc.yacc(module=rules)
        parser.parse(data)
        self.paths = rules.paths
