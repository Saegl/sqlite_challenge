import enum
import dataclasses


class TokenType(enum.Enum):
    # keywords
    CREATE = enum.auto()
    TABLE = enum.auto()
    INSERT = enum.auto()
    INTO = enum.auto()
    VALUES = enum.auto()
    SELECT = enum.auto()
    FROM = enum.auto()
    WHERE = enum.auto()
    BETWEEN = enum.auto()
    LIKE = enum.auto()
    OR = enum.auto()
    AND = enum.auto()
    NOT = enum.auto()
    IN = enum.auto()
    DISTINCT = enum.auto()
    ALL = enum.auto()
    ORDER = enum.auto()
    BY = enum.auto()
    ASC = enum.auto()
    DESC = enum.auto()
    LIMIT = enum.auto()
    OFFSET = enum.auto()
    
    IDENTIFIER = enum.auto()
    STRING_LITERAL = enum.auto()
    INT_LITERAL = enum.auto()
    
    LCOLON = enum.auto()
    RCOLON = enum.auto() 
    STAR = enum.auto()
    COMMA = enum.auto()
    SEMICOLON = enum.auto()

    # cmp
    EQUAL = enum.auto()
    NOT_EQUAL = enum.auto()

    # order op
    LT = enum.auto()
    LE = enum.auto()
    GT = enum.auto()
    GE = enum.auto()

TT = TokenType


keywords = {
    "CREATE": TokenType.CREATE,
    "TABLE": TokenType.TABLE,
    "INSERT": TokenType.INSERT,
    "INTO": TokenType.INTO,
    "VALUES": TokenType.VALUES,
    "SELECT": TokenType.SELECT,
    "FROM": TokenType.FROM,
    "WHERE": TokenType.WHERE,
    "BETWEEN": TT.BETWEEN,
    "LIKE": TT.LIKE,
    "OR": TT.OR,
    "AND": TT.AND,
    "NOT": TT.NOT,
    "IN": TT.IN,
    "DISTINCT": TT.DISTINCT,
    "ALL": TT.ALL,
    "ORDER": TT.ORDER,
    "BY": TT.BY,
    "ASC": TT.ASC,
    "DESC": TT.DESC,
    "LIMIT": TT.LIMIT,
    "OFFSET": TT.OFFSET,
}

@dataclasses.dataclass
class Token:
    ttype: TokenType
    val: str


class TokenizerError(Exception):
    pass


def tokenize(source: str) -> list[Token]:
    i = 0
    ans = []
    while i < len(source):
        c = source[i]
        if c in (' ', '\n', '\t', '\r'):
            i += 1
            continue
        elif c.isalpha() or c == '_':
            l = i
            while i < len(source) and (source[i].isalpha() or source[i] == '_'):
                i += 1
            sseq = source[l:i]
            if sseq.upper() in keywords:
                ans.append(Token(keywords[sseq.upper()], ""))
            else:
                ans.append(Token(TokenType.IDENTIFIER, sseq))
        elif c.isdigit():
            l = i
            while i < len(source) and source[i].isdigit():
                i += 1
            sseq = source[l:i]
            ans.append(Token(TokenType.INT_LITERAL, sseq))
        elif c == "'":
            i += 1
            l = i
            while i < len(source) and source[i] != "'":
                i += 1
            inner = source[l:i]
            i += 1
            ans.append(Token(TokenType.STRING_LITERAL, inner))
        elif c == '*':
            ans.append(Token(TokenType.STAR, ""))
            i += 1
        elif c == '(':
            ans.append(Token(TokenType.LCOLON, ""))
            i += 1
        elif c == ')':
            ans.append(Token(TokenType.RCOLON, ""))
            i += 1
        elif c == ';':
            ans.append(Token(TokenType.SEMICOLON, ""))
            i += 1
        elif c == ',':
            ans.append(Token(TokenType.COMMA, ""))
            i += 1
        elif c == '=':
            ans.append(Token(TokenType.EQUAL, ""))
            i += 1
            if source[i] == '=':
                i += 1
        elif c == '<':
            i += 1
            if source[i] == '>':
                i += 1
                ans.append(Token(TT.NOT_EQUAL, ""))
                continue
            elif source[i] == '=':
                i += 1
                ans.append(Token(TT.LE, ""))
                continue
            
            ans.append(Token(TT.LT, ""))
        elif c == '>':
            i += 1
            if source[i] == '=':
                i += 1
                ans.append(Token(TT.GE, ""))
                continue

            ans.append(Token(TT.GT, ""))
        elif c == '!':
            i += 1
            if source[i] == '=':
                i += 1
                ans.append(Token(TT.NOT_EQUAL, ""))
                continue

            raise TokenizerError
        else:
            raise TokenizerError(f"unexpected symbol {c} at {i}")

    return ans


def test_create():
    line = "CREATE TABLE user (firstname TEXT, secondname TEXT);"
    tokens = tokenize(line)
    expected_tokens = [
        Token(TokenType.CREATE, ""),
        Token(TokenType.TABLE, ""),
        Token(TokenType.IDENTIFIER, "user"),
        Token(TokenType.LCOLON, ""),
        Token(TokenType.IDENTIFIER, "firstname"),
        Token(TokenType.IDENTIFIER, "TEXT"),
        Token(TokenType.COMMA, ""),
        Token(TokenType.IDENTIFIER, "secondname"),
        Token(TokenType.IDENTIFIER, "TEXT"),
        Token(TokenType.RCOLON, ""),
        Token(TokenType.SEMICOLON, ""),
    ]
    
    assert tokens == expected_tokens


def test_insert():
    line = 'INSERT INTO user VALUES ("alisher", "zhubanyshev"), ("john", "doe");'
    tokens = tokenize(line)
    expected_tokens = [
        Token(TokenType.INSERT, ""),
        Token(TokenType.INTO, ""),
        Token(TokenType.IDENTIFIER, "user"),
        Token(TokenType.VALUES, ""),
        Token(TokenType.LCOLON, ""),
        Token(TokenType.STRING_LITERAL, "alisher"),
        Token(TokenType.COMMA, ""),
        Token(TokenType.STRING_LITERAL, "zhubanyshev"),
        Token(TokenType.RCOLON, ""),
        Token(TokenType.COMMA, ""),
        Token(TokenType.LCOLON, ""),
        Token(TokenType.STRING_LITERAL, "john"),
        Token(TokenType.COMMA, ""),
        Token(TokenType.STRING_LITERAL, "doe"),
        Token(TokenType.RCOLON, ""),
        Token(TokenType.SEMICOLON, ""),
    ]
    assert tokens == expected_tokens


def test_select():
    line = 'SELECT * FROM user;'
    tokens = tokenize(line)
    expected_tokens = [
        Token(TokenType.SELECT, ""),
        Token(TokenType.STAR, ""),
        Token(TokenType.FROM, ""),
        Token(TokenType.IDENTIFIER, "user"),
        Token(TokenType.SEMICOLON, ""),
    ]
    assert tokens == expected_tokens

def test_int():
    line = 'SELECT 1;'
    tokens = tokenize(line)
    expected_tokens = [
        Token(TokenType.SELECT, ""),
        Token(TokenType.INT_LITERAL, "1"),
        Token(TokenType.SEMICOLON, ""),
    ]
    assert tokens == expected_tokens

