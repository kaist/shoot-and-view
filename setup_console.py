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
  

try:shutil.copyfile('c:/dev/bin/msvcr90.dll','dist/msvcr90.dll')
except IOError:print 'msvcr90.dll not found in windows/system32'
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


    
    console=['sdwificard.py'],
    
    
    
    options={"py2exe":{"optimize": 2,"includes":[],"packages":[],"excludes":['unicodedata','bz2','ssl','unittest','doctest','pdb','difflib','_ctypes','ctypes'],"compressed":True}},
    zipfile='app/lib.zip')

print 'Deleting unnecessary files....'

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
 

