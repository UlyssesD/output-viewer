# !/usr/bin/env python   # Script python per il parsing di file in formato VCF da inserire in Neo4j
# -*- coding: utf-8 -*-

import pandas as pd
import re
import csv
import gzip
import uuid
import sys, os
import multiprocessing


def worker(lines):
    """Make a dict out of the parsed, supplied lines"""
    result = {}
    #print lines
    for line in lines.split('\n'):
        print line
        
    return result

def test(line):
    print line

def main(argv):  
    

    # ---- ricavo le informazioni dalla riga di comando
    input_file = argv[0] 	# ---- nome del file vcf di input
    temp_folder = argv[1]	# ---- cartella temporanea per memorizzare i csv parziali
    data_folder = argv[2]	# ---- cartella dove memorizzare il file csv finale
    username =  argv[3]		# ---- nome utente del proprietario del file
    experiment = argv[4]	# ---- esperimento a cui il file appartiene
    species = argv[5]		# ---- specie del file passato in input

    numthreads = 8
    numlines = 1000

    # ---- Apro il file vcf
    print 'Opening .vcf file...'
    #lines = open(input_file, 'r').readlines()

    #for line in iter(file):
    # create the process pool
    pool = multiprocessing.Pool(processes=numthreads)

    # map the list of lines into a list of result dicts
    #result_list = pool.map(worker, 
    #    (lines[line:line+numlines] for line in xrange(0,len(lines),numlines) ) )

    file = open(input_file,'r')
    row_count = 0
    
    pool.map(lambda line: test(line), line for line in iter(file))


    # reduce the result dicts into a single dict
    result = {}
    map(result.update, result_list)
    

if __name__ == "__main__":
   main(sys.argv[1:])