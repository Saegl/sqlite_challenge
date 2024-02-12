import abc
import dataclasses
from tokenizer import Token, TokenType, tokenize


class Stmt(abc.ABC):
    pass


@dataclasses.dataclass
class ColumnDef:
    column_name: str
    type_name: str

@dataclasses.dataclass
class Row:
    exprs: list[str]

@dataclasses.dataclass
class CreateStmt(Stmt):
    tablename: str
    columndefs: list[ColumnDef]


@dataclasses.dataclass
class InsertStmt(Stmt):
    tablename: str
    values: list[Row]


@dataclasses.dataclass
class SelectStmt(Stmt):
    tablename: str | None
    result_columns: list[str]


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, source: str):
        self.i = 0
        self.tokens = tokenize(source)

    def cur(self) -> Token:
        return self.tokens[self.i]

    def expect(self, ttype: TokenType):
        if self.cur().ttype == ttype:
            self.i += 1
        else:
            raise ParserError(f"Expected {ttype} got {self.cur().ttype} at {self.i}")

    def expect_ident(self) -> str:
        tok = self.cur()
        self.expect(TokenType.IDENTIFIER)
        return tok.val

    def expect_string(self) -> str:
        tok = self.cur()
        self.expect(TokenType.STRING_LITERAL)
        return tok.val

    def row(self) -> Row:
        self.expect(TokenType.LCOLON)

        exprs = []
        expr = self.expect_string()
        exprs.append(expr)

        while self.cur().ttype != TokenType.RCOLON:
            self.expect(TokenType.COMMA)
            expr = self.expect_string()
            exprs.append(expr)

        self.expect(TokenType.RCOLON)
        return Row(exprs)


    def create_table_stmt(self) -> CreateStmt:
        self.expect(TokenType.CREATE)
        self.expect(TokenType.TABLE)
        tablename = self.expect_ident()
        columndefs = []
        self.expect(TokenType.LCOLON)

        column_name = self.expect_ident()
        type_name = self.expect_ident()
        columndefs.append(ColumnDef(column_name, type_name))

        while self.cur().ttype == TokenType.COMMA:
            self.expect(TokenType.COMMA)
            column_name = self.expect_ident()
            type_name = self.expect_ident()
            columndefs.append(ColumnDef(column_name, type_name))
        self.expect(TokenType.RCOLON)

        return CreateStmt(tablename, columndefs)

    def insert_stmt(self) -> InsertStmt:
        self.expect(TokenType.INSERT)
        self.expect(TokenType.INTO)
        tablename = self.expect_ident()

        self.expect(TokenType.VALUES)
        values = []

        row = self.row()
        values.append(row)

        while self.cur().ttype == TokenType.COMMA:
            self.expect(TokenType.COMMA)
            row = self.row()
            values.append(row) 

        return InsertStmt(tablename, values)

    def result_column(self) -> str:
        if self.cur().ttype == TokenType.STAR:
            self.expect(TokenType.STAR)
            return "*"
        else:
            column_name = self.expect_ident()
            return column_name

    def select_stmt(self) -> SelectStmt:
        self.expect(TokenType.SELECT)
        cols = []
        col = self.result_column()
        cols.append(col)
        while self.cur().ttype == TokenType.COMMA:
            self.expect(TokenType.COMMA)
            col = self.result_column()
            cols.append(col)
        
        tablename = None
        if self.cur().ttype == TokenType.FROM:
            self.expect(TokenType.FROM)
            tablename = self.expect_ident()

        where = None
        if self.cur().ttype == TokenType.WHERE:
            pass

        return SelectStmt(tablename, cols)

    def sql_stmt(self) -> Stmt:
        if self.cur().ttype == TokenType.CREATE:
            stmt = self.create_table_stmt()
        elif self.cur().ttype == TokenType.INSERT:
            stmt = self.insert_stmt()
        elif self.cur().ttype == TokenType.SELECT:
            stmt = self.select_stmt()
        else:
            raise ParserError(f"Unexpected token type {self.cur().ttype}")

        self.expect(TokenType.SEMICOLON)
        return stmt

    def parse(self) -> list[Stmt]:
        ans = []
        while self.i < len(self.tokens):
            tok = self.tokens[self.i]
            if tok.ttype == TokenType.SEMICOLON:
                self.i += 1
            else:
                ans.append(self.sql_stmt())
        return ans


def parse(source: str) -> list[Stmt]:
    return Parser(source).parse()


def test_create():
    line = "CREATE TABLE user (firstname TEXT, secondname TEXT);"
    stmts = parse(line)
    expected_stmts = [
        CreateStmt(
            "user",
            [
                ColumnDef("firstname", "TEXT"),
                ColumnDef("secondname", "TEXT"),
            ]
        )
    ]
    assert stmts == expected_stmts

def test_insert():
    line = 'INSERT INTO user VALUES ("alisher", "zhubanyshev"), ("john", "doe");'
    stmts = parse(line)
    expected_stmts = [
        InsertStmt(
            "user",
            [
                Row(["alisher", "zhubanyshev"]),
                Row(["john", "doe"]),
            ]
        )
    ]
    assert stmts == expected_stmts

def test_select():
    line = 'SELECT * FROM user;'
    stmts = parse(line)
    expected_stmts = [
        SelectStmt("user", ["*"])
    ]
    assert stmts == expected_stmts

def test_select_cols():
    line = 'SELECT title, director FROM movies;'
    stmts = parse(line)
    expected_stmts = [
        SelectStmt("movies", ["title", "director"])
    ]
    assert stmts == expected_stmts

