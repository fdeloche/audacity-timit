'''
author: Francois Deloche
date: 2018, June
'''
import argparse
import re
import os
import sys
import random

parser = argparse.ArgumentParser()

parser.add_argument("--timit_folder", help='''Path of the TIMIT dataset. Contains the root folders SPHERE, TIMIT, CONVERT.
                    Alternatively it can be set as an environment variable named TIMIT_FOLDER.
                    ''')
parser.add_argument("--set", help="TRAIN, TEST. if not set, selected at random (same for following params)")
parser.add_argument("--dr", help="Dialect region. [1-8]")
parser.add_argument("--spk", help="Speaker. ex: FBLV0")
parser.add_argument("--sn", help="Sentence. ex: SA1")

args = parser.parse_args()

##########################################
#Helpers for audacity scripting

# Make sure Audacity is running first and that mod-script-pipe is enabled
# before running this script.

if( sys.platform  == 'win32' ):
    print( "pipe-test.py, running on windows" )
    toname = '\\\\.\\pipe\\ToSrvPipe'
    fromname = '\\\\.\\pipe\\FromSrvPipe'
    EOL = '\r\n\0'
else:
    print( "pipe-test.py, running on linux or mac" )
    toname = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
    fromname = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
    EOL = '\n'

print( "Write to  \"" + toname +"\"" )
if not os.path.exists( toname ) :
   print( " ..does not exist.  Ensure Audacity is running with mod-script-pipe." )
   sys.exit();

print( "Read from \"" + fromname +"\"")
if not os.path.exists( fromname ) :
   print( " ..does not exist.  Ensure Audacity is running with mod-script-pipe." )
   sys.exit();

print( "-- Both pipes exist.  Good." )

tofile = open( toname, 'wt+' )
print( "-- File to write to has been opened" )
fromfile = open( fromname, 'rt')
print( "-- File to read from has now been opened too\r\n" )


def sendCommand( command, verbose=False ) :
    if verbose:
        print( "Send: >>> \n"+command )
    tofile.write( command + EOL )
    tofile.flush()

def getResponse() :
    result = ''
    line = ''
    while line != '\n' :
        result += line
        line = fromfile.readline()
	#print(" I read line:["+line+"]")
    return result

def doCommand( command, verbose=False) :
    sendCommand( command )
    response = getResponse()
    if verbose:
        print( "Rcvd: <<< \n" + response )
    return response

def do( command ) :
    return doCommand( command )

##########################################



#TIMIT folder from environment variable or argument
try:
    if args.timit_folder != None:
        timit_folder = args.timit_folder
    else:
        timit_folder = os.environ['TIMIT_FOLDER']
except KeyError as e:
    print("Error : timit folder not set, please set it as an argument or set the variable 'TIMIT_FOLDER'")
    sys.exit(1)

if os.path.exists(timit_folder):
    print("Timit folder {} is defined and exists".format(timit_folder))
else:
    print("Error : Timit folder {} not found".format(timit_folder))
    sys.exit(1)


#SELECT FILE
def choose_folder(dirpath):
    selec = random.choice(os.listdir(dirpath))
    return "{}/{}".format(dirpath, selec)
dirpath = timit_folder+"/TIMIT/"
dataset = random.choice(['/TEST', '/TRAIN']) if args.set is None else args.set
dirpath += dataset
dirpath = choose_folder(dirpath) if args.dr is None else (dirpath+"/DR"+args.dr) #dr
dirpath = choose_folder(dirpath) if args.spk is None else (dirpath+"/"+args.spk)#spk
if args.sn is None:
    list_sn = []
    for filename in os.listdir(dirpath):
        m = re.match(r"(.*)\.((WAV)|(wav))", filename)
        if m:
            list_sn.append(m.group(1))
    filename = random.choice(list_sn)
    dirpath += "/"+filename
else:
    dirpath += "/"+args.sn

sn_path=sentence_path=dirpath
print("Sentence path : {}(.WAV)".format(dirpath))

#Parse PHN file
def parse_phn(filename, fs=16000):
    '''
    return a list of tuple (begin, end, phn)
    :param filename: .phn file (or .wrd, .txt for words and sentence)
    :param fs: sampling frequency'''
    try:
        l = []
        with open(filename,'r') as f:
            for line in f:
                m = re.match(r"(?P<begin>\d*) (?P<end>\d*) (?P<phn>.*)", line, flags=0)
                if m:
                    l.append((float(m.group("begin"))*1./fs, float(m.group("end"))*1./fs, m.group("phn")))
                else:
                    print("WARNING : line in .phn can not be read")
        return l
    except IOError as e:
        print("Error : {} file does not exist".format(filename))
        return []

do('Import2:Filename="{}.WAV"'.format(sn_path))

#PHN
l_phn = parse_phn("{}.PHN".format(sn_path))
n = len(l_phn)
do("NewLabelTrack:")
do('SetTrack:Name="PHN"')
for i in range(n):
    do("AddLabel:")
for i in range(n):
    t=l_phn[i]
    do('SetLabel:Label="{}" Text="{}" Start="{:.3f}" End="{:.3f}"'.format(i, t[2], t[0], t[1]))

#WRD
l_wrd = parse_phn("{}.WRD".format(sn_path))
m = len(l_wrd)
do("NewLabelTrack:")
do('SetTrack:Name="WRD"')
for i in range(m):
    do("AddLabel:")
for i in range(m):
    t=l_wrd[i]
    do('SetLabel:Label="{}" Text="{}" Start="{:.3f}" End="{:.3f}"'.format(n+i, t[2], t[0], t[1]))

#SENTENCE
l_txt = parse_phn("{}.TXT".format(sn_path))
p = len(l_txt)
do("NewLabelTrack:")
do('SetTrack:Name="SENTENCE"')
for i in range(p):
    do("AddLabel:")
for i in range(p):
    t=l_txt[i]
    do('SetLabel:Label="{}" Text="{}" Start="{:.3f}" End="{:.3f}"'.format(n+m+i, t[2], t[0], t[1]))
