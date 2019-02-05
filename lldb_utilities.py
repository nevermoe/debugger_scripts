#!/usr/bin/python

# installation
"""
echo "command script import `pwd`/lldb_utilities.py" >> ~/.lldbinit
"""


import lldb
import commands
import optparse
import shlex

def dbgcall(command):
    res = lldb.SBCommandReturnObject()
    lldb.debugger.GetCommandInterpreter().HandleCommand(command, res)
    return res.GetOutput()

def imlist(debugger, command, result, internal_dict):
    output = dbgcall("image list")
    for line in output.splitlines():
        if command in line:
            print line

def ls(debugger, command, result, internal_dict):
    print >>result, (commands.getoutput('/bin/ls %s' % command))

# And the initialization code to add your commands 
def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f lldb_utilities.ls ls')
    print 'The "ls" python command has been installed and is ready for use.'

    debugger.HandleCommand('command script add -f lldb_utilities.imlist imlist')
    print 'The "imlist" python command has been installed and is ready for use.'
