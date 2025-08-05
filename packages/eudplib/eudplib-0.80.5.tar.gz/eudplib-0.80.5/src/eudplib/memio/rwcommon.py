# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..core.eudstruct.vararray import _lv
from .byterw import EUDByteReader, EUDByteStream, EUDByteWriter
from .cpbyterw import CPByteWriter

lv = _lv
cw = CPByteWriter()
br1 = EUDByteReader()
br2 = EUDByteReader()
# br3 = bm.EUDByteReader()
bw1 = EUDByteWriter()
# bw2 = bm.EUDByteWriter()
# bw3 = bm.EUDByteWriter()
bs1 = EUDByteStream()
