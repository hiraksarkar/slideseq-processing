#!/usr/bin/python

# This script is to tag bam using matched bead barcodes

from __future__ import print_function

import sys
import os
import getopt
import csv

import argparse
import glob
import re
from subprocess import call
from datetime import datetime

import random
from random import sample

import numpy as np
# silence warnings for pandas below
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import traceback

# Convert string to boolean
def str2bool(s):
    return s.lower() == "true"


# Write to log file
def write_log(log_file, flowcell_barcode, log_string):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as logfile:
        logfile.write(dt_string+" [Slide-seq Flowcell Alignment Workflow - "+flowcell_barcode+"]: "+log_string+"\n")
    logfile.close()


def main():   
    if len(sys.argv) != 7:
        print("Please provide six arguments: manifest file, library ID, lane ID, slice ID, sample barcode and locus function list!")
        sys.exit()
    
    manifest_file = sys.argv[1]
    library = sys.argv[2]
    lane = sys.argv[3]
    slice = sys.argv[4]
    barcode = sys.argv[5]
    locus_function_list = sys.argv[6]

    # Check if the manifest file exists
    if not os.path.isfile(manifest_file):
        print("File {} does not exist. Exiting...".format(manifest_file))
        sys.exit()

    # Read manifest file
    options = {}
    with open(manifest_file,"r") as fp:
        for line in fp:
            dict = line.rstrip().split("=")
            options[dict[0]] = dict[1]
    fp.close()
    
    flowcell_directory = options['flowcell_directory']
    output_folder = options['output_folder']
    metadata_file = options['metadata_file']
    flowcell_barcode = options['flowcell_barcode']
    library_folder = options['library_folder'] if 'library_folder' in options else '{}/libraries'.format(output_folder)
    scripts_folder = options['scripts_folder'] if 'scripts_folder' in options else '/broad/macosko/jilong/slideseq_pipeline/scripts'

    # Read info from metadata file
    reference = ''
    email_address = ''
    experiment_date = ''
    base_quality = '10'
    min_transcripts_per_cell = '10'
    with open('{}/parsed_metadata.txt'.format(output_folder), 'r') as fin:
        reader = csv.reader(fin, delimiter='\t')
        rows = list(reader)
        row0 = rows[0]
        for i in range(1, len(rows)):
            row = rows[i]
            if row[row0.index('library')] == library:
                reference = row[row0.index('reference')]
                email_address = row[row0.index('email')]
                experiment_date = row[row0.index('date')]
                base_quality = row[row0.index('base_quality')]
                min_transcripts_per_cell = row[row0.index('min_transcripts_per_cell')]
                break
    fin.close()
    
    referencePure = reference[reference.rfind('/') + 1:]
    if (referencePure.endswith('.gz')):
        referencePure = referencePure[:referencePure.rfind('.')]
    referencePure = referencePure[:referencePure.rfind('.')]
    reference2 = referencePure + '.' + locus_function_list

    log_file = '{}/logs/workflow.log'.format(output_folder)
    alignment_folder = '{}/{}_{}/{}/alignment/'.format(library_folder, experiment_date, library, reference2)
    barcode_matching_folder = '{}/{}_{}/{}/barcode_matching'.format(library_folder, experiment_date, library, reference2)
    prefix_libraries = '{}/{}.{}.{}.{}'.format(barcode_matching_folder, flowcell_barcode, lane, slice, library)
    if (barcode):
        prefix_libraries += '.'+barcode
    mapped_bam = prefix_libraries + '.star_gene_exon_tagged2.bam'
    mapped_sam = '{}/{}_{}_{}_{}_aligned.sam'.format(barcode_matching_folder, library, lane, slice, barcode)
    tagged_sam = '{}/{}_{}_{}_{}_tagged.sam'.format(barcode_matching_folder, library, lane, slice, barcode)
    tagged_bam = '{}/{}_{}_{}_{}_tagged.bam'.format(barcode_matching_folder, library, lane, slice, barcode)
    raw_sam = '{}/{}_{}_{}_{}_raw.sam'.format(barcode_matching_folder, library, lane, slice, barcode)
    raw_bam = '{}/{}_{}_{}_{}_raw.bam'.format(barcode_matching_folder, library, lane, slice, barcode)
    shuffled_sam = '{}/{}_{}_{}_{}_shuffled.sam'.format(barcode_matching_folder, library, lane, slice, barcode)
    shuffled_bam = '{}/{}_{}_{}_{}_shuffled.bam'.format(barcode_matching_folder, library, lane, slice, barcode)
    combined_cmatcher_file = '{}/{}_barcode_matching.txt'.format(barcode_matching_folder, library)
    combined_cmatcher_shuffled_file = '{}/{}_barcode_matching_shuffled.txt'.format(barcode_matching_folder, library)
    
    if not os.path.isfile(mapped_bam):
        write_log(log_file, flowcell_barcode, 'TagMatchedBam error: '+mapped_bam+' does not exist!')
        raise Exception('TagMatchedBam error: '+mapped_bam+' does not exist!')
    
    if not os.path.isfile(combined_cmatcher_file):
        write_log(log_file, flowcell_barcode, 'TagMatchedBam error: '+combined_cmatcher_file+' does not exist!')
        raise Exception('TagMatchedBam error: '+combined_cmatcher_file+' does not exist!')
    
    if not os.path.isfile(combined_cmatcher_shuffled_file):
        write_log(log_file, flowcell_barcode, 'TagMatchedBam error: '+combined_cmatcher_shuffled_file+' does not exist!')
        raise Exception('TagMatchedBam error: '+combined_cmatcher_shuffled_file+' does not exist!')
    
    folder_running = '{}/status/running.tag_matched_bam_{}_{}_{}_{}_{}'.format(output_folder, library, lane, slice, barcode, reference2)
    folder_finished = '{}/status/finished.tag_matched_bam_{}_{}_{}_{}_{}'.format(output_folder, library, lane, slice, barcode, reference2)
    folder_failed = '{}/status/failed.tag_matched_bam_{}_{}_{}_{}_{}'.format(output_folder, library, lane, slice, barcode, reference2)

    try:
        call(['mkdir', '-p', folder_running])
        
        write_log(log_file, flowcell_barcode, "Tag matched bam for "+library+" "+reference2+" in lane "+lane+" slice "+slice)
        
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        print(dt_string)
        
        print('mapped bam to sam')
        commandStr = 'samtools view -h -o '+mapped_sam+' '+mapped_bam
        os.system(commandStr)
        
        call(['rm', mapped_bam])

        print('read combined_cmatcher_file into dict1')
        dict1 = {}
        with open(combined_cmatcher_file, 'r') as fin:
            j = 0
            for line in fin:
                j += 1
                if j > 1:
                    dict1[line.split('\t')[0]] = line.split('\t')[2]
        fin.close()
        
        print('read raw2shuffle into dict2')
        dict2 = {}
        select_cell_file = alignment_folder+library+'.'+min_transcripts_per_cell+'_transcripts_mq_'+base_quality+'_selected_cells.txt'
        select_cell_shuffled_file = alignment_folder+library+'.'+min_transcripts_per_cell+'_transcripts_mq_'+base_quality+'_selected_cells.shuffled.txt'
        bc1 = np.loadtxt(select_cell_file, delimiter='\t', dtype='str', usecols=(0))
        bc2 = np.loadtxt(select_cell_shuffled_file, delimiter='\t', dtype='str', usecols=(0))
        for i in range(len(bc1)):
            dict2[bc1[i].strip('\n')] = bc2[i].strip('\n')
        
        print('read combined_cmatcher_shuffled_file into dict3')
        dict3 = {}
        with open(combined_cmatcher_shuffled_file, 'r') as fin:
            j = 0
            for line in fin:
                j += 1
                if j > 1:
                    dict3[line.split('\t')[0]] = line.split('\t')[2]
        fin.close()
        
        print('gen tagged_sam')
        with open(tagged_sam, 'w') as fout1:
            with open(raw_sam, 'w') as fout2:
                with open(shuffled_sam, 'w') as fout3:
                    with open(mapped_sam, 'r') as fin:
                        for line in fin:
                            if line[0] == '@':
                                fout1.write(line)
                                fout2.write(line)
                                fout3.write(line)
                            else:
                                items1 = line.split('\t')
                                bc1 = items1[11]
                                items2 = bc1.split(':')
                                bc2 = items2[2]
                                if bc2 in dict1:
                                    fout2.write(line)
                                    items2[2] = dict1[bc2]
                                    items1[11] = ':'.join(items2)
                                    fout1.write('\t'.join(items1))
                                if (bc2 in dict2) and (dict2[bc2] in dict3):
                                    items2[2] = dict2[bc2]
                                    items1[11] = ':'.join(items2)
                                    fout3.write('\t'.join(items1))
                    fin.close()
                fout3.close()
            fout2.close()
        fout1.close()
        
        if os.path.isfile(mapped_sam):
            call(['rm', mapped_sam])
        
        commandStr = 'samtools view -S -b '+tagged_sam+' > '+tagged_bam
        os.system(commandStr)
        
        if os.path.isfile(tagged_sam):
            call(['rm', tagged_sam])
        
        commandStr = 'samtools view -S -b '+raw_sam+' > '+raw_bam
        os.system(commandStr)
        
        if os.path.isfile(raw_sam):
            call(['rm', raw_sam])
        
        commandStr = 'samtools view -S -b '+shuffled_sam+' > '+shuffled_bam
        os.system(commandStr)
        
        if os.path.isfile(shuffled_sam):
            call(['rm', shuffled_sam])
        
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        print(dt_string)
        
        write_log(log_file, flowcell_barcode, "Tag matched bam for "+library+" "+reference2+" in lane "+lane+" slice "+slice+" is done. ")
        
        call(['mv', folder_running, folder_finished])
    except Exception as exp:
        print("EXCEPTION:!")
        print(exp)
        traceback.print_tb(exp.__traceback__, file=sys.stdout)
        if os.path.isdir(folder_running):
            call(['mv', folder_running, folder_failed])
        else:
            call(['mkdir', '-p', folder_failed])
            
        if len(email_address) > 1:
            subject = "Slide-seq workflow failed for " + flowcell_barcode
            content = "The Slide-seq workflow for "+library+" "+reference2+" in lane "+lane+" slice "+slice+" failed at the step of tagging matched bam. Please check the log file for the issues. "
            call_args = ['python', '{}/send_email.py'.format(scripts_folder), email_address, subject, content]
            call(call_args)
        
        sys.exit()


if __name__ == "__main__":
    main()


