import csv_import

if __name__ == '__main__':
    data_csv = csv_import.export_to_csv('res/CDAVariables.xlsx')
    # xslt_file = 'res/EmergencyNote.xslt'
    # csv_to_cda(data_csv, xslt_file)