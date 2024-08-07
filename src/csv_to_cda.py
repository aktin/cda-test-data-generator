import csv
import os

from lxml import etree


def csv_to_cda(csv_file, xslt_file) -> None:
    xslt_doc = etree.parse(xslt_file)
    transform = etree.XSLT(xslt_doc)  # XSLT tree

    # Read CSV data
    with open(csv_file, 'r', newline='') as f:
        csv_reader = csv.reader(f)
        header_row = next(csv_reader)
        for i, row in enumerate(csv_reader, start=1):
            # Create a dictionary to hold CSV values
            csv_data = {field.strip(): value.strip() for field, value in zip(header_row, row)}

            root = etree.Element('aktin_raw')
            for key, value in csv_data.items():
                record = etree.SubElement(root, key)
                record.text = value

            # Create new file with raw xml data 'aktin_raw_{number}
            os.mkdir('../output/') if not os.path.isdir('../output/') else None
            os.mkdir('../output/raw') if not os.path.isdir('../output/raw') else None
            output_file = os.path.join('../output/raw', f'aktin_raw_{i}.xml')
            with open(output_file, 'wb') as aktin_raw_xml:
                aktin_raw_xml.write(etree.tostring(root, pretty_print=True, encoding='UTF-8'))

            # Perform XSLT transformation
            transformed_xml_data = transform(root)

            parser = etree.XMLParser(remove_blank_text=True)
            xml_root = etree.fromstring(str(transformed_xml_data), parser=parser)

            tree = etree.ElementTree(xml_root)

            # Define and add processing instructions to cda
            pi1 = etree.ProcessingInstruction('xml-stylesheet', 'type="text/xsl" href="../stylesheets/CDA.xsl"')
            pi2 = etree.ProcessingInstruction('xml-model', 'href="../schematron-basis/aktin-basism20152b.sch" '
                                                           'type="application/xml" '
                                                           'schematypens="https://purl.oclc.org/dsdl/schematron"')
            tree.getroot().addprevious(pi1)
            tree.getroot().addprevious(pi2)

            # Write XML output to file
            os.mkdir('../output/') if not os.path.isdir('../output/') else None
            os.mkdir('../output/cda') if not os.path.isdir('../output/cda') else None
            output_file = os.path.join('../output/cda', f'cda_{i}.cda')

            with open(output_file, 'wb') as xml_file:
                xml_file.write(
                    etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
