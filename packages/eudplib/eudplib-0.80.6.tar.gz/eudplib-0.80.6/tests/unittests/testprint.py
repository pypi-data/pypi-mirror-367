from helper import *


@TestInstance
def test_variable_hptr():
    a = EUDVariable(5)
    b = a * a * a * a * a

    # variable test
    x = Db(1024)
    y = Db(1024)
    f_dbstr_print(x, "    \x04test ", a, " b: ", hptr(b), " test", 1, hptr(21))
    f_dbstr_print(y, "    \x04test 5 b: 00000C35 test100000015")
    test_equality("variable/hptr printing test", f_strcmp(x, y), 0)


@TestInstance
def test_strprint():
    x = Db(1024)
    y = Db("Test instance")
    f_dbstr_print(x, ptr2s(y))
    f_printAll("{:s}", x)
    f_printAll("{:s}", y)
    test_equality("string printing test", f_strcmp(x, y), 0)
