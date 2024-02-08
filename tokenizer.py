import enum
import dataclasses


class TokenType(enum.Enum):
    CREATE = enum.auto()
    TABLE = enum.auto()
    IDENTIFIER = enum.auto()
    LCOLON = enum.auto()
    RCOLON = enum.auto()
    TEXT = enum.auto()
    INSERT = enum.auto()
    INTO = enum.auto()
    VALUES = enum.auto()
    STRING_LITERAL = enum.auto()
    SELECT = enum.auto()
    FROM = enum.auto()

    STAR = enum.auto()
    COMMA = enum.auto()
    SEMICOLON = enum.auto()

keywords = {
    "CREATE": TokenType.CREATE,
    "TABLE": TokenType.TABLE,
    "TEXT": TokenType.TEXT,
    "INSERT": TokenType.INSERT,
    "INTO": TokenType.INTO,
    "SELECT": TokenType.SELECT,
    "FROM": TokenType.FROM,
}

@dataclasses.dataclass
class Token:
    ttype: TokenType
    val: str


class TokenizerError(Exception):
    pass


def tokenize(source: str) -> list[str]:
    i = 0
    ans = []
    while i < len(source):
        c = source[i]
        if c in (' ', '\n', '\t', '\r'):
            i += 1
            continue
        elif c.isalpha():
            l = i
            while i < len(source) and source[i].isalpha():
                i += 1
            sseq = source[l:i]
            if sseq in keywords:
                ans.append(Token(keywords[sseq], ""))
            else:
                ans.append(Token(TokenType.IDENTIFIER, sseq))
        elif c == '"':
            i += 1
            l = i
            while i < len(source) and source[i] != '"':
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
        else:
            raise TokenizerError(f"unexpected symbol {c} at {i}")

    return ans


def test_create():
    line = "CREATE TABLE user (name TEXT);"
    tokens = tokenize(line)
    expected_tokens = [
        Token(TokenType.CREATE, ""),
        Token(TokenType.TABLE, ""),
        Token(TokenType.IDENTIFIER, "user"),
        Token(TokenType.LCOLON, ""),
        Token(TokenType.IDENTIFIER, "name"),
        Token(TokenType.TEXT, ""),
        Token(TokenType.RCOLON, ""),
        Token(TokenType.SEMICOLON, ""),
    ]
    
    assert tokens == expected_tokens


def test_insert():
    line = 'INSERT INTO user ("alisher");'
    tokens = tokenize(line)
    expected_tokens = [
        Token(TokenType.INSERT, ""),
        Token(TokenType.INTO, ""),
        Token(TokenType.IDENTIFIER, "user"),
        Token(TokenType.LCOLON, ""),
        Token(TokenType.STRING_LITERAL, "alisher"),
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
