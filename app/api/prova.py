#!/usr/bin/python   # Script python per il parsing del file caricato in upload su server da elaborare in formato json
#-*- coding: utf-8 -*-

import uuid
import sys, os
import re, json
import vcf, csv

import pymongo
from pymongo import MongoClient
from neo4j.v1 import GraphDatabase, basic_auth

parsed_output = {
    'Count': 0,
    'Header': [],
    'Data': []
}



def main(argv):
        
    # File csv per i nodi del grafo
    #fileWriter = csv.writer(open('file.csv', 'w'), delimiter=',')
    #variantWriter = csv.writer(open('variant.csv', 'w'), delimiter=',')
    #infoWriter = csv.writer(open('info.csv','w'), delimiter=',')
    #genotypeWriter = csv.writer(open('genotype.csv','w'), delimiter=',')

    # File csv per le relazioni del grafo
    #containsWriter = csv.writer(open('contains.csv', 'w'), delimiter=',')
    #annotationWriter = csv.writer(open('contains.csv', 'w'), delimiter=',')
    #sampleWriter = csv.writer(open('sample.csv', 'w'), delimiter=',')


    # Ottengo la stringa relativa al file da processare
    input_file = argv[0]
    
    print 'Starting parsing procedure for file ' + input_file

#    print 'Expanding fields...'
#    os.system("python vcf_melt.py " + input_file)

    print 'Opening .vcf file...'
    file = open(input_file, 'r')
    reader = vcf.VCFReader(file)

    # Costruisco gli header dei nodi
    file_header = ["name", "total", "hom", "het", "hom_alt", "uncalled", "snp", "indels", "unknown", "in_dbSNP", "not_in_dbSNP", "in_1000g", "not_in_1000g"]
    variant_header = ["variantId", "CHROM", "POS", "START", "END", "ID", "REF", "ALT", "QUAL", "FILTER", "FORMAT", "HETEROZIGOSITY", "MUTATION", "dbSNP"]

    
    # Ricavo gli header per formats e info (necessari per avere gli header dei csv rispettivamente di Genotype e Info)
    print 'Retrieving formats and infos...'
    genotype_header = ["genotypeId", "sample", "phased", "state"] + reader.formats.keys()
    info_header = ["annotationId"] + reader.infos.keys()
    
    # Cotruisco gli header delle relazioni
    contains_header = ["filename", "variantId"]
    annotation_header = ["variantId", "annotationId"]
    sample_header = ["variantId", "genotypeId"]

    # Scrivo gli header dei nodi nei rispettivi file
    #fileWriter.writerow(file_header)
    #variantWriter.writerow(variant_header)
    #genotypeWriter.writerow(genotype_header)
    #infoWriter.writerow(info_header)

    # Scrivo gli header delle relazioni nei rispettivi file
    #containsWriter.writerow(contains_header)
    #annotationWriter.writerow(annotation_header)
    #sampleWriter.writerow(sample_header)

    #sys.exit()


    # Versione che salva le righe del file in GraphDB
    print 'Populating Database...'


    # Connessione a Neo4j
    driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "password"));
    session = driver.session()

    # Creo un nodo corrispondente al file
    properties = {
        "filename": os.path.basename(file.name),
        "total": 0,
        "hom": 0,
        "het": 0,
        "hom_alt": 0,
        "uncalled": 0,
        "snp": 0,
        "indels": 0,
        "unknown": 0,
        "in_dbSNP": 0,
        "not_in_dbSNP": 0,
        "in_1000g": 0,
        "not_in_1000g": 0
    }

    file_id = ''
   
    # f = session.run("CREATE (f: File { name:{filename} }) RETURN ID(f) as file_id", properties)
    # for res in f: file_id = res["file_id"]

    session.run("CREATE INDEX ON :File(name)")
    session.run("CREATE INDEX ON :Variant(variant_id)")
    session.run("MERGE (u:User { username:{username} })", {
        "username": 'lola'
    })
    #f = session.run("CREATE(f:File { name:{filename} })", properties)
    session.run("MATCH (u:User) WHERE u.username='lola' CREATE (u)-[:Owns]->(f:File { name:{filename} })", properties)


    for record in reader:
        
        # Genero il nodo corrispondente alla variante
        variant = {
            "variant_id": str(uuid.uuid4()), # id randomico utilizzato per indicizzare le varianti

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

        # Aggiorno le statistiche sul file
        properties["total"] += 1
        properties["hom"] += record.num_hom_ref
        properties["het"] += record.num_het
        properties["hom_alt"] += record.num_hom_alt
        properties["uncalled"] += record.num_unknown

        if variant["MUTATION"] == 'snp':
            properties["snp"] += 1
        elif variant["MUTATION"]== 'indel':
            properties["indels"] += 1
        else:
            properties["unknown"] += 1

        # variant_id = ''
        # v = session.run("CREATE (v: Variant {CHROM: {CHROM}, POS: {POS}, START: {START}, END: {END}, ID: {ID}, REF: {REF}, ALT: {ALT}, AFFECTED_START: {AFFECTED_START}, AFFECTED_END: {AFFECTED_END}, QUAL: {QUAL}, FILTER: {FILTER}, FORMAT: {FORMAT}, HETEROZIGOSITY: {HETEROZIGOSITY}, MUTATION: {MUTATION}}) RETURN ID(v) as variant_id", variant)
        # for res in v: variant_id = res["variant_id"]

        v = session.run("MATCH (f:File) WHERE f.name={file_id} CREATE (f)-[:Contains]->(v:Variant) SET v = {variant}", {
            "file_id": properties["filename"],
            "variant": variant
            })


        # Creo la relazione File -> Variante
        #session.run("MATCH (f: File), (v: Variant) where ID(f) = {file_id} and ID(v) = {variant_id} create (f)-[:Contains]->(v)", {
        #    "file_id": file_id,
        #    "variant_id": variant_id
        #})
        
        # Costruisco la stringa della lista degli attributi delle annotazioni (sono costretto a farlo perchè non ho un modo univoco per sapere a priori i campi presenti)
        annotation = {}
        #attributes = '{ '

        for (key, value) in record.INFO.items():

            if re.match('(\w*)snp(\w*)', key):
                # session.run("MATCH (v: Variant) where ID(v) = {variant_id} set v += { dbSNP:{dbSNP} }", {
                #    "variant_id": variant_id,
                #    "dbSNP": str(value).strip('[]').split(',')
                #})

                session.run("MATCH (v: Variant) WHERE v.variant_id={variant_id} SET v += { dbSNP:{dbSNP} }", {
                    "variant_id": variant["variant_id"],
                    "dbSNP": str(value).strip('[]').split(',')
                })

                if str(value).strip('[]').split(',')[0] == 'None':
                    properties['not_in_dbSNP'] += 1
                else:
                    properties['in_dbSNP'] += 1
            
            if re.match('1000g(\w*)_all', key):
                if value:
                    properties['in_1000g'] += 1
                else:
                    properties['not_in_1000g'] += 1
                

            # Per ogni chiave considerata, formatto la stringa usata come attributo in Neo4j (necessario per questioni di queri, non accetta '.', '+' oppure stringhe numeriche)
            #if re.match('^(\d+)', key):
            #    key = "__number__" + key
            
           
            #key = key.replace(".", "__dot__")
            #key = key.replace("+", "__plus__")

            #attributes = attributes + '`' + key + '`: {`'  + key + '`}, '
            annotation[key] = str(value).strip('[]').split(',')

        #attributes = attributes.strip(', ') + '}'
        
        # Genero il nodo corrispondente alle annotazioni
        # info_id = ''
        # i = session.run("CREATE (i: Info " + attributes + ") return ID(i) as info_id", annotation);

        #for res in i: info_id = res["info_id"]

        # Creo la relazione Variante -> Info
        #session.run("MATCH (v: Variant), (i: Info) where ID(v) = {variant_id} and ID(i) = {info_id} create (v)-[:Annotation]->(i)", {
        #    "variant_id": variant_id,
        #    "info_id": info_id
        #})
        session.run("MATCH (v:Variant) WHERE v.variant_id = {variant_id} create (v)-[:Annotation]->(i: Info) set i = {annotation}", {
            "variant_id": variant["variant_id"],
            "annotation": annotation
        })

        # Ricavo i nomi degli attributi dei sample
        format_vars = record.FORMAT.split(':')

        for sample in record.samples:
            
            
            #attributes = '{ sample: "' + sample.sample + '", phased: ' + str(sample.phased) + ', state: ' + str(sample.gt_type) + ', '
            genotype = {
                "sample": sample.sample,
                "phased": sample.phased,
                "state": sample.gt_type
            }

            for i in range(len(format_vars)): 
                #attributes = attributes + format_vars[i] + ': {' + format_vars[i] + '}, ' 
                genotype[format_vars[i]] = sample.data[i]

            #attributes = attributes.strip(', ') + '}'

            # Genero il nodo corrispondente all'i-esimo genotipo
            # genotype_id = ''
            # g = session.run("CREATE (g: Genotype " + attributes + ") return ID(g) as genotype_id", genotype);

            # for res in g: genotype_id = res["genotype_id"]

            # Creo la relazione Variante -> Info
            #session.run("MATCH (v: Variant), (g: Genotype) where ID(v) = {variant_id} and ID(g) = {genotype_id} create (v)-[:Sample]->(g)", {
            #    "variant_id": variant_id,
            #    "genotype_id": genotype_id
            #})

            session.run("MATCH (v:Variant) WHERE v.variant_id={variant_id} CREATE (v)-[:Sample]->(g: Genotype) SET g = {genotype}", {
                "variant_id": variant["variant_id"],
                "genotype": genotype
            })

    #salvo le proprietà calcolate nel nodo
    session.run("MATCH (f: File) WHERE f.name={filename} SET f += { total:{total}, hom:{hom}, het:{het}, hom_alt:{hom_alt}, uncalled:{uncalled}, snp:{snp}, indels:{indels}, unknown:{unknown}, in_dbSNP:{in_dbSNP}, not_in_dbSNP:{not_in_dbSNP}, in_1000g:{in_1000g}, not_in_1000g:{not_in_1000g} }", properties)

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

    # Chiudo la sessione di Neo4j e termino
    session.close()
    print 'Done.'


if __name__ == "__main__":
   main(sys.argv[1:])