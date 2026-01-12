import re
from typing import Any, Dict, Literal

from toon_format import encode, decode, EncodeOptions, DecodeOptions


def json_to_toon(data: Dict[str, Any], *,
                 delimiter: str = ",",
                 indent: int = 2,
                 length_marker: Literal["#", False] = "#") -> str:
    """
    Converte un dict JSON in una stringa TOON usando toon‑python.

    Args:
        data: dict da serializzare
        delimiter: delimitatore per array (default ",")
        indent: spazi per livello indentazione (default 2)
        length_marker: prefisso lunghezza array (default "")

    Returns:
        stringa TOON
    """

    options: EncodeOptions = {
        "indent": indent,
        "delimiter": delimiter,
        "lengthMarker": length_marker
    }
    toon_str = encode(data, options=options)
    return toon_str


def toon_to_json(toon_str: str, *, indent: int = 2, strict: bool = True) -> Any:
    """
    Converte una stringa TOON in un oggetto Python (dict/list) usando toon‑python.

    Args:
        toon_str: stringa TOON da deserializzare
        indent: indentazione attesa (default 2)
        strict: se attivare il parsing rigoroso (default True)

    Returns:
        oggetto Python risultante (dict, list, etc)
    """
    options: DecodeOptions = DecodeOptions(indent=indent, strict=strict)
    obj = decode(toon_str, options=options)
    return obj
