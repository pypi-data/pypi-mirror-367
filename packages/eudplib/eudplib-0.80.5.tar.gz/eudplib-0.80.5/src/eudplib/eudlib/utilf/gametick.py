# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from ...memio import f_dwread_epd


@c.EUDFunc
def f_getgametick():
    """Get current game tick value."""

    gametick_cache = c.EUDVariable()
    _gametick_cond = c.Forward()

    if cs.EUDIfNot()([_gametick_cond << c.Memory(0x57F23C, c.Exactly, 0)]):
        f_dwread_epd(ut.EPD(0x57F23C), ret=[gametick_cache])
        c.SetVariables(ut.EPD(_gametick_cond) + 2, gametick_cache)
    cs.EUDEndIf()

    return gametick_cache
