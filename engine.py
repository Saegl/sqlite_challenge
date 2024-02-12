import abc
from dataclasses import dataclass
from typing import Any
import parser


class EngineError(Exception):
    pass

class Value(abc.ABC):
    val: Any

@dataclass
class NullValue(Value):
    val: None

@dataclass
class IntegerValue(Value):
    val: int

@dataclass
class RealValue(Value):
    val: float

@dataclass
class TextValue(Value):
    val: str

@dataclass
class BlobValue(Value):
    val: bytes


class Table:
    columns: list[str]
    data: list[list[Value]]
    
    def __init__(self, columns: list[str]):
        self.columns = columns
        self.data = []
    
    def insert_row(self, row: list[Value]):
        self.data.append(row)


class Engine:
    tables: dict[str, Table]

    def __init__(self):
        self.tables = {}

    def createstmt(self, stmt: parser.CreateStmt):
        table = Table([cd.column_name for cd in stmt.columndefs])
        self.tables[stmt.tablename] = table

    def insertstmt(self, stmt: parser.InsertStmt):
        table = self.tables[stmt.tablename]
        for row in stmt.values:
            row_values: list[Value] = []
            for expr in row.exprs:
                if isinstance(expr, parser.ConstInt):
                    row_values.append(IntegerValue(expr.val))
                elif isinstance(expr, parser.ConstString):
                    row_values.append(TextValue(expr.val))
                else:
                    raise EngineError("expr error")

            table.insert_row(row_values)

    def selectstmt(self, stmt: parser.SelectStmt):
        if stmt.tablename not in self.tables:
            print(f"OperationalError (SQLITE_ERROR): no such table: {stmt.tablename}")
            return

        table = self.tables[stmt.tablename]

        column_ids: list[int] = []
        for rcol in stmt.result_columns:
            if rcol == '*':
                column_ids.extend(range(len(table.columns)))
            else:
                column_ids.append(table.columns.index(rcol))
        
        output: list[Any] = []
        for row in self.tables[stmt.tablename].data:
            outputrow = tuple(row[c_id].val for c_id in column_ids)
            output.append(outputrow)
        return output

    def execute(self, cmd: str) -> list:
        cmd = cmd + ';'
        for stmt in parser.parse(cmd):
            stmtname = stmt.__class__.__name__.lower()
            method = getattr(self, stmtname)
            output = method(stmt)
            if output is None:
                return []
            else:
                return output
        return []

    def eval(self, line):
        for stmt in parser.parse(line):
            stmtname = stmt.__class__.__name__.lower()
            method = getattr(self, stmtname)
            method(stmt)


def main():
    engine = Engine()

    while True:
        try:
            line = input("sqlite> ")
        except EOFError:
            break
        except KeyboardInterrupt:
            break

        engine.eval(line)

if __name__ == "__main__":
    main()

