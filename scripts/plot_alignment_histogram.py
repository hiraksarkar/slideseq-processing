#!/usr/bin/python

from __future__ import print_function

import sys
import os
import getopt
import csv
import gzip
import shutil

import argparse
import glob
import re
import time
from subprocess import call
from datetime import datetime

import numpy as np
# silence warnings for pandas below
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
import pandas as pd

import random
from random import sample

import itertools

import math
import numpy.polynomial.polynomial as poly

import plotnine as pn
from plotnine import *

import matplotlib as mpl
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

if len(sys.argv) != 4:
    print("Please provide three arguments: folder, file name, and library ID!")
    sys.exit()

folder = sys.argv[1]
filename = sys.argv[2]
library = sys.argv[3]

file1 = '{}/{}.unique.ratio'.format(folder, filename)
file2 = '{}/{}.multi.ratio'.format(folder, filename)
file3 = '{}/{}.unique.score'.format(folder, filename)
file4 = '{}/{}.multi.score'.format(folder, filename)
file5 = '{}/{}.unique.mismatch'.format(folder, filename)
file6 = '{}/{}.multi.mismatch'.format(folder, filename)

pp = PdfPages('{}/{}_alignment_quality.pdf'.format(folder, library))

# plot alignment ratio
df_x = np.loadtxt(file1, delimiter='\t', dtype='int', usecols=(0))
df_y = np.loadtxt(file1, delimiter='\t', dtype='int', usecols=(1))
df = pd.DataFrame({"x":df_x, "y":df_y})
fig, ax = plt.subplots(figsize=(8, 8))
plt.bar(df['x'], df['y'], width=0.7, color='lightskyblue', edgecolor='black')
plt.yticks(rotation=90)
plt.xlabel("alignment ratio %")
plt.title("Histogram of unique alignment ratio")
plt.savefig(pp, format='pdf')

df_x = np.loadtxt(file2, delimiter='\t', dtype='int', usecols=(0))
df_y = np.loadtxt(file2, delimiter='\t', dtype='int', usecols=(1))
df = pd.DataFrame({"x":df_x, "y":df_y})
fig, ax = plt.subplots(figsize=(8, 8))
plt.bar(df['x'], df['y'], width=0.7, color='lightskyblue', edgecolor='black')
plt.yticks(rotation=90)
plt.xlabel("alignment ratio %")
plt.title("Histogram of multiple alignment ratio")
plt.savefig(pp, format='pdf')

# plot alignment score
df_x = np.loadtxt(file3, delimiter='\t', dtype='int', usecols=(0))
df_y = np.loadtxt(file3, delimiter='\t', dtype='int', usecols=(1))
df = pd.DataFrame({"x":df_x, "y":df_y})
fig, ax = plt.subplots(figsize=(8, 8))
plt.bar(df['x'], df['y'], width=0.7, color='lightskyblue', edgecolor='black')
plt.yticks(rotation=90)
plt.xlabel("alignment score")
plt.title("Histogram of unique alignment score")
plt.savefig(pp, format='pdf')

df_x = np.loadtxt(file4, delimiter='\t', dtype='int', usecols=(0))
df_y = np.loadtxt(file4, delimiter='\t', dtype='int', usecols=(1))
df = pd.DataFrame({"x":df_x, "y":df_y})
fig, ax = plt.subplots(figsize=(8, 8))
plt.bar(df['x'], df['y'], width=0.7, color='lightskyblue', edgecolor='black')
plt.yticks(rotation=90)
plt.xlabel("alignment score")
plt.title("Histogram of multiple alignment score")
plt.savefig(pp, format='pdf')

# plot alignment mismatch
df_x = np.loadtxt(file5, delimiter='\t', dtype='int', usecols=(0))
df_y = np.loadtxt(file5, delimiter='\t', dtype='int', usecols=(1))
df = pd.DataFrame({"x":df_x, "y":df_y})
fig, ax = plt.subplots(figsize=(8, 8))
plt.bar(df['x'], df['y'], width=0.7, color='lightskyblue', edgecolor='black')
plt.yticks(rotation=90)
plt.xlabel("alignment mismatch")
plt.title("Histogram of unique alignment mismatch")
plt.savefig(pp, format='pdf')

df_x = np.loadtxt(file6, delimiter='\t', dtype='int', usecols=(0))
df_y = np.loadtxt(file6, delimiter='\t', dtype='int', usecols=(1))
df = pd.DataFrame({"x":df_x, "y":df_y})
fig, ax = plt.subplots(figsize=(8, 8))
plt.bar(df['x'], df['y'], width=0.7, color='lightskyblue', edgecolor='black')
plt.yticks(rotation=90)
plt.xlabel("alignment mismatch")
plt.title("Histogram of multiple alignment mismatch")
plt.savefig(pp, format='pdf')

pp.close()
