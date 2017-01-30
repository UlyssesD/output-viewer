# !/usr/bin/python   # Script python per il batch parsing di file vcf
# -*- coding: utf-8 -*-

import os
import sys
import glob

def main(argv):

    base_dir = argv[0]
    temp_folder = argv[1]
    user = argv[2]
    experiment = argv[3]
    species = argv[4]

    for folder in os.listdir(base_dir):
        for file in glob.glob(base_dir + folder + "/*.vcf"):
            os.system('python prova.py "' + file + '" "' + temp_folder + '" "' + user + '" "' + experiment + '" "' + species + '"')

if __name__ == "__main__":
   main(sys.argv[1:])