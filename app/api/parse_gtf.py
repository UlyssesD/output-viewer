# !/usr/bin/env python   # Script python per il parsing di file in formato GTF da inserire in Neo4j

import uuid
import sys
import os
import re
import json
import csv
import GTF
import glob
from neo4j.v1 import GraphDatabase, basic_auth

# Queries per il popolamento del database per il file vcf
queries = [
    [
        "USING PERIODIC COMMIT 15000",
        "LOAD CSV WITH HEADERS from 'File:///{token}_chromosome.csv' as line",
        "MERGE (c:Chromosome {chromosome: line.chromosome})"
    ],
    [
        "USING PERIODIC COMMIT 15000",
        "LOAD CSV WITH HEADERS from 'File:///{token}_gene.csv' as line",
        "MERGE (g:Gene {gene_id: line.gene_id})"
    ],
    [
        "USING PERIODIC COMMIT 15000",
        "LOAD CSV WITH HEADERS from 'File:///{token}_transcript.csv' as line",
        "MERGE (t:Transcript {transcript_id: line.transcript_id})",
        "ON CREATE SET t += line"
    ],
    [
        "USING PERIODIC COMMIT 15000",
        "LOAD CSV WITH HEADERS from 'File:///{token}_exon.csv' as line",
        "MERGE (e:Exon {exon_id: line.exon_id})",
        "ON CREATE SET e += line"
    ],
    [
        "USING PERIODIC COMMIT 15000",
        "LOAD CSV WITH HEADERS from 'File:///{token}_contains.csv' as line",
        "MATCH (f:File) WHERE f.name = line.name WITH line, f",
        "MATCH(g:Gene) WHERE g.gene_id = line.gene_id",
        "CREATE (f)-[:Contains]->(g)"
    ],
    [
        "USING PERIODIC COMMIT 15000",
        "LOAD CSV WITH HEADERS from 'File:///{token}_in_chromosome.csv' as line",
        "MATCH (c:Chromosome) WHERE c.chromosome = line.chromosome WITH line, c",
        "MATCH(g:Gene) WHERE g.gene_id = line.gene_id",
        "CREATE (g)-[:In_Chromosome]->(c)"
    ],
    [
        "USING PERIODIC COMMIT 15000",
        "LOAD CSV WITH HEADERS from 'File:///{token}_has_transcript.csv' as line",
        "MATCH (t:Transcript) WHERE t.transcript_id = line.transcript_id WITH line, t",
        "MATCH(g:Gene) WHERE g.gene_id = line.gene_id",
        "CREATE (g)-[h:Has_Transcript]->(t)",
        "SET h += {strand: line.strand}"
    ],
    [
        "USING PERIODIC COMMIT 15000",
        "LOAD CSV WITH HEADERS from 'File:///{token}_has_exon.csv' as line",
        "MATCH (t:Transcript) WHERE t.transcript_id = line.transcript_id WITH line, t",
        "MATCH(e:Exon) WHERE e.exon_id = line.exon_id",
        "CREATE (t)-[:Has_Exon]->(e)"
    ]
]



