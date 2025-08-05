# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Callable
from typing import overload

from ...localize import _
from ...utils import EPError, ExprProxy, unProxy
from .. import variable as ev
from ..mapdata import GetPropertyIndex, UnitProperty
from .consttype import (
    ConstType,
    T,
    U,
    __Arg,
    __ExprProxy,
    _Arg,
    _Byte,
    _Dword,
    _ExprProxy,
)

# fmt: off


class TrgAllyStatus(ConstType):
    __slots__ = ()

    def __str__(self):
        try:
            return {0: "Enemy", 1: "Ally", 2: "AlliedVictory"}[self._value]
        except KeyError:
            return super().__str__()


Enemy, Ally, AlliedVictory = TrgAllyStatus(0), TrgAllyStatus(1), TrgAllyStatus(2)
AllyStatusDict: dict[ConstType, int] = {Enemy: 0, Ally: 1, AlliedVictory: 2}


class TrgComparison(ConstType):
    __slots__ = ()

    def __str__(self):
        try:
            return {0: "AtLeast", 1: "AtMost", 10: "Exactly"}[self._value]
        except KeyError:
            return super().__str__()


AtLeast, AtMost, Exactly = TrgComparison(0), TrgComparison(1), TrgComparison(10)
ComparisonDict: dict[ConstType, int] = {AtLeast: 0, AtMost: 1, Exactly: 10}


class TrgCount(ConstType):
    __slots__ = ()

    def __str__(self):
        if isinstance(self._value, int) and self._value == 0:
            return "All"
        return super().__str__()


All = TrgCount(0)


class TrgModifier(ConstType):
    __slots__ = ()

    def __str__(self):
        try:
            return {7: "SetTo", 8: "Add", 9: "Subtract"}[self._value]
        except KeyError:
            return super().__str__()



SetTo, Add, Subtract = TrgModifier(7), TrgModifier(8), TrgModifier(9)
ModifierDict: dict[ConstType, int] = {SetTo: 7, Add: 8, Subtract: 9}


class TrgOrder(ConstType):
    __slots__ = ()

    def __str__(self):
        try:
            return {0: "Move", 1: "Patrol", 2: "Attack"}[self._value]
        except KeyError:
            return super().__str__()


Move, Patrol, Attack = TrgOrder(0), TrgOrder(1), TrgOrder(2)
OrderDict: dict[ConstType, int] = {Move: 0, Patrol: 1, Attack: 2}


class _Player(ConstType):
    __slots__ = ()

    def __str__(self):
        try:
            return {
                0: "Player1", 1: "Player2", 2: "Player3", 3: "Player4",
                4: "Player5", 5: "Player6", 6: "Player7", 7: "Player8",
                8: "Player9", 9: "Player10", 10: "Player11", 11: "Player12",
                13: "CurrentPlayer",
                14: "Foes", 15: "Allies", 16: "NeutralPlayers",
                17: "AllPlayers",
                18: "Force1", 19: "Force2", 20: "Force3", 21: "Force4",
                26: "NonAlliedVictoryPlayers",
            }[self._value]
        except KeyError:
            return super().__str__()


PlayerDict: dict[ConstType, int] = {}  # update in offsetmap.scdata


