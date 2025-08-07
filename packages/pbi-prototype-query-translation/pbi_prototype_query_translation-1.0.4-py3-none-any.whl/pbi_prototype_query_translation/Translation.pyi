class CSharpDict:
    Keys: list[str]
    Values: list[str]

class DataViewQueryTranslationResult:
    DaxExpression: str
    SelectNameToDaxColumnName: CSharpDict

class PrototypeQuery:
    @staticmethod
    def Translate(
        query: str, dbName: str, port: int, workingDirectory: str | None = None
    ) -> DataViewQueryTranslationResult: ...
