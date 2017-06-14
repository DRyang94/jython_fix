#!/usr/local/bin/jython
#coding:utf-8
# package com.btcchina.fix.util;

import java.io.BufferedReader as BufferedReader
import java.io.FileReader as FileReader
import java.io.IOException as IOException
import java.util.HashMap as HashMap
import java.util.Properties as Properties

# @SuppressWarnings("rawtypes")
class IniReader():
	def __init__(self,filename):
		self.sections = HashMap();
		self.currentSecion 
		self.current;
		reader = BufferedReader(FileReader(filename))
		self.read(reader)
		reader.close()

	def read(self,reader):
		line = None
		while (line = reader.readLine()) != None:
			self.parseLine(line)
	def parseLine(self,line):
		line = line.trim()
		if line.matches("\\[.*\\]"):
			self.currentSecion = line.replaceFirst("\\[(.*)\\]", "$1")
			self.current = Properties()
			self.sections.put(self.currentSecion, self.current)
		elif line.matches(".*=.*"):
			if self.current != None:
				i = line.find("=")
				name = line[0:i]
				value = line[i+1:]
				self.current.setProperty(name, value)
	def getValue(self,section,name):
		p = self.sections.get(section)
		if p == None:
			return None
		value = p.p.getProperty(name)
		return value
	
    def containsKey(self,section,key):
    	p = self.sections.get(section)
    	return p.contains(key)