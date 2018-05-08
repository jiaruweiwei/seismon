
import os, sys, glob, optparse, shutil, warnings
import urllib
import zipfile

__author__ = "Michael Coughlin <michael.coughlin@ligo.org>"
__version__ = 0.1
__date__    = "10/25/2016"

def parse_commandline():
    """@Parse the options given on the command-line.
    """
    parser = optparse.OptionParser(usage=__doc__,version=__version__)

    parser.add_option("-o", "--outputDir", help="Seismon installation directory.",
                      default ="/home/michael.coughlin/seismon_install")

    parser.add_option("-v", "--verbose", action="store_true", default=False,
                      help="Run verbosely. (Default: False)")

    parser.add_option("-p", "--productClient", help = "USGS PDL download link.",
                      default = "https://github.com/usgs/pdl/releases/download/v1.14.0/ProductClient.zip")

    opts, args = parser.parse_args()

    # show parameters
    if opts.verbose:
        print >> sys.stderr, ""
        print >> sys.stderr, "running pylal_seismon_run..."
        print >> sys.stderr, "version: %s"%__version__
        print >> sys.stderr, ""
        print >> sys.stderr, "***************** PARAMETERS *****************    ***"
        for o in opts.__dict__.items():
          print >> sys.stderr, o[0]+":"
          print >> sys.stderr, o[1]
        print >> sys.stderr, ""
    return opts

def mkdir(path):
    """@create path (if it does not already exist).

    @param path
        directory path to create
    """

    pathSplit = path.split("/")
    pathAppend = "/"
    for piece in pathSplit:
        if piece == "":
            continue
        pathAppend = os.path.join(pathAppend,piece)
        if not os.path.isdir(pathAppend):
            os.mkdir(pathAppend)

warnings.filterwarnings("ignore")
# Parse command line
opts = parse_commandline()

outputDir = opts.outputDir
if not os.path.isdir(outputDir):
    mkdir(outputDir)

productclient = opts.productClient
productclient_zip = "%s/ProductClient.zip"%outputDir
productclient_output = "%s/ProductClient"%outputDir

seismon = "https://github.com/ligovirgo/seismon"
seismon_output = "%s/seismon"%outputDir

eventfiles_output = "%s/eventfiles"%outputDir

if not os.path.isfile(productclient_zip):
    urllib.urlretrieve(productclient, filename=productclient_zip)

zip_ref = zipfile.ZipFile(productclient_zip, 'r')
zip_ref.extractall(outputDir)
zip_ref.close()

if not os.path.isdir(seismon_output):
    os.system("cd %s; git clone %s"%(outputDir,seismon))
    os.system("cd %s; /usr/bin/env python setup.py install --user"%seismon_output)

configexample = "%s/seismon/input/config.ini"%seismon_output
configini = "%s/config.ini"%productclient_output

file = open(configexample)
contents = file.read()
replaced_contents = contents.replace('XXX_PRODUCTCLIENT', productclient_output)

text_file = open(configini, "w")
text_file.write(replaced_contents)
text_file.close()

initfile = "%s/init.sh"%productclient_output
os.system("chmod +rwx %s"%initfile)

mkdir(eventfiles_output)

traveltimesexample = "%s/seismon/input/seismon_params_traveltimes.txt"%seismon_output
traveltimesini = "%s/seismon_params_traveltimes.txt"%eventfiles_output

file = open(traveltimesexample)
contents = file.read()
replaced_contents = contents.replace('XXX_PRODUCTCLIENT', productclient_output).replace('XXX_SEISMON',eventfiles_output)

text_file = open(traveltimesini, "w")
text_file.write(replaced_contents)
text_file.close()

lines = [line.rstrip('\n') for line in open(traveltimesini)]
for line in lines:
    lineSplit = line.split(" ")
    varname = lineSplit[0]
    varpath = lineSplit[1]
    mkdir(varpath)

    if varname == "eventfilesLocation":
        eventfilesTypes = ["public","private","iris"]
        for eventfilesType in eventfilesTypes:
            eventfilepath = "%s/%s"%(varpath,eventfilesType)
            mkdir(eventfilepath)

notice = """
         NOTE: A new dependency is MATLAB Runtime version 9.1 (R2016b).
         Instructions for installing Runtime only are available here:
         RfPrediction/RfAmp_Compiled_Python_Package/robustLocklossPredictionPkg3/for_redistribution_files_only/readme.txt
         Otherwise, with MATLAB 2016b installed, paths can be set as:
         MATLAB_PATH='/ldcg/matlab_r2016b'
         export LD_LIBRARY_PATH="$MATLAB_PATH/sys/os/glnxa64:$MATLAB_PATH/bin/glnxa64:$MATLAB_PATH/extern/lib/glnxa64:$MATLAB_PATH/runtime/glnxa64:$MATLAB_PATH/sys/java/jre/glnxa64/jre/lib/amd64/native_threads:$MATLAB_PATH/sys/java/jre/glnxa64/jre/lib/amd64/server"
         """

print(notice) 
