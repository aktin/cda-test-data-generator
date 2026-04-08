"""
transformer.py
--------------
Apply EmergencyNote.xslt to a flat field dict and return the CDA tree.
"""

import os
from lxml import etree

_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_XSLT = os.path.join(_HERE, "..", "resources", "EmergencyNote.xslt")

_transform_cache: dict = {}


def _get_transform(xslt_path: str) -> etree.XSLT:
    if xslt_path not in _transform_cache:
        xslt_tree = etree.parse(xslt_path)
        _transform_cache[xslt_path] = etree.XSLT(xslt_tree)
    return _transform_cache[xslt_path]


def transform(fields: dict, xslt_path: str = DEFAULT_XSLT) -> etree._ElementTree:
    """
    Apply EmergencyNote.xslt to *fields* and return the resulting CDA element tree.

    Parameters
    ----------
    fields : dict
        Keys are XSLT field names; values are strings.
    xslt_path : str
        Path to EmergencyNote.xslt.

    Returns
    -------
    etree._ElementTree
        The generated CDA document as an lxml element tree.
    """
    # Build <aktin_raw> with one child element per field (matches the XSLT root template)
    root_el = etree.Element("aktin_raw")
    for key, value in fields.items():
        child = etree.SubElement(root_el, key)
        child.text = str(value) if value is not None else ""

    input_tree = etree.ElementTree(root_el)
    xslt_func = _get_transform(xslt_path)
    result = xslt_func(input_tree)
    return result
