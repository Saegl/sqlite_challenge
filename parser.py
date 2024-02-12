import abc
import dataclasses
from tokenizer import Token, TokenType, TT, tokenize


class Stmt(abc.ABC):
    pass

class Expr(abc.ABC):
    pass

@dataclasses.dataclass
class ConstString(Expr):
    val: str

@dataclasses.dataclass
class ConstInt(Expr):
    val: int

@dataclasses.dataclass
class BindParameter(Expr):
    ident: str

@dataclasses.dataclass
class UnaryOperator(Expr):
    expr: Expr
    op: TT

@dataclasses.dataclass
class BinaryOperator(Expr):
    lhs: Expr
    op: TT
    rhs: Expr

@dataclasses.dataclass
class Between(Expr):
    expr: Expr
    lower: Expr
    upper: Expr
    isnot: bool

@dataclasses.dataclass
class ColumnDef:
    column_name: str
    type_name: str

@dataclasses.dataclass
class Row:
    exprs: list[Expr]

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
    where: Expr | None


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, source: str):
        self.i = 0
        self.tokens = tokenize(source)

    def cur(self) -> Token:
        return self.tokens[self.i]

    def skip(self):
        "Skip one token"
        self.i += 1

    def expect(self, ttype: TokenType):
        if self.cur().ttype == ttype:
            self.skip()
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

    def literal_value(self) -> Expr:
        tok = self.cur()
        if tok.ttype == TokenType.STRING_LITERAL:
            self.skip()
            return ConstString(tok.val)
        elif tok.ttype == TokenType.INT_LITERAL:
            self.skip()
            return ConstInt(int(tok.val))
        else:
            raise ParserError(f"Wrong literal, got {tok.ttype}")

    def bind_parameter(self) -> BindParameter:
        tok = self.cur()
        if tok.ttype == TT.IDENTIFIER:
            self.skip()
            return BindParameter(tok.val)
        else:
            raise ParserError

    def value(self) -> Expr:
        if self.cur().ttype in (TT.STRING_LITERAL, TT.INT_LITERAL):
            return self.literal_value()
        elif self.cur().ttype == TT.IDENTIFIER:
            return self.bind_parameter()
        else:
            raise ParserError(str(self.cur().ttype))

    def order_expr(self) -> Expr:
        lhs = self.value()
        if self.cur().ttype in (TT.LT, TT.LE, TT.GT, TT.GE):
            op = self.cur().ttype
            self.skip()
            rhs = self.value()
            return BinaryOperator(lhs, op, rhs)
        
        return lhs

    def cmp_expr(self) -> Expr:
        lhs = self.order_expr()
        if self.cur().ttype in (TT.EQUAL, TT.NOT_EQUAL):
            op = self.cur().ttype
            self.skip()
            rhs = self.order_expr()
            return BinaryOperator(lhs, op, rhs)
        if self.cur().ttype in (TT.NOT, TT.BETWEEN):
            isnot = False
            if self.cur().ttype == TT.NOT:
                isnot = True
                self.skip()
            
            self.expect(TT.BETWEEN)
            lower = self.order_expr()
            self.expect(TT.AND)
            upper = self.order_expr()
            return Between(lhs, lower, upper, isnot)
        
        return lhs

    def not_expr(self) -> Expr:
        if self.cur().ttype == TT.NOT:
            self.skip()
            return UnaryOperator(self.cmp_expr(), TT.NOT)

        return self.cmp_expr()

    def and_expr(self) -> Expr:
        lhs = self.not_expr()
        while self.cur().ttype == TT.AND:
            self.skip()
            rhs = self.not_expr()
            lhs = BinaryOperator(lhs, TT.AND, rhs)

        return lhs

    def or_expr(self) -> Expr:
        lhs = self.and_expr()
        while self.cur().ttype == TT.OR:
            self.skip()
            rhs = self.and_expr()
            lhs = BinaryOperator(lhs, TT.OR, rhs)

        return lhs

    def expr(self) -> Expr:
        return self.or_expr()

    def row(self) -> Row:
        self.expect(TokenType.LCOLON)

        exprs = []
        expr = self.expr()
        exprs.append(expr)

        while self.cur().ttype != TokenType.RCOLON:
            self.expect(TokenType.COMMA)
            expr = self.expr()
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
            self.expect(TokenType.WHERE)
            where = self.expr()

        return SelectStmt(tablename, cols, where)

    def sql_stmt(self) -> Stmt:
        stmt: Stmt
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
                Row([ConstString("alisher"), ConstString("zhubanyshev")]),
                Row([ConstString("john"), ConstString("doe")]),
            ]
        )
    ]
    assert stmts == expected_stmts

def test_select():
    line = 'SELECT * FROM user;'
    stmts = parse(line)
    expected_stmts = [
        SelectStmt("user", ["*"], None)
    ]
    assert stmts == expected_stmts

def test_select_cols():
    line = 'SELECT title, director FROM movies;'
    stmts = parse(line)
    expected_stmts = [
        SelectStmt("movies", ["title", "director"], None)
    ]
    assert stmts == expected_stmts

