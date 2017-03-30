# !/usr/bin/env python   # Script python per il parsing di file in formato VCF da inserire in Neo4j
# -*- coding: utf-8 -*-

import pandas as pd
import re
import csv
import gzip
import uuid
import sys, os


# ---- VARIABILI GLOBALI

ROWS = []						# memorizza le righe del file vcf
SAMPLES = []					# tiene traccia dei campioni presenti nel file

HEADERS = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'FORMAT']			# utilizzato per memorizzare le colonne del file finale
DICTIONARY = {}					# utilizzato per memorizzare i valori dei campi stringa del file (utile lato client per generare le select e le autocomplete)
TYPES = {}						# utilizzato per memorizzare i tipi dei campi presenti nel file (utile lato client per la generazione dei form)



# ----- Funzioni ausiliarie -----
def addType(key, type):

	if not TYPES.has_key(key):
		TYPES[key] = type


def addEntryToDict(key, value):

	if not DICTIONARY.has_key(key):
		DICTIONARY[key] = set([value])
	else:
		DICTIONARY[key].update([value])


def inferType(key, array):
	
	for i in range(len(array)):

		if re.match('^(\d)+\.(\d)+$', array[i].strip()):
			
			addType(key, "float")
			array[i] = float(array[i].strip())

		elif re.match('^(\d)+$', array[i].strip()):
			
			addType(key, "int")
			array[i] = int(array[i].strip())

		else:
			addType(key, "string")
			addEntryToDict(key, array[i])




	return array

