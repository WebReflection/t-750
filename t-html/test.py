from thtml.parser import _instrument
from thtml.utils import _parse
from random import random

prefix = '🐍' + str(random())[2:5]

print(_instrument(["<div />"], prefix, False))
print(_instrument(["<rect />"], prefix, True))
print(_instrument(["<div></div>"], prefix, False))
print(_instrument(["<div></div>"], prefix, True))

print(_instrument(["<div test=", "></div>"], prefix, False))

