from json import load as _load
from os import listdir as _listdir
from os import makedirs as _makedirs
from os.path import exists as _exists
from os.path import join as _join
from typing import Any as _Any
from typing import Optional as _Optional
from typing import TextIO as _TextIO
from typing import Type as _Type
from typing import TypeVar as _TypeVar

from pandas import read_html as _read_html
from pandas import read_parquet as _read_parquet

from ..environment import reader_folder_path as _reader_folder_path
from ..logger import get_logger as _get_logger

T = _TypeVar("T", bound="FileReader")

LOGGER = _get_logger()


class RootedReader:
    def __init__(self: "RootedReader", root_folder: _Optional[str] = None) -> None:
        self._root_folder = root_folder if root_folder else _reader_folder_path()

    def static_files(self: "RootedReader", path: str, create: bool = False) -> _Any:
        reader_path = self._root_folder
        if create:
            _makedirs(reader_path, exist_ok=True)
        return FileReader(folder=reader_path, version=path)

    def versioned_files(self: "RootedReader", path: str, create: bool = False) -> _Any:
        reader_path = _join(self._root_folder, path)
        if create:
            _makedirs(_join(reader_path, "_/_"), exist_ok=True)
        return FileReader(folder=_join(self._root_folder, path))


class FileReader:
    def __init__(self: "FileReader", folder: str, version: _Optional[str] = None) -> None:
        self._root_folder = folder

        if version is None:
            self._folder = _last_folder(_last_folder(folder))
            self._version = self._folder[len(folder) :]
        else:
            self._folder = _join(folder, version)
            self._version = version

    def open(
        self: "FileReader",
        filename: _Optional[str] = None,
        *args: _Any,
        **kwargs: _Any,
    ) -> _TextIO:
        ret: _TextIO = open(self.get(filename), *args, **kwargs)
        return ret

    def get(self: "FileReader", filename: _Optional[str] = None) -> str:
        if filename is None:
            return _join(self._folder, _listdir(self._folder)[0])
        return _join(self._folder, filename)

    def exists(self: "FileReader", filename: str) -> bool:
        try:
            resolved_path = self.get(filename)
        except FileNotFoundError:
            return False
        return _exists(resolved_path)

    @classmethod
    def from_environment(cls: _Type[T], subfolder: str) -> T:
        return cls(_join(_reader_folder_path(), subfolder))

    def load(self: "FileReader", filename: _Optional[str] = None, *args, **kwargs) -> _Any:
        new_file_name = self.get(filename)
        if filename:
            LOGGER.debug(
                "Latest file for folder '%s' (with filename='%s') resolved to '%s'.",
                self._root_folder,
                filename,
                new_file_name,
            )
        else:
            LOGGER.debug(
                "Latest file for folder '%s' resolved to '%s'.",
                self._root_folder,
                new_file_name,
            )
        if new_file_name.endswith(".json"):
            with open(new_file_name) as input_file:
                return _load(input_file, *args, **kwargs)
        if new_file_name.endswith(".parquet"):
            return _read_parquet(new_file_name, *args, **kwargs)
        if new_file_name.endswith(".html"):
            try:
                return _read_html(new_file_name, *args, **kwargs)
            except ValueError as ve:
                raise ValueError(f"Error parsing HTML from '{new_file_name}'") from ve
        raise NotImplementedError(f"Do not know how to load the file `{filename}`: `{new_file_name}`")


def _last_folder(folder: str) -> str:
    try:
        return _join(folder, sorted(_listdir(folder), reverse=True)[0])
    except IndexError:
        raise FileNotFoundError(f"Folder '{folder}' is empty.")


def fload(folder: str, filename: _Optional[str] = None) -> _Any:
    if not filename:
        LOGGER.debug("Loading the file '%s'", folder)
    else:
        LOGGER.debug("Loading the file '%s/%s'", folder, filename)
    return FileReader.from_environment(folder).load(filename)