def main(argv):  
    

    # ---- ricavo le informazioni dalla riga di comando
    input_file = argv[0] 	# ---- nome del file vcf di input
    temp_folder = argv[1]	# ---- cartella temporanea per memorizzare i csv parziali
    data_folder = argv[2]	# ---- cartella dove memorizzare il file csv finale
    username =  argv[3]		# ---- nome utente del proprietario del file
    experiment = argv[4]	# ---- esperimento a cui il file appartiene
    species = argv[5]		# ---- specie del file passato in input

    # ---- Apro il file vcf
    print 'Opening .vcf file...'
    file = open(input_file, 'r')
    
    #reader = vcf.Reader(file, encoding='utf-8')

    
    print 'Starting parsing procedure for file ' + os.path.basename(file.name)


    row_count = 0 

    # ---- aggiungo i tipi per i valori fissi del file
    for entry in [("CHROM", "string"), ("POS", "int"), ("ID", "string"), ("REF", "string"), ("ALT", "string"), ("QUAL", "float"), ("FILTER", "string"), ("FORMAT", "string")]:
    	addType(entry[0], entry[1])

    print "Scanning headers of output file"

    # ---- leggo una prima volta il file per intero per calcolare tutti gli header del file csv finale
    for line in iter(file):
    	# ---- salto gli header del file
    	if re.match("^##.*", line):
    		print "IGNORING LINE"
    		continue
    	
    	if re.match("^#CHROM\t", line):
    		print "HEADER OF VCF FILE"

    		SAMPLES = line.strip('#').split('\t')[9:]
    		print SAMPLES, "length:", len(SAMPLES)
    		continue

    	row_count += 1

    	# ---- comincio a parsare le informazioni della riga
    	values = line.split('\t')

    	# ---- ottengo la lista delle annotazioni della riga
    	annotations = values[7].split(';')

    	for element in annotations:

    		# ---- divido ogni annotazione come una coppia chiave - valore
    		key, value = (element.split('=') + [None]*2)[:2]

    		if key not in HEADERS:
    			HEADERS.append(key)
    			
    	sys.stdout.write("%d lines scanned %s"%(row_count,"\r"))
        sys.stdout.flush();


    sys.stdout.write("%d lines scanned %s"%(row_count,"\n"))
    sys.stdout.flush();
    
    print "HEADERS:", HEADERS 
    print "Processing lines of file..."

    file = open(input_file,'r')
    output = gzip.open(data_folder + username + "_" + experiment + "_" + os.path.basename(file.name) + ".data.gz", "wb")
    writer = csv.DictWriter(output, HEADERS, dialect='excel-tab')

    writer.writeheader()

    row_count = 0
    for line in iter(file):

    	# ---- salto gli header del file
    	if re.match("^##.*", line):
    		#print "IGNORING LINE"
    		continue
    	
    	if re.match("^#CHROM\t", line):
    		#print "HEADER OF VCF FILE"

    		SAMPLES = line.strip('#').split('\t')[9:]
    		print SAMPLES, "length:", len(SAMPLES)
    		continue


    	row_count += 1

    	# ---- comincio a parsare le informazioni della riga
    	values = line.split('\t')

    	# ---- comincio a memorizzare le informazioni fisse del file
    	row = {
    		"CHROM": values[0],
    		"POS": int(values[1]),
    		"ID": values[2],
    		"REF": values[3],
    		"ALT": values[4].split(','),
    		"QUAL": float(values[5]) if not values[5] == '.' else None,
    		"FILTER": values[6],
    		"FORMAT": values[8],
    	}

    	for entry in ["CHROM", "REF"]:
    		addEntryToDict(entry, row[entry])

    	# ---- ottengo la lista delle annotazioni della riga
    	annotations = values[7].split(';')

    	for element in annotations:
    		#print element
    		# ---- divido ogni annotazione come una coppia chiave - valore
    		key, value = (element.split('=') + [None]*2)[:2]

    		# ---- se un valore è presente considero il caso sia vuoto ('.'), oppure se è formato da una lista di elementi (',' oppure '_')
    		if value:
    			value = str(value.decode('string_escape'))

    			if value == '.':
    				#print key + ': None'
    				row[key] = None
    			else:
    				converted = inferType(key, value.replace(" ", "").replace('_', ',').replace(';',',').split(','))

    				#print key + ':', strconv.convert_series(value.replace('_', ',').split(','))
    				row[key] = converted if len(converted) > 1 else converted[0]
    			
    		else:
    			#print key + ': True'
    			addType(key, "boolean")
    			row[key] = True

    	#print row
    	writer.writerow(row)

    #	ROWS.append(row)

    	sys.stdout.write("%d lines scanned %s"%(row_count,"\r"))
        sys.stdout.flush();

    #    if not (row_count % 100000):

    #        print ""
            
    #        dataframe = pd.DataFrame(ROWS)
            
    #        dataframe.to_csv( data_folder + username + "_" + experiment + "_" + os.path.basename(file.name) + ".data.gz", sep="\t", index=False, compression="gzip", mode='a')
           
    #        del ROWS[:]

    output.close()
    # ---- costruisco il dataframe con pandas
    #dataframe = pd.DataFrame(data=ROWS, columns=CSV_HEADERS)
    #dataframe = pd.DataFrame(ROWS)
    
    # ---- memorizzo il risultato in un file csv
    #dataframe.to_csv( data_folder + username + "_" + experiment + "_" + os.path.basename(file.name) + ".data.gz", sep="\t", index=False, compression="gzip", mode='a')

 
    # ---- costrisco il dataframe dei tipi
    key_types = pd.DataFrame.from_dict(TYPES, orient="index")

    key_types.to_csv( data_folder + username + "_" + experiment + "_" + os.path.basename(file.name) + ".types.data.gz", sep="\t", index_label="Key", header=["Type"], compression="gzip")

    # ---- costruisco il dataframe dei valori
    dict_values = pd.DataFrame.from_dict(DICTIONARY, orient="index")

    dict_values.to_csv( data_folder + username + "_" + experiment + "_" + os.path.basename(file.name) + ".dictionary.data.gz", sep="\t", index_label="Key", compression="gzip")


    #print dataframe.dtypes


if __name__ == "__main__":
   main(sys.argv[1:])