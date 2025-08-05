# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..utils import EPD
from .allocator import Forward
from .rawtrigger import Add, EncodePlayer, Exactly, Memory, SetMemory, SetTo
from .variable import EUDXVariable

_curpl_var = EUDXVariable(EPD(0x6509B0), SetTo, 0)
_curpl_checkcond = Forward()


def cpcache_match_cond():
    if not _curpl_checkcond.IsSet():
        _curpl_checkcond << Memory(0x6509B0, Exactly, 0)
    return _curpl_checkcond


def SetCurrentPlayer(p):  # noqa: N802
    p = EncodePlayer(p)
    return [
        _curpl_var.SetNumber(p),
        SetMemory(_curpl_checkcond + 8, SetTo, p),
        SetMemory(0x6509B0, SetTo, p),
    ]


def AddCurrentPlayer(p):  # noqa: N802
    p = EncodePlayer(p)
    return [
        _curpl_var.AddNumber(p),
        SetMemory(_curpl_checkcond + 8, Add, p),
        SetMemory(0x6509B0, Add, p),
    ]


def GetCPCache():  # noqa: N802
    return _curpl_var
