#!/usr/bin/python   # Script python per il parsing del file caricato in upload su server da elaborare in formato json
import sys, os
import re, json
import pymongo
from pymongo import MongoClient

parsed_output = {
    'Count': 0,
    'Header': [],
    'Data': []
}

def main(argv):
   
    # Ottengo la stringa relativa al file da processare
    input_file = argv[0]
    
    print 'Starting parsing procedure for file ' + input_file

    print 'Expanding fields...'
    os.system("python vcf_melt.py " + input_file)

    print 'Populating Database...'
    # Connessione a MongoDB
    client = MongoClient()

    # Creazione del database [nome_file_input]
    db = client['test_vcf']

    # Creazione della tabella 'Rows' (contiene le righe del file appena parsato)
    rows = db.rows
    
    i = 0         # Usato per sapere quando stiamo leggendo le righe
    headers = 0     # Memorizzato per salvare gli header del file in input

    for line in open(re.sub("(\.)(\w)*$", "", input_file) + '_parsed.txt'):
        
        if i != 0:    # Riga
            
            r = re.sub("\n", "", line).split('\t')
            data = {}   # variabile utilizzata per riferirsi all'i-esima riga del file

            for h in range(len(headers)):
                data[headers[h].replace('.', '_')] = r[h]

            rows.insert_one(data)
        
        else:          # Header

            headers = re.sub("\n", "", line).split('\t')
        
        i = i + 1
    
#    print 'Creating JSON file...'

#   row = 0 # Questa variabile mi permette di identificare l'header (la prima riga del file)

#    for line in open(re.sub("(\.)(\w)*$", "", input_file) + '_parsed.txt'):
        
#        if row != 0:    # Salvo la riga
#            data = {
#                '_id': row,
#                'row': re.sub("\n", "", line).split('\t')
#            }

#            parsed_output['Data'].append(data)
#            #print line
        
#        else:   # Salvo l'header
#            print line
#            parsed_output['Header'] = re.sub("\n", "", line).split('\t')
        
#        # Aggiorno l'indice di riga
#        row = row + 1
    
#    parsed_output['Count'] = row
#    print 'Saving JSON file...'
    
#    # Salvo le informazioni in un file json
#    with open(re.sub("(\.)(\w)*$", "", input_file) + '.json', 'w') as output_file:
#        json.dump(parsed_output, output_file)

    print 'Done.'

''' Versione che effettua il parse del file tramite regex 
    for line in open(input_file):
        
        # Comincio identificando l'header del file'
        header = re.match('^#[^#]([a-zA-Z0-9])*', line)
        if header:
            print line

            uncommented = re.sub('#', "", line)
            parsed_output['Header'] = re.sub("\n", "", uncommented).split('\t')
        
        # Cerco le righe della tabella
        row = re.match('chr*', line)
        if row:
            #print line
            
            parsed_output['Rows'].append(re.sub("\n", "", line).split('\t'))

    #salvo le informazioni in un file json
    with open('test.json', 'w') as output_file:
        json.dump(parsed_output, output_file)
'''

if __name__ == "__main__":
   main(sys.argv[1:])