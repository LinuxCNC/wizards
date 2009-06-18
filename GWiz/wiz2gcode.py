#!/usr/bin/python

#----------------------------------------------------------------------------
"""GWiz -- A tool to take a wizard file and prepend all the wizards to it.
   If the wiz file is a % file, the % is moved to the beginning, and a
   trailing % is put on the end (even if one was missing).
   Written by K. Lerman"""

import sys, os
import dircache
import string

BASE = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
sys.path.insert(0, os.path.join(BASE, "lib", "python"))

import emc

home = os.getenv('HOME')

# first argument is -ini
# second is ini file name
# third is file to process

# read ini file stuff

emcrc = emc.ini(home + '/' + '.emcrc')
inifilename = emcrc.find("PICKCONFIG", "LAST_CONFIG")

inifile = emc.ini(inifilename)

if inifilename == None:
    raise SystemExit, "-ini must be first argument or must pick config"

wizard_root = inifile.find("WIZARD", "WIZARD_ROOT")
if wizard_root is None:
  wizard_root = '/usr/share/gwiz/wizards'

fullPath = sys.argv[1]

#print "(wizard root:", wizard_root, ")"
#print "(file name:", fullPath, ")"

#---------------------------------------------------------------------------

def main():

    hasPercent = testPercent(fullPath)

    if(hasPercent):
        print "%"
    print "(----------------------)"
    print "(wizard programs follow)"
    print "(----------------------)"

    # now copy the wizard files
    rootDirect = wizard_root
    traverseTree(rootDirect+"/")

    # copy the actual file
    print "(----------------------)"
    print "(main program follows  )"
    print "(----------------------)"
    copyFile(fullPath)

    # copy the trailing percent if any
    if hasPercent:
        print "%"

def traverseTree(dirName):
    """ Recursively traverses the directory outputting ngc files """

    try:
        direct = dircache.listdir(dirName)
        dircache.annotate(dirName, direct)
        #print "direct OK", dirName, direct

    except IOError:
        #print "direct NG", dirName
        return

    # now traverse the children one at a time

    # for each child that is a directory
    for d in direct[:]:
        # print "---", d
        # if a directory, recurse
        if d[-1] == '/':
            traverseTree(dirName + d)
        # if an ngc file, append to the output
        elif d[-4:] == '.ngc':
	    print "(from wizard:", dirName+d, ")"
	    copyFile(dirName + d)

#----------------------------------------------------------------------------

def testPercent(fullName):
    ret = 0
    try:
        f = open(fullName, 'r')
	for line in f:
            line.rstrip(string.whitespace)
            line.lstrip(string.whitespace)
	    if(len(line) == 0):
                continue
            if (line[0] == '%'):
                ret = 1
            else:
                ret = 0

        f.close()
        return ret

    except IOError:
         print "Unable to read file:", fullName
    return 0


# Copy the file. Percent lines are deleted. Stuff after a second percent line
# is not copied.

def copyFile(fullName):
    firstLine = 0
    try:
        f = open(fullName, 'r')
        for line in f:
            lineCopy = line
            lineCopy.rstrip(string.whitespace)
            lineCopy.lstrip(string.whitespace)

	    if (len(lineCopy) and lineCopy[0] == '%') and (firstLine == 0):
                firstLine = 1
            elif (len(lineCopy) and line[0] == '%') and (firstLine == 1):
                break
            else:
                print line,
        f.close()

    except IOError:
         print "Unable to read file:", fullName
 
main()
#----------------------------------------------------------------------------
