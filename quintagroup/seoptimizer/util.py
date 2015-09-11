from htmlentitydefs import entitydefs
import re


def _group_unescape(m):
    if m.group("ent"):
        try:
            return unescape(entitydefs[m.group("ent")])
        except KeyError:
            return m.group(0)
    if m.group("dec"):
        return unichr(int(m.group("dec")))
    if m.group("hex"):
        return unichr(int(m.group("hex"), 16))

expr = re.compile(r'&(?:(?P<ent>\w+?)|'
                  '#(?P<dec>\d{1,10})|'
                  '#x(?P<hex>[0-9a-fA-F]{1,8}));')


def unescape(s):
    return expr.sub(_group_unescape, s)
