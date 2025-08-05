from abc import ABC, abstractmethod
from os import linesep, path
from typing import Any, List, Tuple

from robot.api import SuiteVisitor
from robot.model import TestCase
from robot.utils import robottime


class BaseWriter(SuiteVisitor, ABC):
    default_format: Tuple[str] = (
        "full_name",
        "doc",
        "tags",
        "status",
        "message",
        "elapsedtime",
        "starttime",
        "endtime",
    )
    default_format_str: str = ",".join(default_format)
    long_format: Tuple[str] = (
        "id",
        "parent.name",
        "name",
        "parent.metadata",
        *default_format[1:],
        "timeout",
        "source",
        "lineno",
    )
    long_format_str: str = ",".join(long_format)
    default_docs_max_len: int = 100

    def __init__(self, output_filename: str, format_specifier: str = None, docs_max_len: Any = None) -> None:
        if not format_specifier:
            self.format_specifier = BaseWriter.default_format_str
        elif format_specifier == "LONG":  # Special case
            self.format_specifier = BaseWriter.long_format_str
        else:
            self.format_specifier = format_specifier

        self.docs_max_len = int(docs_max_len) if docs_max_len else BaseWriter.default_docs_max_len

        self.open_output_file(output_filename)
        self.write_header_pretty(self.format_specifier)

    def visit_test(self, test: TestCase) -> None:
        data: List[str] = list()

        for item in self.format_specifier.split(","):
            match item.lower():
                case "parent.metadata":
                    meta = str([list(test.parent.metadata.items())])
                    value = "" if meta == "[[]]" else meta[1:-2]
                case "parent.all_tests":
                    value = str([t.name for t in test.parent.all_tests])
                case i if "parent" in i:
                    value = getattr(test.parent, i.split(".")[1])
                case "doc":
                    value = test.doc[: self.docs_max_len]
                case "shortdoc":
                    doc = test.doc[: self.docs_max_len]
                    value = doc[: doc.find(linesep)]
                case "tags":
                    value = ", ".join(test.tags)
                case "elapsedtime":
                    value = robottime.secs_to_timestr(test.elapsedtime / 1000, compact=True)
                case i:
                    value = getattr(test, i)
            data.append(str(value))

        self.write_data(data)

    def write_header_pretty(self, format_specifier: str) -> None:
        data = [self.__pretty_name(entry) for entry in format_specifier.split(",")]
        self.write_header(data)

    def __pretty_name(self, specifier: str) -> str:
        # 1st case (special case): We have an exact replacement for this specifier set up
        special_exact_replace = {
            "lineno": "line",
            "name": "test name",
            "tags": "test tags",
            "setup": "test setup",
            "teardown": "test teardown",
            "body": "test body",
            "timeout": "timeout" # to prevent 2nd case
        }
        if specifier in special_exact_replace:
            return special_exact_replace[specifier].title()
        
        # 2nd case: We do dome generic replacements to make the specifier as pretty as possible
        always_replace = {
            "_": " ",
            ".": " ",
            "parent": "suite",
            "doc": "documentation",
            "time": " time",
        }
        default_pretty_name = specifier
        for word,sub in always_replace.items():
            default_pretty_name = default_pretty_name.replace(word, sub)
        return default_pretty_name.title()

    def print_success(self, filename: str):
        filepath = path.abspath(path.join(path.curdir, filename))
        print(f"Tabular: {filepath}")

    @abstractmethod
    def open_output_file(self, output_filename: str) -> None: ...

    @abstractmethod
    def write_data(self, data: List[str]) -> None: ...

    @abstractmethod
    def write_header(self, data: List[str]) -> None: ...
