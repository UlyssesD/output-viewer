# !/usr/bin/env python   # Script python per il parsing di file in formato VCF da inserire in Neo4j
# -*- coding: utf-8 -*-

import pandas as pd
import strconv
import re
import vcf
import uuid
import sys, os


# ---- VARIABILI GLOBALI
CSV_HEADERS = [
				"CHROM", "ID", "POS", "END", "REF", "ALT", "MUTATION", "QUAL", "FILTER", "FORMAT",
				"HETEROZIGOSITY", "dbSNP", "DP", "gene_refGene", "func_refGene", "QD", "sift_score",
				"otg_all", "NM", "LM", "FS", "MQ0", "genotypes_state"
			]

ROWS = []


def inferType(value):


    if isinstance(value,list):
        res = []
        
        for v in value:

            if type(v) is str:
                v = str(v.decode('string_escape'))

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
            value = str(value.decode('string_escape'))

        inferred = strconv.infer(value)
        #print 'Single - ', key, ': ', inferred

        if (inferred is None) or re.match('^date', inferred):
            res = value
        else:
            res = strconv.convert(value)

        #print key, ' result: ', type(res)

    return res


def getAnnotationOrNone(record, label, default=None):

	return inferType(record.INFO[label]) if record.INFO.has_key(label) else default


def matchExp(record, searchExp, default=None):

	r = re.compile(searchExp)

	search_results = filter(r.match, record.INFO.keys())

	if search_results:
		return getAnnotationOrNone(record, search_results[0], default)
	else:
		return None


def getSampleState(state):

	if state == None:
		return "uncalled"
	elif state == 0:
		return "hom_ref"
	elif state == 1:
		return "hom_alt"
	elif state == 2:
		return "het"



def constructStateColumn(samples, headers):

	header = ["sample", "phased", "state"] + headers
	rows = []

	rows.append(getSampleState(sample.gt_type) for sample in samples)
	

	return  [ getSampleState(sample.gt_type) for sample in samples ]

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
    reader = vcf.Reader(file, encoding='utf-8')

    
    print 'Starting parsing procedure for file ' + os.path.basename(file.name)


    row_count = 0 

    for record in reader:

    	row_count += 1

    	# row = (
    	# 		record.CHROM, record.ID or None, record.POS, record.end, record.REF, record.ALT, record.var_type, record.QUAL, record.FILTER or "PASS", record.FORMAT,
    	# 		record.heterozygosity, matchExp(record, '(\w*)snp(\w*)'), int(getAnnotationOrNone(record, "DP", 0)), getAnnotationOrNone(record, "Gene.refGene"), 
    	# 		getAnnotationOrNone(record, "Func.refGene"), getAnnotationOrNone(record, "QD", None), getAnnotationOrNone(record, "SIFT_score", None), 
    	# 		matchExp(record, '1000g(\w*)_all', 0.0), int(getAnnotationOrNone(record, "NM", None)), getAnnotationOrNone(record, "LM").split("_"), getAnnotationOrNone(record, "FS", 0.0),
    	# 		getAnnotationOrNone(record, "MQ0", None), constructStateColumn(record.samples, record.FORMAT.split(":"))
    	# 	)

        row = {
            "CHROM": record.CHROM,
            "ID": record.ID or None,
            "POS": record.POS,
            "END": record.end,
            "REF": record.REF,
            "ALT": record.ALT,
            "MUTATION": record.var_type,
            "QUAL": record.QUAL,
            "FILTER": record.FILTER or "PASS",
            "FORMAT": record.FORMAT,
            "HETEROZIGOSITY": record.heterozygosity

        }

        for (key, value) in record.INFO.items():
            if key == 'LM':
                row[key] = value[0].split('_')
            else: 
                row[key] = getAnnotationOrNone(record, key, None)

    	ROWS.append(row)

    	sys.stdout.write("%d lines scanned %s"%(row_count,"\r"))
        sys.stdout.flush();

    print ""
    
    # ---- costruisco il dataframe con pandas
    #dataframe = pd.DataFrame(data=ROWS, columns=CSV_HEADERS)
    dataframe = pd.DataFrame(ROWS)
    
    # ---- memorizzo il risultato in un file csv
    dataframe.to_csv( data_folder + username + "_" + experiment + "_" + os.path.basename(file.name) + ".data", sep="\t", index=False)

    print dataframe.dtypes
    #print type(dataframe.head(1).gene_refGene)

if __name__ == "__main__":
   main(sys.argv[1:])