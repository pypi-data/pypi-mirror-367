from contextlib import suppress
from logging import getLogger
from math import log2
from re import findall

from kain.descriptors import pin, proxy_to
from kain.importer import optional
from kain.internals import Who, to_ascii, unique

logger = getLogger(__name__)


def generate_binary_offsets(x: int):
    power = int(log2(x))

    yield 0
    for base in range(power):
        bias = (2 ** (power - base))
        for no in range(x // bias + 1):
            if no % 2:
                yield no * bias


def iter_by_binary_offsets(x: bytes | str, /, ordinate: bool):
    getter = x.__getitem__
    offset = len(x) - len(x) % 2 - 1

    if offset != -1:
        iterator = generate_binary_offsets(offset)

        offsets = map(getter, iterator)
        if ordinate:
            offsets = map(ord, offsets)
        yield from enumerate(offsets)


def replace_class_with_str(method, *args, **kw):
    if args and isinstance(args[0], Str):
        args = (str(args[0]), *args[1:])
    return method(*args, **kw)


class External:

    @pin.cls
    def _charset_detect(cls):
        return optional("charset_normalizer.detect")

    @pin.cls
    def _from_buffer(cls):
        return optional("magic.from_buffer")

    @pin.cls
    def _from_content(cls):
        return optional("magic.detect_from_content")

    #

    @pin.cls
    def charset_detect(cls):
        if detect := External._charset_detect:
            def charset_detect(x: bytes) -> str:
                return detect(x)
        else:
            def charset_detect(x: bytes) -> None: ...

        return charset_detect

    @pin.cls
    def mime_reader(cls):
        if (read := cls._from_buffer) and (detect := cls._from_content):
            def mime_reader(x: bytes) -> dict[str, str]:
                return {
                    "type": detect(x).mime_type,
                    "description": read(x)}
        else:
            def mime_reader(x: bytes) -> None: ...

        return mime_reader


@proxy_to(
    "text",
    "__add__", "__contains__", "__eq__", "__format__", "__hash__", "__ge__",
    "__getitem__", "__gt__", "__iter__", "__le__", "__len__", "__lt__", "__mod__",
    "__mul__", "__ne__", "__rmod__", "__rmul__", "__sizeof__", "capitalize",
    "casefold", "center", "count", "encode", "endswith", "expandtabs", "find",
    "format", "format_map", "index", "isalnum", "isalpha", "isascii", "isdecimal",
    "isdigit", "isidentifier", "islower", "isnumeric", "isprintable", "isspace",
    "istitle", "isupper", "join", "ljust", "lower", "lstrip", "maketrans",
    "partition", "removeprefix", "removesuffix", "replace", "rfind", "rindex",
    "rjust", "rpartition", "rsplit", "rstrip", "split", "splitlines", "startswith",
    "strip", "swapcase", "title", "translate", "upper", "zfill",
    pin, pre=replace_class_with_str,
)
class Str:
    """A class for handling bytes | str objects.

    Autodetect charsets, autoencode/decode from bytes/text.
    Just pass any bytes | str object to Str and use it:

    x = Str(b'hello')
    str(x) == 'hello'
    bytes(x) == b'hello'

    """

    InternalCharset   : str = "utf-8"
    DetectionSizeLimit: int = 2 ** 20
    DetectionScanLimit: int = 2 ** 10

    to_ascii = staticmethod(to_ascii)

    @classmethod
    def to_bytes(cls, obj, *args, **kw):
        return bytes(cls(obj, *args, **kw))

    @classmethod
    def to_text(cls, obj, *args, **kw):
        return str(cls(obj, *args, **kw))

    #

    @classmethod
    def downcast(cls, obj):
        if isinstance(obj, bytes | str):
            return obj

        if isinstance(obj, int):
            return str(obj)

        msg = f"{Who(cls)} accept bytes | str, got {Who.Is(obj)}"
        raise TypeError(msg)

    @pin
    def mime(self):
        try:
            return External.mime_reader(self.bytes)

        except Exception:  # noqa: BLE001 Do not catch blind exception: `Exception`
            logger.warning(
                f"something went wrong for {self.bytes[:2**10]!r}", exc_info=True)

    #

    def __bytes__(self):
        return self.bytes

    def __str__(self):
        return self.text

    def __init__(self, obj, /, charset=None):
        self._object = obj
        self._charset = charset or self.InternalCharset

    @pin
    def _value(self):
        return self.downcast(self._object)

    #

    @pin
    def external_charset(self):
        return External.charset_detect(self.bytes)

    @pin
    def probe_order(self):
        result = [self._charset]

        if meta := self.external_charset:
            result.append(meta["encoding"])

        return tuple(unique([*result, "ascii"]))

    @pin
    def compatible_charset(self):
        string = self._value

        if isinstance(string, bytes):
            method = string.decode
            order = self.probe_order

        else:
            method = string.encode
            order = tuple(reversed(self.probe_order))

        for charset in filter(bool, order):
            with suppress(UnicodeEncodeError, UnicodeDecodeError):
                method(charset)
                return charset

    @pin
    def charset(self):
        string = self._value
        is_bytes = isinstance(string, bytes)

        read_limit = self.DetectionSizeLimit
        if not is_bytes and len(string) <= read_limit:
            read_limit = 0

        default = "ascii"
        if not string:
            return default

        collected = set()
        scan_limit = self.DetectionScanLimit

        for no, char in iter_by_binary_offsets(string, ordinate=not is_bytes):
            if no > read_limit:
                break

            if char < 0x20:  # noqa: PLR2004
                if char in (0x9, 0xa, 0xc, 0xd):
                    continue
                return "binary"

            if char >= 0x7f:  # noqa: PLR2004, ANSI Extended Border
                if is_bytes:
                    default = "ansi"

                elif char not in collected:
                    if len(collected) >= scan_limit:
                        return self.compatible_charset
                    collected.add(char)

        return default if is_bytes else self.compatible_charset

    #

    @pin
    def bytes(self):
        string = self._value
        return string if isinstance(string, bytes) else string.encode(self._charset)

    @pin
    def text(self):
        string = self._value
        if isinstance(string, str):
            return string

        charset = self.charset
        if charset == "ansi":
            charset = self.compatible_charset

        if charset != "binary":
            return string.decode(charset)

        msg = f"couldn't {charset=} decode {string[:2**10]!r}"
        if charset := self.charset:
            msg = f"{msg}; {charset}"

        raise ValueError(msg)

    def __repr__(self):
        string = self._value
        size = f"{len(self.bytes):d}"

        length = ""
        charset = (f"{self.charset} ".upper()) if self.charset else ""

        if isinstance(string, str) and len(self.bytes) != len(self.text):
            length = f"={len(self.text):d}"

        return (
            f"<{charset}{Who(self, full=False)}"
            f"[{Who(self._object, full=False)}"
            f"({size})]{length} at {id(self):#x}>")

    #

    def tokenize(self, regex=r"([\w\d]+)"):
        return findall(regex, self.text)
