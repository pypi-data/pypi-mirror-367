import json
import zipfile
from pathlib import Path
from typing import Type, Dict, Any, Generator, Union, List

from progress.bar import Bar
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from pyimporters_plugins.base import (
    KnowledgeParserOptions,
    KnowledgeParserBase,
    Term,
    maybe_archive,
)


@dataclass
class JSONOptions(KnowledgeParserOptions):
    """
    Options for the JSON knowledge import
    """

    pass


JSONOptionsModel = JSONOptions.__pydantic_model__


class JSONKnowledgeParser(KnowledgeParserBase):
    def parse(
        self, source: Path, options: Union[BaseModel, Dict[str, Any]], bar: Bar
    ) -> Generator[Term, None, None]:
        options = JSONOptionsModel(**options) if isinstance(options, dict) else options
        with maybe_archive(source, mode="rb") as fin:
            if isinstance(fin, zipfile.ZipFile):
                for zentry in fin.filelist:
                    with fin.open(zentry) as zfin:
                        yield from self._parse_json(bar, zfin)
            else:
                yield from self._parse_json(bar, fin)

    def _parse_json(self, bar, fin):
        terms = json.load(fin)
        bar.max = len(terms)
        bar.start()
        for term in terms:
            bar.next()
            yield Term(**term)

    @classmethod
    def get_schema(cls) -> KnowledgeParserOptions:
        return JSONOptions

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return JSONOptionsModel

    @classmethod
    def get_extensions(cls) -> List[str]:
        return ["json", "zip"]
