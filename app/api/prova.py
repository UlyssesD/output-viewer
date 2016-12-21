# !/usr/bin/python   # Script python per il parsing del file caricato in upload su server da elaborare in formato json
# -*- coding: utf-8 -*-

import uuid
import sys
import os
import re
import json
import vcf
import csv
import glob
import pymongo
from pymongo import MongoClient
from neo4j.v1 import GraphDatabase, basic_auth

def main(argv):
    
    
    info_id = 0

    # Ottengo la stringa relativa al file da processare
    input_file = argv[0]
    temp_folder = argv[1]
    username =  argv[2]
    experiment = argv[3]
    species = argv[4]
    
    config = json.load(open('../configuration.json'))
    
    temp_token = username + '_' + str(uuid.uuid4()) 
    part_count = 0
    # File csv per i nodi del grafo
    
    variant_csv = open(temp_folder + temp_token + '_variant.csv', 'w')
    info_csv = open(temp_folder + temp_token + '_info.csv','w')
    genotype_csv = open(temp_folder + temp_token + '_genotype.csv','w')
    
    # File csv per le relazioni del grafo
    of_species_csv = open(temp_folder + temp_token + '_of_species.csv', 'w')
    contains_csv = open(temp_folder + temp_token + '_contains.csv', 'w')
    supported_by_csv = open(temp_folder + temp_token + '_supported_by_' + str(part_count) + '.csv', 'w')
    for_variant_csv = open(temp_folder + temp_token + '_for_variant.csv', 'w')

    # Inizializzo i writer per tutti i file
    
    variantWriter = csv.writer(variant_csv, delimiter=',')
    infoWriter = csv.writer(info_csv, delimiter=',')
    genotypeWriter = csv.writer(genotype_csv, delimiter=',')

    ofSpeciesWriter = csv.writer(of_species_csv, delimiter=',')
    containsWriter = csv.writer(contains_csv, delimiter=',')
    supportedByWriter = csv.writer(supported_by_csv, delimiter=',')
    forVariantWriter = csv.writer(for_variant_csv, delimiter=',')

    
    print 'Starting parsing procedure for file ' + input_file

    print 'Opening .vcf file...'
    file = open(input_file, 'r')
    reader = vcf.VCFReader(file)


    # Costruisco gli header dei nodi
    variant_header = ["variant_id", "CHROM", "POS", "REF", "ALT"]
    genotype_header = ["sample"]

    # Cotruisco gli header delle relazioni
    contains_header = ["name", "info_id"]
    for_variant_header = ["info_id", "variant_id", "START", "END", "ID", "QUAL", "FILTER", "FORMAT", "HETEROZIGOSITY", "MUTATION", "dbSNP"]
    of_species_header = ["sample", "species"]
    
    # Ricavo gli header per formats e info (necessari per avere gli header dei csv rispettivamente di Genotype e Info)
    print 'Retrieving formats and infos...'
    supported_by_header = ["info_id", "sample", "phased", "state"] + reader.formats.keys()
    info_header = ["info_id"]  + reader.infos.keys()

    # supported_by_header = set(["info_id", "sample", "phased", "state"] + reader.formats.keys()) 
    # info_header = set(reader.infos.keys())
    
    genotypes = set()

    #for record in reader:
        


    #    for key in record.INFO.keys():
    #        info_header.add(key)
    #    for key in record.FORMAT.split(':'):
    #        supported_by_header.add(key)

    #file.close()

    # supported_by_header = list(supported_by_header)
    # info_header = list(info_header) + ["info_id"]

    # Scrivo gli header dei nodi nei rispettivi file
    variantWriter.writerow(variant_header)
    genotypeWriter.writerow(genotype_header)
    infoWriter.writerow(info_header)

    # Scrivo gli header delle relazioni nei rispettivi file
    supportedByWriter.writerow(supported_by_header)
    containsWriter.writerow(contains_header)
    ofSpeciesWriter.writerow(of_species_header)
    forVariantWriter.writerow(for_variant_header)

    # Versione che salva le righe del file in GraphDB
    print 'Parsing file...'

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
   
    row_count = 0 # Utilizzato per splittare il file ogni tot righe

    file = open(input_file, 'r')
    reader = vcf.VCFReader(file)
    for record in reader:
        row_count += 1
        # Genero il nodo corrispondente alla variante
        variant = {
            "variant_id": record.CHROM + ':' + str(record.POS) + ':' + record.REF + ':' + ";".join(str(v) for v in record.ALT) if isinstance(record.ALT,list) else record.ALT, # id randomico utilizzato per indicizzare le varianti

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

        # Costruisco la stringa della lista degli attributi delle annotazioni (sono costretto a farlo perchè non ho un modo univoco per sapere a priori i campi presenti)
        annotation = {
            "info_id": uuid.uuid4()
        }



        for (key, value) in record.INFO.items():

            if re.match('(\w*)snp(\w*)', key):
                
                variant["dbSNP"] = ";".join(str(v) for v in value) if isinstance(value,list) else value

                if variant["dbSNP"] == 'None':
                    properties['not_in_dbSNP'] += 1
                else:
                    properties['in_dbSNP'] += 1
            
            if re.match('1000g(\w*)_all', key):
                if value:
                    properties['in_1000g'] += 1
                else:
                    properties['not_in_1000g'] += 1
                

            annotation[key] = ";".join(str(v) for v in value) if isinstance(value,list) else value
        

        info_row = []

        for item in info_header:
            info_row.append( annotation[item] if annotation.has_key(item) else "" )
        
        infoWriter.writerow(info_row)
        containsWriter.writerow( [ properties["name"], annotation["info_id"] ] )
        
        # Ricavo i nomi degli attributi dei sample
        format_vars = record.FORMAT.split(':')

        for sample in record.samples:
            
            genotypes.add(sample.sample)
            #attributes = '{ sample: "' + sample.sample + '", phased: ' + str(sample.phased) + ', state: ' + str(sample.gt_type) + ', '
            genotype = {
                "sample": sample.sample,
                "phased": sample.phased,
                "state" : sample.gt_type or 'None'
            }

            for i in range(len(format_vars)): 
                #attributes = attributes + format_vars[i] + ': {' + format_vars[i] + '}, ' 
                genotype[format_vars[i]] = ";".join(str(v) for v in sample.data[i]) if isinstance(sample.data[i],list) else sample.data[i]


            supported_by_row = [  ]

            for item in supported_by_header:
                if item == "info_id":
                    supported_by_row.append(annotation["info_id"])
                else:
                    supported_by_row.append( genotype[item] if genotype.has_key(item) else "" )
                
            
            supportedByWriter.writerow(supported_by_row)
        
        variant_row = []

        for item in variant_header:
            variant_row.append( variant[item] )
        
        variantWriter.writerow(variant_row)

        for_variant_row = [ annotation["info_id"] ]

        for item in for_variant_header:
             if variant.has_key(item):
                for_variant_row.append( variant[item]) 

        forVariantWriter.writerow(for_variant_row)


        if not (row_count % 15000):
            print str(row_count) + " scanned"
            part_count += 1
            supported_by_csv.close() # Chiudo il file
            supported_by_csv = open(temp_folder + temp_token + '_supported_by_' + str(part_count) + '.csv', 'w') # ne creo uno nuovo
            supportedByWriter = csv.writer(supported_by_csv, delimiter=',') #Riapro il writer
            supportedByWriter.writerow(supported_by_header)





    for item in list(genotypes):
        genotypeWriter.writerow( [ item ] )
        ofSpeciesWriter.writerow( [ item, species ] )

    file.close()

    # Termino la scrittura dei file (altrimenti non posso caricare i dati su database)
    variant_csv.close()
    info_csv.close()
    genotype_csv.close()
    
    of_species_csv.close()
    contains_csv.close()
    supported_by_csv.close()
    for_variant_csv.close()
    
     # Versione che salva le righe del file in Neo4j
    print 'Populating Database...'

    # Connessione a Neo4j
    driver = GraphDatabase.driver("bolt://" + config["neo4j"]["address"], auth=basic_auth(config["neo4j"]["username"], config["neo4j"]["password"]));
    session = driver.session()

    statements = [
        "CREATE INDEX ON :File(name);",
        "CREATE INDEX ON :Species(species);",
        "CREATE INDEX ON :Variant(variant_id);",
        "CREATE INDEX ON :Info(info_id);",
        "CREATE INDEX ON :Genotype(sample);"
    ]

    for statement in statements:
        session.run(statement)

    prova = [
       "MERGE (u:User { username:{username} })",
       "MERGE (e:Experiment { name:{experiment} })",
       "MERGE (s:Species {species: {species} })",
       "MERGE (f:File { name:{properties}.name }) ON CREATE SET f += {properties}",
       "MERGE (u)-[:Created]->(e)",
       "MERGE (e)-[:For_Species]->(s)",
       "MERGE (e)-[:Composed_By]->(f)"
    ]

    # Associo il file all'utente
    session.run(" ".join(prova), {
        "username": username,
        "experiment": experiment,
        "species": species,
        "properties": properties
    })

    
    queries = [
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///" + temp_folder + temp_token + "_variant.csv' as line",
            "MERGE (v:Variant {variant_id: line.variant_id})",
            "ON CREATE SET v += line"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///" + temp_folder +  temp_token + "_info.csv' as line",
            "CREATE (i:Info) SET i += line"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///" + temp_folder +  temp_token + "_genotype.csv' as line",
            "MERGE (g:Genotype {sample: line.sample})"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///" + temp_folder +  temp_token + "_contains.csv' as line",
            "MATCH (f:File) WHERE f.name = line.name WITH line, f",
            "MATCH(i:Info) WHERE i.info_id = line.info_id",
            "CREATE (f)-[:Contains]->(i)"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///" + temp_folder +  temp_token + "_for_variant.csv' as line",
            "MATCH(v:Variant) WHERE v.variant_id = line.variant_id WITH line, v",
            "MATCH(i:Info) WHERE i.info_id = line.info_id",
            "CREATE (i)-[f:For_Variant]->(v) SET f += line"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///" + temp_folder +  temp_token + "_of_species.csv' as line",
            "MATCH(s:Species) WHERE s.species = line.species WITH line, s",
            "MATCH(g:Genotype) WHERE g.sample= line.sample",
            "CREATE (g)-[:Of_Species]->(s)"
        ]
    ]

    
    for query in queries:
        session.run( " ".join(query) )

    print range(part_count + 1)


    for part in range(part_count + 1):
        session.run(" ".join([
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///" + temp_folder +  temp_token + "_supported_by_" +  str(part) + ".csv' as line",
            "MATCH(i:Info) WHERE i.info_id = line.info_id WITH line, i",
            "MATCH(g:Genotype) WHERE g.sample= line.sample",
            "CREATE (i)-[s:Supported_By]->(g) SET s += line"
            ])
        )
    

    # Chiudo la sessione di Neo4j e termino
    session.close()
    print 'Done.'

    # os.remove(input_file)
    # os.remove(temp_folder + temp_token + '_variant.csv')
    # os.remove(temp_folder + temp_token + '_info.csv')
    # os.remove(temp_folder + temp_token + '_genotype.csv')
    # os.remove(temp_folder + temp_token + '_of_species.csv')
    # os.remove(temp_folder + temp_token + '_contains.csv')
    # os.remove(temp_folder + temp_token + '_supported_by.csv')
    # os.remove(temp_folder + temp_token + '_for_variant.csv')


if __name__ == "__main__":
   main(sys.argv[1:])