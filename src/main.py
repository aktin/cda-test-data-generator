import csv_import
import csv_to_cda

if __name__ == '__main__':
    
    # TODO Proper import
    data_csv = csv_import.generate_csv('res/CDAVariables.xlsx')
    xslt_file = 'res/EmergencyNote.xslt'
    csv_to_cda.csv_to_cda(data_csv, xslt_file)