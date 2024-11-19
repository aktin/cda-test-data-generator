import csv
import os
from typing import Callable

import lxml.etree
from lxml import etree


def create_directory(path: str) -> None:
    """
    Create a directory if it does not already exist.

    Args:
        path (str): The path of the directory to create.

    Returns:
        None
    """
    if not os.path.isdir(path):
        os.mkdir(path)


def csv_to_dict(csv_file: str) -> dict:
    """
    Convert a CSV file to a dictionary.

    Args:
        csv_file (str): The path to the CSV file.

    Yields:
        dict: A dictionary where the keys are the CSV header fields and the values are the corresponding row values.
    """
    with open(csv_file, 'r', newline='', encoding="UTF-8") as f:
        csv_reader = csv.reader(f)
        header_row = next(csv_reader)
        for row in csv_reader:
            yield {field.strip(): value.strip() for field, value in zip(header_row, row)}


def dict_to_xml(data: dict) -> etree.Element:
    """
    Convert a dictionary to an XML element tree.

    Args:
        data (dict): The dictionary to convert, where keys are element tags and values are element text.

    Returns:
        lxml.etree.Element: The root element of the created XML tree.
    """
    root = etree.Element('aktin_raw')
    for key, value in data.items():
        record = etree.SubElement(root, key)
        record.text = value
    return root


def save_xml(xml_root: lxml.etree.Element, file_path: str) -> None:
    """
    Save an XML element tree to a file.

    Args:
        xml_root (lxml.etree.Element): The root element of the XML tree to save.
        file_path (str): The path to the file where the XML tree will be saved.

    Returns:
        None
    """
    with open(file_path, 'wb') as xml_file:
        xml_file.write(etree.tostring(xml_root, pretty_print=True, encoding='UTF-8'))


def transform_xml(xml_root: etree.Element, xslt_transform: Callable) -> etree._XSLTResultTree:
    """
    Apply an XSLT transformation to an XML element tree.

    Args:
        xml_root (lxml.etree._Element): The root element of the XML tree to transform.
        xslt_transform (lxml.etree.XSLT): The XSLT transformation to apply.

    Returns:
        lxml.etree._XSLTResultTree: The transformed XML tree.
    """
    return xslt_transform(xml_root)


def add_processing_instructions(tree: etree.ElementTree) -> etree.ElementTree:
    """
    Add processing instructions to an XML element tree.

    Args:
        tree (lxml.etree._ElementTree): The XML element tree to which the processing instructions will be added.

    Returns:
        lxml.etree._ElementTree: The XML element tree with the added processing instructions.
    """
    pi1 = etree.ProcessingInstruction('xml-stylesheet', 'type="text/xsl" href="../stylesheets/CDA.xsl"')
    pi2 = etree.ProcessingInstruction('xml-model', 'href="../schematron-basis/aktin-basism20152b.sch" '
                                                   'type="application/xml" '
                                                   'schematypens="https://purl.oclc.org/dsdl/schematron"')
    tree.getroot().addprevious(pi1)
    tree.getroot().addprevious(pi2)
    return tree

def add_warning_comment(tree: etree.ElementTree, warning: str) -> etree.ElementTree:
    """
    Add a warning comment to an XML element tree.

    Args:
        tree (lxml.etree._ElementTree): The XML element tree to which the warning comment will be added.
        warning (str): The warning message to add to the comment.

    Returns:
        lxml.etree._ElementTree: The XML element tree with the added warning comment.
    """
    comment = etree.Comment(warning)
    tree.getroot().addprevious(comment)
    return tree


def csv_to_cda(csv_file: str, xslt_file: str, output_dir: str) -> None:
    """
    Convert a CSV file to CDA format using XSLT transformation and save the output.

    Args:
        csv_file (str): The path to the CSV file to convert.
        xslt_file (str): The path to the XSLT file for transformation.
        output_dir (str): The directory to save the output files.

    Returns:
        None
    """
    raw_path = os.path.join(output_dir, 'raw')
    cda_path = os.path.join(output_dir, 'cda')

    create_directory(output_dir)
    create_directory(raw_path)
    create_directory(cda_path)

    # Load XSLT transformation from Skeleton
    xslt_transform = etree.XSLT(etree.parse(xslt_file))
    # Create Parser
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)

    for i, csv_data in enumerate(csv_to_dict(csv_file), start=1):
        # Create and save raw XML
        raw_xml = dict_to_xml(csv_data)
        save_xml(raw_xml, os.path.join(raw_path, f'aktin_raw_{i}.xml'))

        # Transform raw XML with XSLT
        transformed_xml = transform_xml(raw_xml, xslt_transform)
        xml_root = etree.fromstring(str(transformed_xml), parser=parser)
        tree = add_processing_instructions(etree.ElementTree(xml_root))
        tree = add_warning_comment(tree, "WARNING!. This file was random generated.")

        # Save CDA
        save_xml(tree, os.path.join(cda_path, f'cda_{i}.xml'))