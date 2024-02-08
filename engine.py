import parser


class Engine:
    def __init__(self):
        self.tabledata = {}
        self.tablecols = {}

    def createstmt(self, stmt: parser.CreateStmt):
        self.tabledata[stmt.tablename] = []
        self.tablecols[stmt.tablename] = []
        for coldef in stmt.columndefs:
            self.tablecols[stmt.tablename].append((coldef.column_name, coldef.column_name))

    def insertstmt(self, stmt: parser.InsertStmt):
        for row in stmt.values:
            self.tabledata[stmt.tablename].append(row.exprs)

    def selectstmt(self, stmt: parser.SelectStmt):
        if stmt.tablename not in self.tabledata:
            print(f"OperationalError (SQLITE_ERROR): no such table: {stmt.tablename}")
            return

        for row in self.tabledata[stmt.tablename]:
            print(row)

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

