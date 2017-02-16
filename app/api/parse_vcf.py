# !/usr/bin/env python   # Script python per il parsing di file in formato VCF da inserire in Neo4j
# -*- coding: utf-8 -*-

import uuid
import sys
import os
import re
import json
import vcf
import csv
import glob
import datetime
import strconv

from neo4j.v1 import GraphDatabase, basic_auth


# Queries per il popolamento del database per il file vcf
queries = [
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///{token}_variant.csv' as line",
            "MERGE (v:Variant {variant_id: line.variant_id})",
            "ON CREATE SET v += line"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///{token}_info.csv' as line FIELDTERMINATOR '\t'",
            "CREATE (i:Info {info_id: line.info_id}) SET i += line"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///{token}_genotype.csv' as line",
            "MERGE (g:Genotype {sample: line.sample})"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///{token}_gene.csv' as line",
            "MERGE (g:Gene {gene_id: line.gene_id})"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///{token}_chromosome.csv' as line",
            "MERGE (c:Chromosome {chromosome: line.chromosome})"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///{token}_contains.csv' as line",
            "MATCH (f:File), (i:Info) WHERE f.name = line.name AND i.info_id = line.info_id",
            "CREATE (f)-[:Contains]->(i)"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///{token}_for_variant.csv' as line",
            "MATCH(v:Variant) WHERE v.variant_id = line.variant_id WITH line, v",
            "MATCH(i:Info) WHERE i.info_id = line.info_id",
            "CREATE (i)-[f:For_Variant]->(v) SET f += line"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///{token}_of_species.csv' as line",
            "MATCH(s:Species) WHERE s.species = line.species WITH line, s",
            "MATCH(g:Genotype) WHERE g.sample= line.sample",
            "CREATE (g)-[:Of_Species]->(s)"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///{token}_in_variant.csv' as line",
            "MATCH(v:Variant) WHERE v.variant_id = line.variant_id WITH line, v",
            "MATCH(g:Gene) WHERE g.gene_id = line.gene_id",
            "CREATE (g)-[:In_Variant]->(v)"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///{token}_has_variant.csv' as line",
            "MATCH(v:Variant) WHERE v.variant_id = line.variant_id WITH line, v",
            "MATCH(c:Chromosome) WHERE c.chromosome = line.chromosome",
            "CREATE (c)-[:Has_Variant]->(v)"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///{token}_in_chromosome.csv' as line",
            "MATCH(g:Gene) WHERE g.gene_id = line.gene_id WITH line, g",
            "MATCH(c:Chromosome) WHERE c.chromosome = line.chromosome",
            "MERGE (g)-[:In_Chromosome]->(c)"
        ],
        [
            "USING PERIODIC COMMIT 15000",
            "LOAD CSV WITH HEADERS from 'File:///{token}_supported_by.csv' as line FIELDTERMINATOR '\t'",
            "MATCH(i:Info) WHERE i.info_id = line.info_id WITH line, i",
            "MATCH(g:Genotype) WHERE g.sample= line.sample",
            "CREATE (i)-[s:Supported_By]->(g) SET s += line"
        ]
    ]

def inferType(key, value):


    if isinstance(value,list):
        res = []
        
        for v in value:

            if type(v) is str:
                v = v.decode('string_escape')

            inferred = strconv.infer(v)
            #print 'List - ', key, ': ', inferred

            if (inferred is None) or re.match('^date', inferred):
                res.append(v)
            else:
                res.append(strconv.convert(v))

        #print key, ' result: ', [type(r) for r in res]
        
        res = res[0] if len(res) == 1 else res

    else:

        if type(value) is str:
            value = value.decode('string_escape')

        inferred = strconv.infer(value)
        #print 'Single - ', key, ': ', inferred

        if (inferred is None) or re.match('^date', inferred):
            res = value
        else:
            res = strconv.convert(value)

        #print key, ' result: ', type(res)

    return res


def populateDB(driver, token):
    print 'Populating Database...'

    for query in queries:
        session = driver.session()
        session.run(" ".join(query).replace('{token}', token))
        session.close()


