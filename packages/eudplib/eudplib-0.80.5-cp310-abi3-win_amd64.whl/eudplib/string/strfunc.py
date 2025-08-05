# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .. import core as c
from .. import ctrlstru as cs
from ..memio import f_setcurpl2cpcache
from ..memio.rwcommon import br1, br2, bs1, bw1
from ..scdata import CurrentPlayer
from ..utils import EPD


@c.EUDFunc
def f_strcpy(dst, src):
    """
    Strcpy equivalent in eudplib. Copy C-style string.

    :param dst: Destination address (Not EPD player)
    :param src: Source address (Not EPD player)

    :return: dst
    """
    b = c.EUDVariable()

    br1.seekoffset(src)
    bw1.seekoffset(dst)

    if cs.EUDInfLoop()():
        c.SetVariables(b, br1.readbyte())
        bw1.writebyte(b)
        cs.EUDBreakIf(b == 0)
    cs.EUDEndInfLoop()

    return dst


@c.EUDFunc
def f_strcmp(s1, s2):
    br1.seekoffset(s1)
    br2.seekoffset(s2)

    if cs.EUDInfLoop()():
        ch1 = br1.readbyte()
        ch2 = br2.readbyte()
        if cs.EUDIf()(ch1 == ch2):
            if cs.EUDIf()(ch1 == 0):
                c.EUDReturn(0)
            cs.EUDEndIf()
            cs.EUDContinue()
        if cs.EUDElse()():
            c.EUDReturn(ch1 - ch2)
        cs.EUDEndIf()
    cs.EUDEndInfLoop()


def f_strlen_epd(epd, subp=0, /, **kwargs):
    return _strlen_epd(epd, subp, **kwargs)


@c.EUDFunc
def _strlen_epd(epd, subp):
    ret = c.EUDVariable()
    b = [c.Forward() for _ in range(4)]
    jump = c.SetNextPtr(epd.GetVTable(), 0)
    loopend = c.Forward()
    for i, t in enumerate(b):
        c.RawTrigger(
            conditions=subp.ExactlyX(i, 3),
            actions=[
                c.SetMemory(jump + 20, c.SetTo, t),
                c.SetNextPtr(t, loopend),
            ],
        )
    c.RawTrigger(
        nextptr=epd.GetVTable(),
        actions=[jump, epd.SetDest(EPD(0x6509B0)), ret.SetNumber(0)],
    )
    if cs.EUDInfLoop()():
        b[0] << c.RawTrigger(
            nextptr=loopend,
            conditions=c.DeathsX(CurrentPlayer, c.AtLeast, 1, 0, 0xFF),
            actions=[
                c.SetNextPtr(b[0], b[1]),
                c.SetNextPtr(b[1], loopend),
                ret.AddNumber(1),
            ],
        )
        b[1] << c.RawTrigger(
            nextptr=loopend,
            conditions=c.DeathsX(CurrentPlayer, c.AtLeast, 1, 0, 0xFF00),
            actions=[
                c.SetNextPtr(b[1], b[2]),
                c.SetNextPtr(b[2], loopend),
                ret.AddNumber(1),
            ],
        )
        b[2] << c.RawTrigger(
            nextptr=loopend,
            conditions=c.DeathsX(CurrentPlayer, c.AtLeast, 1, 0, 0xFF0000),
            actions=[
                c.SetNextPtr(b[2], b[3]),
                c.SetNextPtr(b[3], loopend),
                ret.AddNumber(1),
            ],
        )
        b[3] << c.RawTrigger(
            nextptr=loopend,
            conditions=c.DeathsX(CurrentPlayer, c.AtLeast, 1, 0, 0xFF000000),
            actions=[
                c.SetNextPtr(b[3], b[0]),
                c.SetNextPtr(b[0], loopend),
                ret.AddNumber(1),
                c.SetMemory(0x6509B0, c.Add, 1),
            ],
        )
    cs.EUDEndInfLoop()
    loopend << c.NextTrigger()
    f_setcurpl2cpcache()
    c.EUDReturn(ret)


def f_strlen(src, /, **kwargs):
    epd, subp = c.f_div(src, 4)
    epd += -0x58A364 // 4
    return f_strlen_epd(epd, subp, **kwargs)


@c.EUDFunc
def f_strnstr(string, substring, count):
    bs1.seekoffset(string)
    br2.seekoffset(substring)
    dst = c.EUDVariable()
    dst << -1

    b = br2.readbyte()
    if cs.EUDIf()(b == 0):
        c.EUDReturn(string)
    cs.EUDEndIf()
    if cs.EUDWhile()(count >= 1):
        a = bs1.readbyte()
        cs.DoActions(dst.AddNumber(1), count.SubtractNumber(1))
        cs.EUDBreakIf(a == 0)
        cs.EUDContinueIfNot(a == b)
        oldoffset, oldsuboffset = c.EUDCreateVariables(2)
        c.VProc(
            [bs1._offset, bs1._suboffset],
            [
                bs1._offset.SetDest(oldoffset),
                bs1._suboffset.SetDest(oldsuboffset),
            ],
        )
        if cs.EUDInfLoop()():
            d = br2.readbyte()
            if cs.EUDIf()(d == 0):
                c.EUDReturn(string + dst)
            cs.EUDEndIf()
            cs.EUDBreakIfNot(bs1.readbyte() == d)
        cs.EUDEndInfLoop()
        c.VProc(
            [oldoffset, oldsuboffset],
            [
                oldoffset.SetDest(bs1._offset),
                oldsuboffset.SetDest(bs1._suboffset),
            ],
        )
        br2.seekoffset(substring + 1)
    cs.EUDEndWhile()
    c.EUDReturn(-1)
