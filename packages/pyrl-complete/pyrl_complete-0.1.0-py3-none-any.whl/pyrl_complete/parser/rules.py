# Copyright (C) 2025 codimoc, codimoc@prismoid.uk

"""
Lexer and Parser rules
"""

from typing import List
import re

Paths = List[
    List[str]
]  # definition of a partial path in the command line, e.g. [["one", "two"]]


def merge(l1: Paths, l2: Paths) -> Paths:
    """
    l1 and l2 are list of partial paths. Each element is a list or partial
    set of tokens. This function performs a cartesian product from the two
    list and each element in the product is the concatenation of two
    elements from the original list
    """
    if l1 is None or len(l1) == 0:
        return l2
    if l2 is None or len(l2) == 0:
        return l1
    ret = []
    for i1 in l1:
        for i2 in l2:
            # each partial path from l1 is concatened with each partial path
            # from l2.
            # if l1 = [["one", "two"],["three"]] and l2 = [["four"]]
            # the result will be [["one","two","four"], ["three", "four"]]
            ret.append(i1 + i2)
    return ret


paths = []  # this is the output

# List of token names.   This is always required
tokens = (
    "WORD",
    "OPTION",
    "OR",
    "LBR",
    "RBR",
    "EOL",
    "LSB",
    "RSB",
    "EOS",  # end of statment separator
)

# Regular expression rules for simple tokens
t_OR = r"\|"
t_LBR = r"\("
t_RBR = r"\)"
t_LSB = r"\["
t_RSB = r"\]"
t_EOS = r";"


def t_WORD(t):
    r"[a-zA-Z_]+"  # a simple ford like: set
    t.value = [[t.value]]  # the value of the token is now a Paths object
    return t  # t is a token, its value is a Paths object


def t_OPTION(t):
    r"-[a-zA-Z]+(\s*\?+)?"  # an optional argument like: -d ? or -abc ?
    token = re.sub(r"\?+", "?", t.value)  # remove redundant ?
    # now format with one space between option letter and ?
    token = re.sub(r"(-[a-zA-Z]+)\s*(\?+)", r"\1 \2", token)
    t.value = [[token]]
    return t


# A regular expression rule with some action code
# Define a rule so we can track line numbers
def t_EOL(t):
    r"\n+"
    t.lexer.lineno += len(t.value)
    return t


# A string containing ignored characters (spaces and tabs)
t_ignore = " \t"


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
# lexer = lex.lex()


def p_all(p):
    """all : line
    | all line"""
    pass


def p_line(p):
    """line : path EOL
    | path EOS
    | path EOS EOL
    """
    if len(p) > 1:
        for pt in p[1]:
            paths.append(pt)
    pass


def p_path(p):
    """path : wrdopt
    | alternatives
    | collection
    | path wrdopt
    | path collection
    | path alternatives
    """
    if len(p) < 2:
        p[0] = list()
    elif len(p) < 3:
        p[0] = p[1]
    else:
        p[0] = merge(p[1], p[2])
    # paths.append(p[0])


def p_group(p):
    """group : LBR alternatives RBR
    | LBR path RBR
    """
    p[0] = p[2]


def p_optional_group(p):
    """ogroup : LSB alternatives RSB
    | LSB path RSB
    """
    p[0] = p[2] + [
        []
    ]  # this is an optional group so add an empty sub-path as alternative


def p_alternatives(p):
    """alternatives : alternatives OR wrdopt
    | alternatives OR collection
    | wrdopt OR collection
    | collection OR wrdopt
    | wrdopt OR wrdopt
    """
    p[0] = p[1] + p[3]


def p_word_or_option(p):
    """wrdopt : WORD
    | OPTION
    """
    p[0] = p[1]


def p_collection(p):
    """collection : group
    | ogroup
    """
    p[0] = p[1]
