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

