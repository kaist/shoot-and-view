#coding:utf-8
from distutils.core import setup
import sys
import py2exe
import shutil
import os
import subprocess
import glob



print 'Copying a folder with the program resource....'
try:shutil.rmtree('dist')	
except WindowsError:pass

shutil.copytree('app/','dist/app')    

try:shutil.copyfile('c:/dev/bin/msvcr90.dll','dist/msvcr90.dll')
except IOError:print 'msvcr90.dll not found in windows/system32'
shutil.copyfile('exiftool.exe','dist/exiftool.exe')
# get revision from bzr
s=subprocess.Popen(['bzr','log'],shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
try:revision=s.stdout.read().split('revno: ')[1].split('\n')[0]
except IndexError:revision='0'
print 'Revision: '+revision



setup(
# The first three parameters are not required, if at least a
# 'version' is given, then a versioninfo resource is built from
# them and added to the executables.
    version = "1.%s"%(revision),
    description = "Shoot&View Transcend WiFi",
    name = "Shoot&View Transcend WiFi",

# targets to build

    windows = [
        {"script": "ShootAndView.pyw",
            "icon_resources": [(0, "app/images/icon.ico")]}
            ],
    
    
    
    options={"py2exe":{"optimize": 2,"includes":[],"packages":[],"excludes":['unicodedata','bz2','ssl','unittest','doctest','pdb','difflib','_ctypes','ctypes'],"compressed":True}},
    zipfile='app/lib.zip')

print 'Deleting unnecessary files....'
shutil.rmtree('dist/app/tcl/tcl8.5/tzdata/')
shutil.rmtree('dist/app/tcl/tcl8.5/msgs/')
shutil.rmtree('dist/app/tcl/tcl8.5/opt0.4/')
shutil.rmtree('dist/app/tcl/tcl8.5/http1.0/')
os.remove('dist/app/tcl/tcl8.5/clock.tcl')

shutil.rmtree('dist/app/tcl/tk8.5/demos')
shutil.rmtree('dist/app/tcl/tk8.5/images')
shutil.rmtree('dist/app/tcl/tk8.5/msgs')
shutil.rmtree('build')
os.remove('dist/w9xpopen.exe')
os.remove('dist/app/_ssl.pyd')




print 'Compressing files ....'
lst=['upx','--brute','-q']
for x in ['dist/*.exe','dist/*.dll','dist/app/*.exe','dist/app/*.dll','dist/app/*.pyd']:
    l=glob.glob(x)
    for y in l:lst.append(y)




try:subprocess.Popen(lst)
except WindowsError:print 'UPX not found'
 

