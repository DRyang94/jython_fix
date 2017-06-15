#!/usr/local/bin/jython
#coding:utf-8
# package com.btcchina.fix.util;

import java.io.BufferedReader as BufferedReader
import java.io.FileReader as FileReader
import java.io.IOException as IOException
import java.util.HashMap as HashMap
import java.util.Properties as Properties

import re

import ConfigParser

# @SuppressWarnings("rawtypes")
class IniReader():
    def __init__(self,filename):
        # self.sections = HashMap();
        # self.currentSecion = None
        # self.current = None
        # reader = BufferedReader(FileReader(filename))
        # self.read(reader)
        # reader.close()

        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(filename))
    def getValue(self,section,name):
        p = self.config.get(section,name)
        if p == None:
            return None
        return p
    
    def containsKey(self,section,key):
        items = self.config.items(section) 
        isHeaveKey = False
        for item in items:
            if item[0] == key:
                isHeaveKey = True
        print isHeaveKey
    def getSections(self):
        return self.config.sections()
    def getOptions(self,section):
        return self.config.options(section)
if __name__ == '__main__':
    inireader = IniReader('../data/config.txt')
    inireader.containsKey("config", 'offset')
    print inireader.getSections()
    print inireader.getOptions('config')
    print inireader.getValue('config', 'offset')
    # def read(self,reader):
    #     line = reader.readLine()
    #     while line != None:
    #         self.parseLine(line)
    #         line = reader.readLine()
    # def parseLine(self,line):
    #     line = line.strip()
    #     # if line.matches("\\[.*\\]"):
    #     if re.match("\\[.*\\]", line):
    #         self.currentSecion = line.replaceFirst("\\[(.*)\\]", "$1")
    #         self.current = Properties()
    #         self.sections.put(self.currentSecion, self.current)
    #     # elif line.matches(".*=.*"):
    #     elif re.match(".*=.*", line):
    #         if self.current != None:
    #             i = line.find("=")
    #             name = line[0:i]
    #             value = line[i+1:]
    #             self.current.setProperty(name, value)
    # def getValue(self,section,name):
    #     p = self.sections.get(section)
    #     if p == None:
    #         return None
    #     value = p.p.getProperty(name)
    #     return value
    
    # def containsKey(self,section,key):
    #     p = self.sections.get(section)
    #     return p.contains(key)