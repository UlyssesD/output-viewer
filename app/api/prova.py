#!/usr/bin/python   # Script python per il parsing del file caricato in upload su server da elaborare in formato json
#-*- coding: utf-8 -*-

import sys, os
import re, json
import vcf

import pymongo
from pymongo import MongoClient
from neo4j.v1 import GraphDatabase, basic_auth

parsed_output = {
    'Count': 0,
    'Header': [],
    'Data': []
}



def main(argv):
   
    # Ottengo la stringa relativa al file da processare
    input_file = argv[0]
    
    print 'Starting parsing procedure for file ' + input_file

#    print 'Expanding fields...'
#    os.system("python vcf_melt.py " + input_file)

    print 'Opening .vcf file...'
    file = open(input_file, 'r')
    reader = vcf.VCFReader(file)

    # Versione che salva le righe del file in GraphDB
    print 'Populating Database...'


    # Connessione a Neo4j
    driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "password"));
    session = driver.session()

    # Creo un nodo corrispondente al file
    filename = os.path.basename(file.name)
    file_id = ''
    f = session.run("CREATE (f: File {name:'"+ filename + "'}) RETURN ID(f) as file_id")

    for res in f: file_id = res["file_id"]

    for record in reader:
        
        # Genero il nodo corrispondente alla variante
        variant = {
            "CHROM": record.CHROM,
            "POS": record.POS,
            "START": record.start,
            "END": record.end,
            "ID": record.ID or '.',
            "REF": record.REF,
            "ALT": str(record.ALT).strip('[]').split(','),
            "AFFECTED_START": record.affected_start,
            "AFFECTED_END": record.affected_end,
            "QUAL": record.QUAL,
            "FILTER": record.FILTER or '.',
            "FORMAT": record.FORMAT or '.',
            "HETEROZIGOSITY": record.heterozygosity,
            "MUTATION": record.var_type
        }

        variant_id = ''
        v = session.run("CREATE (v: Variant {CHROM: {CHROM}, POS: {POS}, START: {START}, END: {END}, ID: {ID}, REF: {REF}, ALT: {ALT}, AFFECTED_START: {AFFECTED_START}, AFFECTED_END: {AFFECTED_END}, QUAL: {QUAL}, FILTER: {FILTER}, FORMAT: {FORMAT}, HETEROZIGOSITY: {HETEROZIGOSITY}, MUTATION: {MUTATION}}) RETURN ID(v) as variant_id", variant)

        for res in v: variant_id = res["variant_id"]
        
        # Creo la relazione File -> Variante
        session.run("MATCH (f: File), (v: Variant) where ID(f) = {file_id} and ID(v) = {variant_id} create (f)-[:Contains]->(v)", {
            "file_id": file_id,
            "variant_id": variant_id
        })
        
        # Costruisco la stringa della lista degli attributi delle annotazioni (sono costretto a farlo perchè non ho un modo univoco per sapere a priori i campi presenti)
        annotation = {}
        attributes = '{ '
        for (key, value) in record.INFO.items():


            # Per ogni chiave considerata, formatto la stringa usata come attributo in Neo4j (necessario per questioni di queri, non accetta '.', '+' oppure stringhe numeriche)
            #if re.match('^(\d+)', key):
            #    key = "__number__" + key
            
           
            #key = key.replace(".", "__dot__")
            #key = key.replace("+", "__plus__")

            attributes = attributes + '`' + key + '`: {`'  + key + '`}, '
            annotation[key] = str(value).strip('[]').split(',')

        attributes = attributes.strip(', ') + '}'
        
        # Genero il nodo corrispondente alle annotazioni
        info_id = ''
        i = session.run("CREATE (i: Info " + attributes + ") return ID(i) as info_id", annotation);

        for res in i: info_id = res["info_id"]

        # Creo la relazione Variante -> Info
        session.run("MATCH (v: Variant), (i: Info) where ID(v) = {variant_id} and ID(i) = {info_id} create (v)-[:Annotation]->(i)", {
            "variant_id": variant_id,
            "info_id": info_id
        })

        # Ricavo i nomi degli attributi dei sample
        format_vars = record.FORMAT.split(':')

        for sample in record.samples:
            attributes = '{ sample: "' + sample.sample + '", phased: ' + str(sample.phased) + ', state: ' + str(sample.gt_type) + ', '
            genotype = {}

            for i in range(len(format_vars)): 
                attributes = attributes + format_vars[i] + ': {' + format_vars[i] + '}, ' 
                genotype[format_vars[i]] = sample.data[i]

            attributes = attributes.strip(', ') + '}'

            # Genero il nodo corrispondente all'i-esimo genotipo
            genotype_id = ''
            g = session.run("CREATE (g: Genotype " + attributes + ") return ID(g) as genotype_id", genotype);

            for res in g: genotype_id = res["genotype_id"]

            # Creo la relazione Variante -> Info
            session.run("MATCH (v: Variant), (g: Genotype) where ID(v) = {variant_id} and ID(g) = {genotype_id} create (v)-[:Sample]->(g)", {
                "variant_id": variant_id,
                "genotype_id": genotype_id
            })
            
    ''' 
    # Versione che salva le righe del file in mongoDB 
    print 'Populating Database...'
    # Connessione a MongoDB
    client = MongoClient()

    # Creazione del database [nome_file_input]
    db = client['test_vcf']

    # Creazione della tabella 'Rows' (contiene le righe del file appena parsato)
    rows = db.rows
    
    i = 0         # Usato per sapere quando stiamo leggendo le righe
    headers = []    # Memorizzato per salvare gli header del file in input

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
    '''

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

    # Chiudo la sessione di Neo4j e termino
    session.close()
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