def main(argv):  
    

    # Ottengo la stringa relativa al file da processare
    input_file = argv[0]
    temp_folder = argv[1]
    username =  argv[2]
    experiment = argv[3]
    species = argv[4]
    
    config = json.load(open('../configuration.json'))

    temp_token = username + '_' + str(uuid.uuid4()) 

    
    # Creo i csv per memorizzare le informazioni sui nodi
    variant_csv = open(temp_folder + temp_token + '_variant.csv', 'w')
    info_csv = open(temp_folder + temp_token + '_info.csv','w')
    genotype_csv = open(temp_folder + temp_token + '_genotype.csv','w')
    gene_csv = open(temp_folder + temp_token + '_gene.csv', 'w')
    chromosome_csv = open(temp_folder + temp_token + '_chromosome.csv', 'w')

    # Creo i csv per memorizzare le informazioni sulle relazioni
    of_species_csv = open(temp_folder + temp_token + '_of_species.csv', 'w')
    contains_csv = open(temp_folder + temp_token + '_contains.csv', 'w')
    supported_by_csv = open(temp_folder + temp_token + '_supported_by.csv', 'w')
    for_variant_csv = open(temp_folder + temp_token + '_for_variant.csv', 'w')
    in_variant_csv = open(temp_folder + temp_token + '_in_variant.csv', 'w')
    has_variant_csv = open(temp_folder + temp_token + '_has_variant.csv', 'w')
    in_chromosome_csv = open(temp_folder + temp_token + '_in_chromosome.csv', 'w')

    
    # Inizializzo i writer per tutti i file
    
    # ---- nodi 
    variantWriter = csv.writer(variant_csv, delimiter=',')
    infoWriter = csv.writer(info_csv, delimiter='\t')
    genotypeWriter = csv.writer(genotype_csv, delimiter=',')
    geneWriter = csv.writer(gene_csv, delimiter=',')
    chromosomeWriter = csv.writer(chromosome_csv, delimiter=',')

    # ---- relazioni
    ofSpeciesWriter = csv.writer(of_species_csv, delimiter=',')
    containsWriter = csv.writer(contains_csv, delimiter=',')
    supportedByWriter = csv.writer(supported_by_csv, delimiter='\t')
    forVariantWriter = csv.writer(for_variant_csv, delimiter=',')
    inVariantWriter = csv.writer(in_variant_csv, delimiter=',')
    hasVariantWriter = csv.writer(has_variant_csv, delimiter=',')
    inChromosomeWriter = csv.writer(in_chromosome_csv, delimiter=',')



    # Apro il file vcf
    print 'Opening .vcf file...'
    file = open(input_file, 'r')
    reader = vcf.Reader(file, encoding='utf-8')


    # Costruisco gli header dei file

    # ---- nodi
    variant_header = ["variant_id", "CHROM", "POS", "REF", "ALT", "MUTATION"]
    genotype_header = ["sample"]
    info_header = ["info_id", "DP", "Gene_refGene", "Func_refGene", "QD", "SIFT_score", "otg_all", "NM", "LM", "FS", "MQ0", "attributes"]
    gene_header = ["gene_id"]
    chromosome_header = ["chromosome"]

    # ---- relazioni
    contains_header = ["name", "info_id"]
    for_variant_header = ["info_id", "variant_id", "END", "ID", "QUAL", "FILTER", "FORMAT", "HETEROZIGOSITY", "dbSNP"]
    of_species_header = ["sample", "species"]
    in_variant_header = ["gene_id", "variant_id"]
    has_variant_header = ["chromosome", "variant_id"]
    in_chromosome_header = ["gene_id", "chromosome"]
    supported_by_header = ["info_id", "sample", "phased", "state", "attributes"]
    
    
    # Inizializzo le strutture dati necessarie al parsing (per ottimizzare il caricamento dei dati su database)
    
    # ---- nodi
    genotypes = set()
    genes = set()
    chromosomes = set()


    # Scrivo gli header nei rispettivi file

    # ---- nodi
    variantWriter.writerow(variant_header)
    genotypeWriter.writerow(genotype_header)
    infoWriter.writerow(info_header)
    geneWriter.writerow(gene_header)
    chromosomeWriter.writerow(chromosome_header)    

    # ---- relazioni
    supportedByWriter.writerow(supported_by_header)
    containsWriter.writerow(contains_header)
    ofSpeciesWriter.writerow(of_species_header)
    forVariantWriter.writerow(for_variant_header)
    inVariantWriter.writerow(in_variant_header)
    hasVariantWriter.writerow(has_variant_header)
    inChromosomeWriter.writerow(in_chromosome_header)    

    
    print 'Starting parsing procedure for file ' + input_file

    # Connessione a Neo4j
    driver = GraphDatabase.driver("bolt://" + config["neo4j"]["address"], auth=basic_auth(config["neo4j"]["username"], config["neo4j"]["password"]));
    
    session = driver.session()
    statements = [
        "CREATE INDEX ON :File(name);",
        "CREATE INDEX ON :Species(species);",
        "CREATE INDEX ON :Variant(variant_id);",
        "CREATE INDEX ON :Info(info_id);",
        "CREATE INDEX ON :Genotype(sample);",
        "CREATE INDEX ON :Gene(gene_id);",
        "CREATE INDEX ON :Chromosome(chromosome);"
    ]
    for statement in statements:
        session.run(statement)
    session.close()


    # Creo un nodo corrispondente al file
    properties = {
        "name": os.path.basename(file.name),
        "extension": os.path.splitext(input_file)[1]
    }
    
    statistics = {
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

    # ---- comincio creando i primi nodi di riferimento
    session = driver.session()

    prova = [
       "MERGE (u:User { username:{username} })",
       "MERGE (e:Experiment { name:{experiment} })",
       "MERGE (s:Species {species: {species} })",
       "CREATE (f:File { name:{properties}.name }) SET f.extension = {properties}.extension",
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

    session.close()

    # inizializzo un contatore per fare un load parziale del file su database per file troppo grandi
    row_count = 0 

    for record in reader:
        
        row_count += 1
        
        # Genero il nodo corrispondente alla variante
        variant = {
            "variant_id": record.CHROM + ':' + str(record.POS) + ':' + record.REF + ':' + ";".join(str(v) for v in record.ALT) if isinstance(record.ALT,list) else record.ALT, # id randomico utilizzato per indicizzare le varianti

            "CHROM": record.CHROM,
            "POS": record.POS,
            #"START": record.start,
            "END": record.end,
            "ID": record.ID or '.',
            "REF": record.REF,
            "ALT": ";".join(str(v) for v in record.ALT) if isinstance(record.ALT,list) else record.ALT,
            #"AFFECTED_START": record.affected_start,
            #"AFFECTED_END": record.affected_end,
            "QUAL": record.QUAL,
            "FILTER": record.FILTER or 'PASS',
            "FORMAT": record.FORMAT or '.',
            "HETEROZIGOSITY": record.heterozygosity,
            "MUTATION": record.var_type,
            "dbSNP": ""
        }

        
        # Aggiorno le statistiche sul file
        statistics["total"] += 1
        statistics["hom"] += record.num_hom_ref
        statistics["het"] += record.num_het
        statistics["hom_alt"] += record.num_hom_alt
        statistics["uncalled"] += record.num_unknown

        if variant["MUTATION"] == 'snp':
            statistics["snp"] += 1
        elif variant["MUTATION"]== 'indel':
            statistics["indels"] += 1
        else:
            statistics["unknown"] += 1


        # Costruisco la stringa della lista degli attributi delle annotazioni (sono costretto a farlo perchè non ho un modo univoco per sapere a priori i campi presenti)
        annotation = {
            "info_id": uuid.uuid4(),
            "DP": "",
            "Gene.refGene": "",
            "Func.refgene": "",
            "otg_all": "",
            "QD": "",
            "NM": "",
            "LM": "",
            "FS": "",
            "MQ0": "",
            "SIFT_score": "",
            "attributes": {}
        }


        for (key, value) in record.INFO.items():

            if re.match('(\w*)snp(\w*)', key):
                
                variant["dbSNP"] = ";".join(str(v) for v in value) if isinstance(value,list) else value
                variant["ID"] = ";".join(str(v) for v in value) if isinstance(value,list) else value
                
                if variant["dbSNP"] == 'None':
                    statistics['not_in_dbSNP'] += 1
                else:
                    statistics['in_dbSNP'] += 1
            
            if re.match('1000g(\w*)_all', key):
                
                if value:
                    annotation['otg_all'] = value
                    statistics['in_1000g'] += 1
                else:
                    statistics['not_in_1000g'] += 1
                

            #annotation["attributes"] += key + "=" + ( ";".join(str(v) for v in value) if isinstance(value,list) else str(value) ) + ","
            #annotation["attributes"][key] = value[0] if isinstance(value,list) and len(value) == 1 else value
            if key.replace(".", "_") in info_header:
                if key == "LM":
                    annotation[key] = inferType(key, value[0].split('_'))
                else:
                    annotation[key] = inferType(key, value)
            else:
                annotation["attributes"][key] = inferType(key, value)
            #if isinstance(value, list):
            #    for v in value:
            #        inferType(key, v)
            #else:
            #    inferType(key, value)


        # rimuovo la virgola in eccesso alla fine della stringa di attributi
        #annotation["attributes"] = annotation["attributes"].rstrip(',')

        # trasformo il dictionary ottenuto in formato json (serve per neomodel)
        annotation["attributes"] = json.dumps(annotation["attributes"])

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
                #"state" : sample.gt_type or 'None',
                "attributes": {}
            }

            if not sample.gt_type:
                genotype["state"] = "None"
            elif sample.gt_type == 0:
                genotype["state"] = "hom_ref"
            elif sample.gt_type == 1:
                genotype["state"] = "hom_alt"
            elif sample.gt_type == 2:
                genotype["state"] = "het"

                

            for i in range(len(format_vars)): 
                #attributes = attributes + format_vars[i] + ': {' + format_vars[i] + '}, ' 
                #genotype["attributes"] += format_vars[i] + "=" + (";".join(str(v) for v in sample.data[i]) if isinstance(sample.data[i],list) else str(sample.data[i]) ) + ","
                #genotype["attributes"][format_vars[i]] = sample.data[i][0] if isinstance(sample.data[i],list) and len(sample.data[i]) == 1 else sample.data[i]
                genotype["attributes"][format_vars[i]] = inferType(format_vars[i], sample.data[i])

            #genotype["attributes"] = genotype["attributes"].rstrip(',')

            genotype["attributes"] = json.dumps(genotype["attributes"])

            supported_by_row = []

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


        # Aggiungo cromosomi e geni (e relative relazioni)
        chromosomes.add(record.CHROM)
        hasVariantWriter.writerow([ record.CHROM, variant["variant_id"] ])

        if record.INFO.has_key('Gene.refGene'):
            for g in record.INFO['Gene.refGene']:
                if not (g == 'NONE'):
                    genes.add(g)
                    inChromosomeWriter.writerow([ g, record.CHROM ])
                    inVariantWriter.writerow([ g, variant["variant_id"] ])
                

        sys.stdout.write("%d lines scanned %s"%(row_count,"\r"))
        sys.stdout.flush();

        if not (row_count % 15000):

            print ""

            for item in list(genes):
                geneWriter.writerow([ item ])
        
            for item in list(chromosomes):
                chromosomeWriter.writerow([ item ])
        

            for item in list(genotypes):
                genotypeWriter.writerow( [ item ] )
                ofSpeciesWriter.writerow( [ item, species ] )
            
            variant_csv.close()
            info_csv.close()
            genotype_csv.close()
            gene_csv.close()
            chromosome_csv.close()
            
            of_species_csv.close()
            contains_csv.close()
            supported_by_csv.close()
            for_variant_csv.close()
            in_variant_csv.close()
            has_variant_csv.close()
            in_chromosome_csv.close()
            
            populateDB(driver, temp_folder + temp_token)

            # Creo i csv per memorizzare le informazioni sui nodi
            variant_csv = open(temp_folder + temp_token + '_variant.csv', 'w')
            info_csv = open(temp_folder + temp_token + '_info.csv','w')
            genotype_csv = open(temp_folder + temp_token + '_genotype.csv','w')
            gene_csv = open(temp_folder + temp_token + '_gene.csv', 'w')
            chromosome_csv = open(temp_folder + temp_token + '_chromosome.csv', 'w')

            # Creo i csv per memorizzare le informazioni sulle relazioni
            of_species_csv = open(temp_folder + temp_token + '_of_species.csv', 'w')
            contains_csv = open(temp_folder + temp_token + '_contains.csv', 'w')
            supported_by_csv = open(temp_folder + temp_token + '_supported_by.csv', 'w')
            for_variant_csv = open(temp_folder + temp_token + '_for_variant.csv', 'w')
            in_variant_csv = open(temp_folder + temp_token + '_in_variant.csv', 'w')
            has_variant_csv = open(temp_folder + temp_token + '_has_variant.csv', 'w')
            in_chromosome_csv = open(temp_folder + temp_token + '_in_chromosome.csv', 'w')

        
            # Inizializzo i writer per tutti i file
            
            # ---- nodi 
            variantWriter = csv.writer(variant_csv, delimiter=',')
            infoWriter = csv.writer(info_csv, delimiter='\t')
            genotypeWriter = csv.writer(genotype_csv, delimiter=',')
            geneWriter = csv.writer(gene_csv, delimiter=',')
            chromosomeWriter = csv.writer(chromosome_csv, delimiter=',')
    
            # ---- relazioni
            ofSpeciesWriter = csv.writer(of_species_csv, delimiter=',')
            containsWriter = csv.writer(contains_csv, delimiter=',')
            supportedByWriter = csv.writer(supported_by_csv, delimiter='\t')
            forVariantWriter = csv.writer(for_variant_csv, delimiter=',')
            inVariantWriter = csv.writer(in_variant_csv, delimiter=',')
            hasVariantWriter = csv.writer(has_variant_csv, delimiter=',')
            inChromosomeWriter = csv.writer(in_chromosome_csv, delimiter=',')

            # Scrivo gli header nei rispettivi file
        
            # ---- nodi
            variantWriter.writerow(variant_header)
            genotypeWriter.writerow(genotype_header)
            infoWriter.writerow(info_header)
            geneWriter.writerow(gene_header)
            chromosomeWriter.writerow(chromosome_header)    
        
            # ---- relazioni
            supportedByWriter.writerow(supported_by_header)
            containsWriter.writerow(contains_header)
            ofSpeciesWriter.writerow(of_species_header)
            forVariantWriter.writerow(for_variant_header)
            inVariantWriter.writerow(in_variant_header)
            hasVariantWriter.writerow(has_variant_header)
            inChromosomeWriter.writerow(in_chromosome_header)
            
            # session = driver.session()
            # session.run(" ".join([
            #         "USING PERIODIC COMMIT 15000",
            #         "LOAD CSV WITH HEADERS from 'File:///" + temp_folder +  temp_token + "_supported_by.csv' as line",
            #         "MERGE (i:Info {info_id: line.info_id}) WITH line, i",
            #         "MERGE (g:Genotype {sample: line.sample}) WITH line, i, g",
            #         "CREATE (i)-[s:Supported_By]->(g) SET s += line"
            #     ]))
            # session.close()    

            # supported_by_csv = open(temp_folder + temp_token + '_supported_by.csv', 'w')
            # supportedByWriter = csv.writer(supported_by_csv, delimiter=',') #Riapro il writer
            # supportedByWriter.writerow(supported_by_header)

    print ""

    for item in list(genes):
        geneWriter.writerow([ item ])
        
    for item in list(chromosomes):
        chromosomeWriter.writerow([ item ])
        

    for item in list(genotypes):
        genotypeWriter.writerow( [ item ] )
        ofSpeciesWriter.writerow( [ item, species ] )

    file.close()

    # Termino la scrittura dei file (altrimenti non posso caricare i dati su database)
    variant_csv.close()
    info_csv.close()
    genotype_csv.close()
    gene_csv.close()
    chromosome_csv.close()
    
    of_species_csv.close()
    contains_csv.close()
    supported_by_csv.close()
    for_variant_csv.close()
    in_variant_csv.close()
    has_variant_csv.close()
    in_chromosome_csv.close()
    

    
    session = driver.session()

    prova = [
       "MATCH (u:User { username: {username} })-[:Created]->(e:Experiment { name:{experiment} })-[:Composed_By]->(f:File { name:{properties}.name })",
       "SET f.statistics =  {statistics}"
    ]

    # Associo il file all'utente
    session.run(" ".join(prova), {
        "username": username,
        "experiment": experiment,
        "species": species,
        "properties": properties,
        "statistics": json.dumps(statistics)
    })

    session.close()
    
    
    populateDB(driver, temp_folder + temp_token)

    # os.remove(input_file)
    os.remove(temp_folder + temp_token + '_variant.csv')
    os.remove(temp_folder + temp_token + '_info.csv')
    os.remove(temp_folder + temp_token + '_genotype.csv')
    os.remove(temp_folder + temp_token + '_gene.csv')
    os.remove(temp_folder + temp_token + '_chromosome.csv')
    os.remove(temp_folder + temp_token + '_of_species.csv')
    os.remove(temp_folder + temp_token + '_contains.csv')
    os.remove(temp_folder +  temp_token + "_supported_by.csv")
    #for part in range(part_count + 1):
    #    os.remove(temp_folder +  temp_token + "_supported_by_" +  str(part) + ".csv")
    
    os.remove(temp_folder + temp_token + '_for_variant.csv')
    os.remove(temp_folder + temp_token + '_in_variant.csv')
    os.remove(temp_folder + temp_token + '_has_variant.csv')
    os.remove(temp_folder + temp_token + '_in_chromosome.csv')
    
   
    print 'Done.'

if __name__ == "__main__":
   main(sys.argv[1:])
