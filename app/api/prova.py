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
    
    # Ottengo la stringa relativa al file da processare
    input_file = argv[0]

    # File csv per i nodi del grafo
    file_csv = open('file.csv', 'w')
    variant_csv = open('variant.csv', 'w')
    info_csv = open('info.csv','w')
    genotype_csv = open('genotype.csv','w')
    
    # File csv per le relazioni del grafo
    contains_csv = open('contains.csv', 'w')
    annotaion_csv = open('annotation.csv', 'w')
    sample_csv = open('sample.csv', 'w')

    # Inizializzo i writer per tutti i file
    fileWriter = csv.writer(file_csv)
    variantWriter = csv.writer(variant_csv, delimiter=',')
    infoWriter = csv.writer(info_csv, delimiter=',')
    genotypeWriter = csv.writer(genotype_csv, delimiter=',')

    containsWriter = csv.writer(contains_csv, delimiter=',')
    annotationWriter = csv.writer(annotaion_csv, delimiter=',')
    sampleWriter = csv.writer(sample_csv, delimiter=',')

    
    print 'Starting parsing procedure for file ' + input_file

    print 'Opening .vcf file...'
    file = open(input_file, 'r')
    reader = vcf.VCFReader(file)


    # Costruisco gli header dei nodi
    file_header = ["name", "total", "hom", "het", "hom_alt", "uncalled", "snp", "indels", "unknown", "in_dbSNP", "not_in_dbSNP", "in_1000g", "not_in_1000g"]
    variant_header = ["variant_id", "CHROM", "POS", "START", "END", "ID", "REF", "ALT", "QUAL", "FILTER", "FORMAT", "HETEROZIGOSITY", "MUTATION", "dbSNP"]
    
    # Ricavo gli header per formats e info (necessari per avere gli header dei csv rispettivamente di Genotype e Info)
    print 'Retrieving formats and infos...'
    genotype_header = set(["genotype_id", "sample", "phased", "state"] + reader.formats.keys()) 
    info_header = set(["info_id"] + reader.infos.keys())

    for record in reader:
           
        for key in record.INFO.keys():
            info_header.add(key)
        for key in record.FORMAT.split(':'):
            genotype_header.add(key)

    file.close()

    genotype_header = list(genotype_header)
    info_header = list(info_header)

    # Cotruisco gli header delle relazioni
    contains_header = ["name", "variant_id"]
    annotation_header = ["variant_id", "info_id"]
    sample_header = ["variant_id", "genotype_id"]

    # Scrivo gli header dei nodi nei rispettivi file
    fileWriter.writerow(file_header)
    variantWriter.writerow(variant_header)
    genotypeWriter.writerow(genotype_header)
    infoWriter.writerow(info_header)

    # Scrivo gli header delle relazioni nei rispettivi file
    containsWriter.writerow(contains_header)
    annotationWriter.writerow(annotation_header)
    sampleWriter.writerow(sample_header)

    # Versione che salva le righe del file in GraphDB
    print 'Populating Database...'

    # Connessione a Neo4j
    driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "password"));
    session = driver.session()

    # Creo un nodo corrispondente al file
    properties = {
        "name": os.path.basename(file.name),
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
   
    # f = session.run("CREATE (f: File { name:{filename} }) RETURN ID(f) as file_id", properties)
    # for res in f: file_id = res["file_id"]

    #session.run("CREATE INDEX ON :File(name)")
    #session.run("CREATE INDEX ON :Variant(variant_id)")
    #session.run("MERGE (u:User { username:{username} })", {
    #    "username": 'lola'
    #})
    #f = session.run("CREATE(f:File { name:{filename} })", properties)
    #session.run("MATCH (u:User) WHERE u.username='lola' CREATE (u)-[:Owns]->(f:File { name:{filename} })", properties)
    file = open(input_file, 'r')
    reader = vcf.VCFReader(file)
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
            "ALT": ";".join(str(v) for v in record.ALT) if isinstance(record.ALT,list) else record.ALT,
            "AFFECTED_START": record.affected_start,
            "AFFECTED_END": record.affected_end,
            "QUAL": record.QUAL,
            "FILTER": record.FILTER or '.',
            "FORMAT": record.FORMAT or '.',
            "HETEROZIGOSITY": record.heterozygosity,
            "MUTATION": record.var_type,
            "dbSNP": ""
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

        #v = session.run("MATCH (f:File) WHERE f.name={file_id} CREATE (f)-[:Contains]->(v:Variant) SET v = {variant}", {
        #    "file_id": properties["filename"],
        #    "variant": variant
        #    })


        # Creo la relazione File -> Variante
        #session.run("MATCH (f: File), (v: Variant) where ID(f) = {file_id} and ID(v) = {variant_id} create (f)-[:Contains]->(v)", {
        #    "file_id": file_id,
        #    "variant_id": variant_id
        #})
        
        # Costruisco la stringa della lista degli attributi delle annotazioni (sono costretto a farlo perchè non ho un modo univoco per sapere a priori i campi presenti)
        annotation = {
            "info_id": uuid.uuid4()
        }

        #attributes = '{ '

        for (key, value) in record.INFO.items():

            if re.match('(\w*)snp(\w*)', key):
                variant["dbSNP"] = ";".join(str(v) for v in value) if isinstance(value,list) else value
                # session.run("MATCH (v: Variant) where ID(v) = {variant_id} set v += { dbSNP:{dbSNP} }", {
                #    "variant_id": variant_id,
                #    "dbSNP": str(value).strip('[]').split(',')
                #})

                #session.run("MATCH (v: Variant) WHERE v.variant_id={variant_id} SET v += { dbSNP:{dbSNP} }", {
                #    "variant_id": variant["variant_id"],
                #    "dbSNP": str(value).strip('[]').split(',')
                #})

                if variant["dbSNP"] == 'None':
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
            annotation[key] = ";".join(str(v) for v in value) if isinstance(value,list) else value
        

        info_row = []

        for item in info_header:
            info_row.append( annotation[item] if annotation.has_key(item) else "" )
        
        infoWriter.writerow(info_row)
        annotationWriter.writerow( [ variant["variant_id"], annotation["info_id"] ] )
        
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
        #session.run("MATCH (v:Variant) WHERE v.variant_id = {variant_id} create (v)-[:Annotation]->(i: Info) set i = {annotation}", {
        #    "variant_id": variant["variant_id"],
        #   "annotation": annotation
        #})

        # Ricavo i nomi degli attributi dei sample
        format_vars = record.FORMAT.split(':')

        for sample in record.samples:
            
            
            #attributes = '{ sample: "' + sample.sample + '", phased: ' + str(sample.phased) + ', state: ' + str(sample.gt_type) + ', '
            genotype = {
                "genotype_id": uuid.uuid4(),
                "sample": sample.sample,
                "phased": sample.phased,
                "state": sample.gt_type
            }

            for i in range(len(format_vars)): 
                #attributes = attributes + format_vars[i] + ': {' + format_vars[i] + '}, ' 
                genotype[format_vars[i]] = ";".join(str(v) for v in sample.data[i]) if isinstance(sample.data[i],list) else sample.data[i]

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

            #session.run("MATCH (v:Variant) WHERE v.variant_id={variant_id} CREATE (v)-[:Sample]->(g: Genotype) SET g = {genotype}", {
            #    "variant_id": variant["variant_id"],
            #    "genotype": genotype
            #})

            genotype_row = []

            for item in genotype_header:
                genotype_row.append( genotype[item] if genotype.has_key(item) else "" )
        
            genotypeWriter.writerow(genotype_row)
            sampleWriter.writerow( [ variant["variant_id"], genotype["genotype_id"] ] )
        
        variant_row = []

        for item in variant_header:
            variant_row.append( variant[item] )
        
        variantWriter.writerow(variant_row)
        containsWriter.writerow( [ properties["name"], variant["variant_id"] ] )

    #salvo le proprietà calcolate nel nodo
    #session.run("MATCH (f: File) WHERE f.name={filename} SET f += { total:{total}, hom:{hom}, het:{het}, hom_alt:{hom_alt}, uncalled:{uncalled}, snp:{snp}, indels:{indels}, unknown:{unknown}, in_dbSNP:{in_dbSNP}, not_in_dbSNP:{not_in_dbSNP}, in_1000g:{in_1000g}, not_in_1000g:{not_in_1000g} }", #properties)

    file_row = []

    for item in file_header:
        file_row.append(properties[item])

    fileWriter.writerow(file_row)

    file_csv.close()
    variant_csv.close()
    info_csv.close()
    genotype_csv.close()
    contains_csv.close()
    sample_csv.close()
    annotaion_csv.close()

    statements = [
        "CREATE INDEX ON :File(name);",
        "CREATE INDEX ON :Variant(variant_id);",
        "CREATE INDEX ON :Info(info_id);",
        "CREATE INDEX ON :Genotype(genotype_id);",
    ]

    for statement in statements:
        session.run(statement)

    queries = [
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'http://localhost/output-viewer/app/api/file.csv' as line",
            "CREATE (f:File) SET f += line"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'http://localhost/output-viewer/app/api/variant.csv' as line",
            "CREATE (v:Variant) SET v += line"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'http://localhost/output-viewer/app/api/info.csv' as line",
            "CREATE (i:Info) SET i += line"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'http://localhost/output-viewer/app/api/genotype.csv' as line",
            "CREATE (g:Genotype) SET g += line"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'http://localhost/output-viewer/app/api/contains.csv' as line",
            "MATCH (f:File) WHERE f.name = line.name WITH line, f MATCH(v:Variant) WHERE v.variant_id = line.variant_id CREATE (f)-[:Contains]->(v)"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'http://localhost/output-viewer/app/api/annotation.csv' as line",
            "MATCH(v:Variant) WHERE v.variant_id = line.variant_id WITH line, v MATCH(i:Info) WHERE i.info_id = line.info_id CREATE (v)-[:Annotation]->(i)"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'http://localhost/output-viewer/app/api/sample.csv' as line",
            "MATCH(v:Variant) WHERE v.variant_id = line.variant_id WITH line, v MATCH(g:Genotype) WHERE g.genotype_id = line.genotype_id CREATE (v)-[:Sample]->(g)"
        ]
    ]

    # Termino la scrittura dei file (altrimenti non posso caricare i dati su database)
    
    for query in queries:
        session.run( " ".join(query) )

    # Associo il file all'utente
    session.run("MERGE (u:User { username:{username} })", {
        "username": 'lola'
    })

    session.run("MATCH (u:User) WHERE u.username='lola' CREATE (u)-[:Owns]->(f:File { name:{name} })", properties)

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