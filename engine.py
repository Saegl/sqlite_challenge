import parser


class Table:
    columns: list[str]
    data: list[list[str]]
    
    def __init__(self, columns: list[str]):
        self.columns = columns
        self.data = []
    
    def insert_row(self, row: list[str]):
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
            table.insert_row(row.exprs)

    def selectstmt(self, stmt: parser.SelectStmt):
        if stmt.tablename not in self.tables:
            print(f"OperationalError (SQLITE_ERROR): no such table: {stmt.tablename}")
            return
        
        output = []
        for row in self.tables[stmt.tablename].data:
            output.append(tuple(row))
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