def populateDB(driver, token):

    for query in queries:
        session = driver.session()
        session.run(" ".join(query).replace('{token}', token))
        session.close()
    
    # rimuovo i file temporanei

    # ---- nodi
    # os.remove( token + '_chromosome.csv' )
    # os.remove( token + '_gene.csv' )
    # os.remove( token + '_transcript.csv' )
    # os.remove( token + '_exon.csv' )

    # ---- relazioni
    # os.remove( token + '_contains.csv' )
    # os.remove( token + '_in_chromosome.csv' )
    # os.remove( token + '_has_transcript.csv' )
    # os.remove( token + '_has_exon.csv' )



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
    chromosome_csv = open(temp_folder + temp_token + '_chromosome.csv', 'w')
    gene_csv = open(temp_folder + temp_token + '_gene.csv', 'w')
    transcript_csv = open(temp_folder + temp_token + '_transcript.csv', 'w')
    exon_csv = open(temp_folder + temp_token + '_exon.csv', 'w')

    # Creo i csv per memorizzare le informazioni sulle relazioni
    contains_csv = open(temp_folder + temp_token + '_contains.csv', 'w')
    in_chromosome_csv = open(temp_folder + temp_token + '_in_chromosome.csv', 'w')    
    has_transcript_csv = open(temp_folder + temp_token + '_has_transcript.csv', 'w')
    has_exon_csv = open(temp_folder + temp_token + '_has_exon.csv', 'w')

    # Inizializzo i writer per tutti i file

    # ---- nodi
    chromosomeWriter = csv.writer(chromosome_csv, delimiter=',')
    geneWriter = csv.writer(gene_csv, delimiter=',')
    transcriptWriter = csv.writer(transcript_csv, delimiter=',')
    exonWriter = csv.writer(exon_csv, delimiter=',')

    # ---- relazioni
    containsWriter = csv.writer(contains_csv, delimiter=',')
    inChromosomeWriter = csv.writer(in_chromosome_csv, delimiter=',')
    hasTranscriptWriter = csv.writer(has_transcript_csv, delimiter=',')
    hasExonWriter = csv.writer(has_exon_csv, delimiter=',')

    # Cotruisco gli header dei file

    # ---- nodi
    chromosome_header = ["chromosome"]
    gene_header = ["gene_id"]
    transcript_header = ["transcript_id", "reference_id", "cov", "FPKM", "TPM", "start", "end"]
    exon_header = ["exon_id", "exon_number", "start", "end", "cov"]  

    # ---- relazioni
    contains_header = ["name", "gene_id"]
    in_chromosome_header = ["gene_id", "chromosome"]
    has_transcript_header = ["gene_id", "strand", "transcript_id"]
    has_exon_header = ["transcript_id", "exon_id"]


    # Scrivo gli header nei rispettivi file

    # ---- nodi
    chromosomeWriter.writerow(chromosome_header)
    geneWriter.writerow(gene_header)
    transcriptWriter.writerow(transcript_header)
    exonWriter.writerow(exon_header)

    # ---- relazioni
    containsWriter.writerow(contains_header)
    inChromosomeWriter.writerow(in_chromosome_header)
    hasTranscriptWriter.writerow(has_transcript_header)
    hasExonWriter.writerow(has_exon_header)

    # Inizializzo le strutture dati necessarie al parsing (per ottimizzare il caricamento dei dati su database)

    # ---- nodi
    chromosomes = set()
    genes_dict = {}
    transcripts_dict = {}

    # ---- relazioni
    contains_dict = {}
    in_chromosome_dict = {}
    has_transcript_dict = {}


    print 'Starting parsing procedure for file ' + input_file    
    properties = {
        "name": os.path.basename(input_file),
        "extension": os.path.splitext(input_file)[1]
    }

    # Connessione a Neo4j
    driver = GraphDatabase.driver("bolt://" + config["neo4j"]["address"], auth=basic_auth(config["neo4j"]["username"], config["neo4j"]["password"]));


    # Inizializzazione degli indici
    session = driver.session()

    statements = [
        "CREATE INDEX ON :File(name);",
        "CREATE INDEX ON :Species(species);",
        "CREATE INDEX ON :Gene(gene_id);",
        "CREATE INDEX ON :Chromosome(chromosome);",
        "CREATE INDEX ON :Transcript(transcript_id);",
        "CREATE INDEX ON :Exon(exon_id);"
    ]

    for statement in statements:
        session.run(statement)

    session.close()


    # Versione che salva le righe del file in GraphDB
    print 'Parsing file...'

    # inizializzo un contatore per fare un load parziale del file su database per file troppo grandi
    row_count = 0

    for line in GTF.lines(input_file):
        row_count += 1
       
        # memorizzo il cromosoma
        chromosomes.add(line["seqname"])

        # memorizzo il gene (se non presente)
        if not genes_dict.has_key(line["gene_id"]):
            genes_dict[ line["gene_id"] ] = [ line[attr] if line.has_key(attr) else "None" for attr in gene_header ]

        # memorizzo la relazione (file)-[contiene]->(gene) (se non esiste)
        if not contains_dict.has_key(properties["name"] + ':' + line["gene_id"]):
            contains_dict[ properties["name"] + ':' + line["gene_id"] ] = [ properties["name"], line["gene_id"] ]
        
        # memorizzo la relazione (gene)-[contenuto in]->(cromosoma) (se non esiste)
        if not in_chromosome_dict.has_key(line["gene_id"] + ':' + line["seqname"]):
            in_chromosome_dict[ line["gene_id"] + ':' + line["seqname"] ] = [  line["gene_id"], line["seqname"]  ]

        # a seconda della feature considerata (transcript, exon) memorizzo opportunamente le informazioni della riga
        if line['feature'] == 'transcript':
            
            # memorizzo il trascritto (se non presente)
            if not transcripts_dict.has_key(line["transcript_id"]):
                transcripts_dict[ line["transcript_id"] ] = [ line[attr] if line.has_key(attr) else "None" for attr in transcript_header ]

            # memorizzo la relazione (gene)-[contiente]->(trascritto) (se non esiste)
            if not has_transcript_dict.has_key( line["gene_id"] + ':' + line["transcript_id"] ):
                has_transcript_dict[ line["gene_id"] + ':' + line["transcript_id"] ] = [  line[attr] for attr in has_transcript_header  ]

        elif line['feature'] == 'exon':
            #definisco un ID per l'esone (necessario per il popolamento su db)
            exon_id = line["exon_number"] + ':' + line["transcript_id"]

            # memorizzo l'esone nel file csv
            exonWriter.writerow([ exon_id ] + [ line[attr] if line.has_key(attr) else "None" for attr in exon_header[1:] ])

            #memorizzo la relazione (trascritto)-[contiene]->(esone) nel file csv
            hasExonWriter.writerow([ line["transcript_id"], exon_id ]) 
        
        if not (row_count % 15000):
            print str(row_count) + " scanned"


    # scrivo i file csv dei dict creati in precedenza
    for chrom in list(chromosomes):
        chromosomeWriter.writerow([ chrom ])
    
    for gene in genes_dict.keys():
        geneWriter.writerow( genes_dict[gene] )
    
    for transcript in transcripts_dict.keys():
        transcriptWriter.writerow( transcripts_dict[transcript] )
    
    for entry in contains_dict.keys():
        containsWriter.writerow( contains_dict[entry] )
    
    for entry in in_chromosome_dict.keys():
        inChromosomeWriter.writerow( in_chromosome_dict[entry] )
    
    for entry in has_transcript_dict.keys():
        hasTranscriptWriter.writerow( has_transcript_dict[entry] )
    
    # termino la scrittura dei file csv
    
    # ---- nodi
    chromosome_csv.close()
    gene_csv.close()
    transcript_csv.close()
    exon_csv.close()

    # ---- relazioni
    contains_csv.close()
    in_chromosome_csv.close()
    has_transcript_csv.close()
    has_exon_csv.close()


    print 'Populating Database...'
    session = driver.session()

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

    session.close()

    populateDB(driver, temp_folder + temp_token)

    print 'Done.'

if __name__ == "__main__":
   main(sys.argv[1:])