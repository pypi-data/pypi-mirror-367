# Copyright (C) 2025 codimoc, codimoc@prismoid.uk

from . import rules
from .rules import Paths
from . import parser
from . import tree

# redefinition to simplify namespace
Parser = parser.Parser
Node = tree.Node
Tree = tree.Tree


def clear():
    rules.paths = []


def paths() -> Paths:
    return rules.paths
