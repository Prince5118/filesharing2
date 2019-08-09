#!usr/bin/python
from command import Command
from samba import *
print('Hello')

"""

def run_list_file (workgroup, sharename, username, passwd=None, cwd='', filename=None) :
    if filename is None : return None
    options = ""
    com = " -D '%s' -c 'dir \"%s\" - \"  '" % (cwd, filename)
    command =  "%s %s '\\\\%s\\%s' %s %s" % (smbclient, options, workgroup, sharename, get_user_string(username, passwd), com)
#    print command
    return Command().runcommand(command)

"""


com =" smbclient '\\\\10.35.28.189\\u1' -U u1%u123 -D '' -c 'ls'"

#com = " smbclient '\\\\10.35.28.189\\u1' -U u1%u123 -D 't2' -c 'cd /root ; put neeraj.txt '"

#com = " smbclient '\\\\10.35.28.189\\u1' -U u1%u123 -D 't2' -c 'cd /root ; put neeraj.txt '"

#com = "smbclient '\\\\10.35.28.189\\u1' -U u1%u123 -D '' -c 'cd /root/ ; put neeraj.txt '"

x =  Command().runcommand(com)

print(x._stdout)