class TrgProperty(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeProperty(s)


class TrgPropState(ConstType):
    __slots__ = ()

    def __str__(self):
        try:
            return {4: "Enable", 5: "Disable", 6: "Toggle"}[self._value]
        except KeyError:
            return super().__str__()


class TrgSwitchAction(ConstType):
    __slots__ = ()

    def __str__(self):
        try:
            return {4: "Set", 5: "Clear", 6: "Toggle", 11: "Random"}[self._value]
        except KeyError:
            return super().__str__()


class TrgSwitchState(ConstType):
    __slots__ = ()

    def __str__(self):
        try:
            return {2: "Set", 3: "Cleared"}[self._value]
        except KeyError:
            return super().__str__()


class _Toggle(TrgPropState, TrgSwitchAction):
    __slots__ = ()
    def __init__(self):
        super().__init__(6)


class _Set(TrgSwitchState, TrgSwitchAction):
    __slots__ = ()
    def __init__(self):
        super().__init__(4)  # 2 or 4


Enable, Disable, Toggle = TrgPropState(4), TrgPropState(5), _Toggle()
Set, Clear, Random = _Set(), TrgSwitchAction(5), TrgSwitchAction(11)
Cleared = TrgSwitchState(3)
PropStateDict: dict[ConstType, int] = {Enable: 4, Disable: 5, Toggle: 6}
SwitchActionDict: dict[ConstType, int] = {Set: 4, Clear: 5, Toggle: 6, Random: 11}
SwitchStateDict: dict[ConstType, int] = {Set: 2, Cleared: 3}


class TrgResource(ConstType):
    __slots__ = ()

    def __str__(self):
        try:
            return {0: "Ore", 1: "Gas", 2: "OreAndGas"}[self._value]
        except KeyError:
            return super().__str__()


Ore, Gas, OreAndGas = TrgResource(0), TrgResource(1), TrgResource(2)
ResourceDict: dict[ConstType, int] = {Ore: 0, Gas: 1, OreAndGas: 2}


class TrgScore(ConstType):
    __slots__ = ()

    def __str__(self):
        try:
            return {
                0: "Total", 1: "Units", 2: "Buildings", 3: "UnitsAndBuildings",
                4: "Kills", 5: "Razings", 6: "KillsAndRazings", 7: "Custom",
            }[self._value]
        except KeyError:
            return super().__str__()


class _Kills(TrgScore):
    def __init__(self) -> None:
        super().__init__(4)
        self._internalf: Callable

    # TODO: player: Player, comparison: Comparison, number: Dword, unit: Unit
    # ) -> Condition
    def __call__(self, a, b, c, d):
        return self._internalf(a, b, c, d)


Total, Units, Buildings, UnitsAndBuildings = TrgScore(0), TrgScore(1), TrgScore(2), TrgScore(3)  # noqa: E501
# Name 'Kills' is used for both condition type and score type.
# To resolve conflict, we initialize Kills differently from others.
Kills, Razings, KillsAndRazings, Custom = _Kills(), TrgScore(5), TrgScore(6), TrgScore(7)  # noqa: E501
ScoreDict: dict[ConstType, int] = {
    Total: 0, Units: 1, Buildings: 2, UnitsAndBuildings: 3,
    Kills: 4, Razings: 5, KillsAndRazings: 6, Custom: 7,
}
# fmt: on


@overload
def _EncodeConst(t: type[ConstType], s: ConstType, u: str | None = None) -> int:
    ...


@overload
def _EncodeConst(t: type[ConstType], s: T, u: str | None = None) -> T:
    ...


@overload
def _EncodeConst(t: type[ConstType], s: _ExprProxy, u: str | None = None) -> _Dword:
    ...


def _EncodeConst(t: type[ConstType], s: _Arg, u: str | None = None) -> _Dword:  # noqa: N802
    while isinstance(s, ExprProxy) and not isinstance(s, ConstType):
        s = s._value
    if isinstance(s, ConstType):
        if isinstance(s, t):
            return unProxy(s)
        raise EPError(_('"{}" is not a {}').format(s, u if u else t.__name__))
    return s


@overload
def EncodeAllyStatus(s: ConstType) -> int:
    ...


@overload
def EncodeAllyStatus(s: U) -> U:
    ...


@overload
def EncodeAllyStatus(s: __ExprProxy) -> _Byte:
    ...


def EncodeAllyStatus(s: __Arg) -> _Byte:  # noqa: N802
    """Convert [Enemy, Ally, AlliedVictory] to number [0, 1, 2]."""
    try:
        return AllyStatusDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgAllyStatus, s)  # type: ignore[return-value]


@overload
def EncodeComparison(s: ConstType) -> int:
    ...


@overload
def EncodeComparison(s: U) -> U:
    ...


@overload
def EncodeComparison(s: __ExprProxy) -> _Byte:
    ...


def EncodeComparison(s: __Arg) -> _Byte:  # noqa: N802
    """Convert [AtLeast, AtMost, Exactly] to number [0, 1, 10]."""
    try:
        return ComparisonDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgComparison, s)  # type: ignore[return-value]


@overload
def EncodeModifier(s: ConstType) -> int:
    ...


@overload
def EncodeModifier(s: U) -> U:
    ...


@overload
def EncodeModifier(s: __ExprProxy) -> _Byte:
    ...


def EncodeModifier(s: __Arg) -> _Byte:  # noqa: N802
    """Convert [SetTo, Add, Subtract] to number [7, 8, 9]."""
    try:
        return ModifierDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgModifier, s)  # type: ignore[return-value]


@overload
def EncodeOrder(s: ConstType) -> int:
    ...


@overload
def EncodeOrder(s: U) -> U:
    ...


@overload
def EncodeOrder(s: __ExprProxy) -> _Byte:
    ...


def EncodeOrder(s: __Arg) -> _Byte:  # noqa: N802
    """Convert [Move, Patrol, Attack] to number [0, 1, 2]."""
    try:
        return OrderDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgOrder, s)  # type: ignore[return-value]


