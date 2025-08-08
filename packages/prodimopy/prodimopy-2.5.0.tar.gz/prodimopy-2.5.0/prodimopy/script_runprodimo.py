'''
  Simple script to run prodimo from the command line.

  Mainly for convenience. The script makes sure that the log output is written to a file, but also allows to e.g. set the number of threads.
'''

import argparse
import prodimopy.utils as putils

import shutil
import subprocess
import os

# The main routine is require to have an entry point.
# It is not necessary if you want to write your own script.
def main(args=None):
  parser=argparse.ArgumentParser(description='Runs ProDiMo in the current working directory.')
  parser.add_argument('PARAMA',nargs="?",help='Add additional Parameter input file (additional to Parameter.in)',default=None)
  parser.add_argument('-n',help="The number of OMP threads to use. (Default is System settings, e.g. what's in OMP_NUM_THREADS)",default=None)

  args=parser.parse_args()

  # Check if prodimo is in the path
  prodimopath=shutil.which("prodimo")
  if prodimopath is None:
    print("ERROR: prodimo is not in the path. Please add it to the path, or provide the path to the executable.")
    return

  callargs=[prodimopath]
  if args.PARAMA is not None:
    callargs.append(args.PARAMA)

  print("Run ProDiMo with: "," ".join(callargs),"in the background ...")

  penv=os.environ.copy()
  if args.n is not None:
    print("Setting number of OMP threads to: ",args.n)
    penv=os.environ.copy()
    penv["OMP_NUM_THREADS"]=args.n.strip()   
  
  with open("prodimo.log","w") as f:
    proc=subprocess.Popen(callargs,stdout=f,stderr=f,env=penv)
    
  print("You can check the progress by looking at the file prodimo.log")
    
  print("You can stop ProDiMo by killing the process with:  kill ",proc.pid)

  
  #subprocess.run(executable=prodimopath,args=[">","prodimo.log"],STD) 