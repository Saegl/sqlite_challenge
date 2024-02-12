import sqlite3

from engine import Engine


class SqliteWrapper:
    """
    I am not interested in implementing Transaction control
    (manual commit after each insert)
    So this wrapper commits on each executes, useful for testing,
    but this is not proper use of `sqlite3`
    """
    def __init__(self):
        self.con = sqlite3.connect(":memory:")
        self.cur = self.con.cursor()

    def execute(self, text: str):
        res = self.cur.execute(text)
        self.con.commit()
        return res.fetchall()


class SameOutput:
    def __init__(self):
        self.sw = SqliteWrapper()
        self.e = Engine()

    def same(self, cmd: str):
        assert self.sw.execute(cmd) == self.e.execute(cmd)


def test1():
    sm = SameOutput()
    sm.same("CREATE TABLE user(firstname TEXT, secondname TEXT)")
    sm.same("INSERT INTO user VALUES ('alisher', 'zhuban'), ('john', 'doe')")
    sm.same("SELECT * FROM user")
    sm.same("SELECT firstname, secondname FROM user")
    sm.same("SELECT *, firstname, * FROM user")


def test2():
    sm = SameOutput()
    sm.same("CREATE TABLE user(name TEXT, age INTEGER)")
    sm.same("INSERT INTO user VALUES ('alisher', 22), ('john', 21)")
    sm.same("SELECT name FROM user WHERE age = 22")
    sm.same("SELECT name FROM user WHERE age BETWEEN 18 AND 21")
    sm.same("SELECT name FROM user WHERE age NOT BETWEEN 18 AND 21")

def test_nums():
    sm = SameOutput()
    sm.same("CREATE TABLE nums(x INTEGER)")
    sm.same("INSERT INTO nums VALUES (1), (2), (3), (4), (5)")
    sm.same("SELECT x FROM nums WHERE x == 1 OR x == 2")
    sm.same("SELECT x FROM nums WHERE NOT x == 3 AND NOT x == 2")
    sm.same("SELECT x FROM nums WHERE x != 1 AND x <> 2")

