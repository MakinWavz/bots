import os
import sys
import inmessage
import outmessage
import botslib
import botsinit
import botsglobal
from botsconfig import *

#buggy
#in usersys/grammars/xmlnocheck should be a file xmlnocheck
#usage: c:\python25\python  bots-xml2botsgrammar.py  botssys/infile/test.xml   botssys/infile/resultgrammar.py  -cconfig


def treewalker(node,mpath):
    mpath.append({'BOTSID':node.record['BOTSID']})
    for childnode in node.children:
        yield childnode,mpath[:]
        for terug in treewalker(childnode,mpath):
            yield terug 
    mpath.pop()
    

def writefields(tree,node,mpath):
    for key in node.record.keys():
        if key != 'BOTSID':
            mpath[-1][key]=u'dummy'
            tree.put(*mpath)
            del mpath[-1][key]
        
def tree2grammar(node,structure,recorddefs):
    structure.append({ID:node.record['BOTSID'],MIN:0,MAX:99999,LEVEL:[]})
    recordlist = []
    for key in node.record.keys():
        recordlist.append([key, 'C', 256, 'AN'])
    recorddefs[node.record['BOTSID']] = recordlist
    for childnode in node.children:
        tree2grammar(childnode,structure[-1][LEVEL],recorddefs)

def formatrecorddefs(recorddefs):
    recorddefsstring = "{\n"
    for key, value in recorddefs.items():
        recorddefsstring += "    '%s':\n        [\n"%key
        for field in value:
            if field[0]=='BOTSID':
                field[1]='M'
                recorddefsstring += "        %s,\n"%field
                break
        for field in value:
            if '__' in field[0]:
                recorddefsstring += "        %s,\n"%field
        for field in value:
            if field[0]!='BOTSID' and '__' not in field[0]:
                recorddefsstring += "        %s,\n"%field
        recorddefsstring += "        ],\n"
    recorddefsstring += "    }\n"
    return recorddefsstring
    
def formatstructure(structure,level=0):
    structurestring = ""
    for i in structure:
        structurestring += level*"    " + "{ID:'%s',MIN:%s,MAX:%s"%(i[ID],i[MIN],i[MAX])
        recursivestructurestring = formatstructure(i[LEVEL],level+1)
        if recursivestructurestring:
            structurestring += ",LEVEL:[\n" + recursivestructurestring + level*"    " + "]},\n"
        else:
            structurestring += "},\n"
    return structurestring
    
def showusage():
    print
    print 'Usage:'
    print '    %s   -c<directory>  <xml_file>  <xml_grammar_file>'%os.path.basename(sys.argv[0])
    print
    print '    Creates a grammar from an xml file.'
    print '    Options:'
    print "        -c<directory>      directory for configuration files (default: config)."
    print '        <xml_file>         name of the xml file to read'
    print '        <xml_grammar_file> name of the grammar file to write'
    print
    sys.exit(0)
    
def start():
    #********command line arguments**************************
    edifile =''
    grammarfile = ''
    configdir = 'config'
    for arg in sys.argv[1:]:
        if not arg:
            continue
        if arg.startswith('-c'):
            configdir = arg[2:]
            if not configdir:
                print '    !!Indicated Bots should use specific .ini file but no file name was given.'
                showusage()
        elif arg in ["?", "/?"] or arg.startswith('-'):
            showusage()
        else:
            if not edifile:
                edifile = arg
            else:
                grammarfile = arg
    if not (edifile and grammarfile):
        print '    !!Both edifile and grammarfile are required.'
        showusage()

    #********end handling command line arguments**************************
    
    mpath = []
    structure = []
    recorddefs = {}
    
    botsinit.generalinit(configdir)
    os.chdir(botsglobal.ini.get('directories','botspath'))
    botsinit.initenginelogging()
    
    #~ botslib.initconfigurationfile(botsinifile)
    #~ botslib.initbotscharsets()
    #~ botslib.initlogging()
    
    inn = inmessage.edifromfile(editype='xmlnocheck',messagetype='xmlnocheck',filename=edifile)
    out = outmessage.outmessage_init(editype='xmlnocheck',messagetype='xmlnocheck',filename='botssys/infile/unitnode/output/inisout03.edi',divtext='',topartner='')    #make outmessage object
    #~ inn.root.display()
    #handle root
    rootmpath = [{'BOTSID':inn.root.record['BOTSID']}]
    out.put(*rootmpath)
    writefields(out,inn.root,rootmpath)
    #walk tree; write results to out-tree
    for node,mpath in treewalker(inn.root,mpath):
        mpath.append({'BOTSID':node.record['BOTSID']})
        if out.get(*mpath) is None:
            out.put(*mpath)
        writefields(out,node,mpath)
        
    #out-tree is finished; represents ' normalised' tree suited for writing as a grammar
    tree2grammar(out.root,structure,recorddefs)
    recorddefsstring = formatrecorddefs(recorddefs)
    structurestring = formatstructure(structure)
    
    #~ out.root.display()
    #write grammar file
    grammar = open(grammarfile,'wb')
    grammar.write('#grammar automatically generated by bots open source edi software.')
    grammar.write('\n\n')
    grammar.write('from bots.botsconfig import *')
    grammar.write('\n\n')
    grammar.write('syntax = {}')
    grammar.write('\n\n')
    grammar.write('structure = [\n%s]\n'%(structurestring))
    grammar.write('\n\n')
    grammar.write('recorddefs = %s'%(recorddefsstring))
    grammar.write('\n\n')
    grammar.close()
    print 'grammar file is written',grammarfile

if __name__ == '__main__':
    start()
    