@overload
def EncodePlayer(s: ConstType) -> int:
    ...


@overload
def EncodePlayer(s: T) -> T:
    ...


@overload
def EncodePlayer(s: _ExprProxy) -> _Dword:
    ...


def EncodePlayer(s: _Arg) -> _Dword:  # noqa: N802
    """Convert player identifier to corresponding number.

    ======================= ========
        Identifier           Number
    ======================= ========
    P1                         0
    P2                         1
    P3                         2
    P4                         3
    P5                         4
    P6                         5
    P7                         6
    P8                         7
    P9                         8
    P10                        9
    P11                        10
    P12                        11
    Player1                    0
    Player2                    1
    Player3                    2
    Player4                    3
    Player5                    4
    Player6                    5
    Player7                    6
    Player8                    7
    Player9                    8
    Player10                   9
    Player11                   10
    Player12                   11
    CurrentPlayer              13
    Foes                       14
    Allies                     15
    NeutralPlayers             16
    AllPlayers                 17
    Force1                     18
    Force2                     19
    Force3                     20
    Force4                     21
    NonAlliedVictoryPlayers    26
    ======================= ========

    """
    if type(s) is ev.EUDVariable:
        return s

    try:
        return PlayerDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(_Player, s, "TrgPlayer")


@overload
def EncodePropState(s: ConstType) -> int:
    ...


@overload
def EncodePropState(s: U) -> U:
    ...


@overload
def EncodePropState(s: __ExprProxy) -> _Byte:
    ...


def EncodePropState(s: __Arg) -> _Byte:  # noqa: N802
    """Convert [Enable, Disable, Toogle] to number [4, 5, 6]"""
    try:
        return PropStateDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgPropState, s)  # type: ignore[return-value]


@overload
def EncodeResource(s: ConstType) -> int:
    ...


@overload
def EncodeResource(s: U) -> U:
    ...


@overload
def EncodeResource(s: __ExprProxy) -> _Byte:
    ...


def EncodeResource(s: __Arg) -> _Byte:  # noqa: N802
    """Convert [Ore, Gas, OreAndGas] to [0, 1, 2]"""
    try:
        return ResourceDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgResource, s)  # type: ignore[return-value]


@overload
def EncodeScore(s: ConstType) -> int:
    ...


@overload
def EncodeScore(s: U) -> U:
    ...


@overload
def EncodeScore(s: __ExprProxy) -> _Byte:
    ...


def EncodeScore(s: __Arg) -> _Byte:  # noqa: N802
    """Convert score type identifier to number.

    ================= ========
        _Score type     Number
    ================= ========
    Total                0
    Units                1
    Buildings            2
    UnitsAndBuildings    3
    Kills                4
    Razings              5
    KillsAndRazings      6
    Custom               7
    ================= ========

    """
    try:
        return ScoreDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgScore, s)  # type: ignore[return-value]


@overload
def EncodeSwitchAction(s: ConstType) -> int:
    ...


@overload
def EncodeSwitchAction(s: U) -> U:
    ...


@overload
def EncodeSwitchAction(s: __ExprProxy) -> _Byte:
    ...


def EncodeSwitchAction(s: __Arg) -> _Byte:  # noqa: N802
    """Convert [Set, Clear, Toogle, Random] to [4, 5, 6, 11]."""
    try:
        return SwitchActionDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgSwitchAction, s)  # type: ignore[return-value]


@overload
def EncodeSwitchState(s: ConstType) -> int:
    ...


@overload
def EncodeSwitchState(s: U) -> U:
    ...


@overload
def EncodeSwitchState(s: __ExprProxy) -> _Byte:
    ...


def EncodeSwitchState(s: __Arg) -> _Byte:  # noqa: N802
    """Convert [Set, Cleared] to [2, 3]."""
    try:
        return SwitchStateDict[s]  # type: ignore[index]
    except KeyError:
        return _EncodeConst(TrgSwitchState, s)  # type: ignore[return-value]


@overload
def EncodeCount(s: ConstType) -> int:
    ...


@overload
def EncodeCount(s: U) -> U:
    ...


@overload
def EncodeCount(s: __ExprProxy) -> _Byte:
    ...


def EncodeCount(s: __Arg) -> _Byte:  # noqa: N802
    """Convert [All, (other numbers)] to number [0, (as-is)]."""
    if s is All:
        return 0
    return _EncodeConst(TrgCount, s)  # type: ignore[return-value]


# ========================


def EncodeProperty(  # noqa: N802
    prop: UnitProperty | bytes | ExprProxy[UnitProperty | bytes],
) -> int:
    prop = unProxy(prop)
    return GetPropertyIndex(prop)
