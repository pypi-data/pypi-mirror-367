import sys
from pathlib import Path
from typing import TYPE_CHECKING

import clr  # type: ignore[import-untyped]

SOURCE_FOLDER = (Path(__file__).parent / "libs").absolute().as_posix()
sys.path.insert(0, SOURCE_FOLDER)
clr.AddReference("Translation")  # type: ignore
# When type checking, we import from the stub file. When running, we import from the actual C# module.
if TYPE_CHECKING:
    from .Translation import (  # type: ignore[import-untyped]
        DataViewQueryTranslationResult,
        PrototypeQuery,
    )
else:
    from Translation import DataViewQueryTranslationResult, PrototypeQuery


def prototype_query(
    query: str, db_name: str, port: int
) -> "DataViewQueryTranslationResult":
    return PrototypeQuery.Translate(query, db_name, port, SOURCE_FOLDER)
