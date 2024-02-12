import abc
import re
from dataclasses import dataclass
from typing import Any
import parser
from tokenizer import TT


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

    def expr(self, node: parser.Expr, context: dict[str, Value]) -> Value:
        match node:
            case parser.ConstString(val):
                return TextValue(val)
            case parser.ConstInt(val):
                return IntegerValue(val)
            case parser.BindParameter(val):
                return context[node.ident]
            case parser.InExpr(element, container, isnot):
                elementval = self.expr(element, context).val
                containerval = [self.expr(e, context).val for e in container]
                if isnot:
                    return IntegerValue(elementval not in containerval)
                else:
                    return IntegerValue(elementval in containerval)
            case parser.LikeExpr(element, pattern, isnot):
                elementval = self.expr(element, context).val
                patternval = self.expr(pattern, context).val
                modified_pattern = patternval.replace('%', '.*').replace('_', '.')
                regex_pattern = re.compile(modified_pattern, re.IGNORECASE)
                return IntegerValue(regex_pattern.fullmatch(elementval) is not None)
            case parser.UnaryOperator(expr, op):
                expr = self.expr(expr, context)
                if op == TT.NOT:
                    return IntegerValue(not expr.val)
                else:
                    raise EngineError(f"Unary op {op} is not implemented")
            case parser.BinaryOperator(lhs, op, rhs):
                lhsval = self.expr(lhs, context).val
                rhsval = self.expr(rhs, context).val

                if op == TT.EQUAL:
                    return IntegerValue(lhsval == rhsval)
                elif op == TT.NOT_EQUAL:
                    return IntegerValue(lhsval != rhsval)
                elif op == TT.LT:
                    return IntegerValue(lhsval < rhsval)
                elif op == TT.LE:
                    return IntegerValue(lhsval <= rhsval)
                elif op == TT.GT:
                    return IntegerValue(lhsval > rhsval)
                elif op == TT.GE:
                    return IntegerValue(lhsval >= rhsval)
                elif op == TT.OR:
                    return IntegerValue(lhsval == 1 or rhsval == 1)
                elif op == TT.AND:
                    return IntegerValue(lhsval == 1 and rhsval == 1)
                else:
                    raise EngineError(f"{op} operator is not implemented")

            case parser.Between(expr, lower, upper, isnot):
                exprval = self.expr(expr, context).val
                lowerval = self.expr(lower, context).val
                upperval = self.expr(upper, context).val
                output = lowerval <= exprval <= upperval
                if isnot:
                    output = not output
                return IntegerValue(output)
            case _:
                raise EngineError(f"Not implemented expr {node}")

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
        for row in table.data:
            context = {}
            for k, v in zip(table.columns, row):
                context[k] = v

            if stmt.where:
                incl = self.expr(stmt.where, context).val == 1
                if incl:
                    outputrow = tuple(row[c_id].val for c_id in column_ids)
                    output.append(outputrow)
            else:
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

