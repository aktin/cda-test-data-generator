from lxml import etree


def xslt_transform(xml_path: str, xsl_path: str, output_path: str) -> None:
    """
    Transform an XML file using an XSLT stylesheet and save the result to a file.

    Args:
        xml_path (str): The path to the input XML file.
        xsl_path (str): The path to the XSLT stylesheet file.
        output_path (str): The path to save the transformed XML file.

    Returns:
        None
    """
    # Parse the XML and XSL files
    xml_tree = etree.parse(xml_path)
    xsl_tree = etree.parse(xsl_path)

    # Create an XSLT transform object
    transform = etree.XSLT(xsl_tree)

    # Apply the transformation
    result_tree = transform(xml_tree)

    # Define and add processing instructions to cda
    pi1 = etree.ProcessingInstruction('xml-stylesheet', 'type="text/xsl" href="../stylesheets/CDA.xsl"')
    pi2 = etree.ProcessingInstruction('xml-model', 'href="../schematron-basis/aktin-basism20152b.sch" '
                                                   'type="application/xml" '
                                                   'schematypens="https://purl.oclc.org/dsdl/schematron"')
    result_tree.getroot().addprevious(pi1)
    result_tree.getroot().addprevious(pi2)

    # Save the result to a file
    result_tree.write(output_path, pretty_print=True, encoding='UTF-8', xml_declaration=True)



