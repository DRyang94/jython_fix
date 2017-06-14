# package com.btcchina.fix.util;

import java.util.Iterator as Iterator

import quickfix.DataDictionary as DataDictionary
import quickfix.Field as Field
import quickfix.FieldMap as FieldMap
import quickfix.FieldNotFound as FieldNotFound
import quickfix.FieldType as FieldType
import quickfix.Group as Group
import quickfix.field.MsgType as MsgType
import quickfix.fix44.Message as Message

import javax.xml.parsers.DocumentBuilderFactory as DocumentBuilderFactory
import javax.xml.parsers.DocumentBuilder as DocumentBuilder

import org.w3c.dom.Document as Document
import org.w3c.dom.NodeList as NodeList
import org.w3c.dom.Node as Node
import org.w3c.dom.Element as Element

import java.io.File as File

class MessagePrinter():
    def __init__(self):
        pass

    def mpprint(self,dd,message):
        msgType = message.getHeader().getString(MsgType.FIELD)
        self.printFieldMap("", dd, msgType, message.getHeader())
        self.printFieldMap("", dd, msgType, message)
        self.printFieldMap("", dd, msgType, message.getTrailer())

    def printFieldMap(self,prefix,dd,msgType,fieldMap):
        fieldIterator = fieldMap.iterator()
        while fieldIterator.hasNext():
            Field field = fieldIterator.next();
            if not self.isGroupCountField(dd, field): 
                value = fieldMap.getString(field.getTag())
                if dd.hasFieldValue(field.getTag()): 
                    value = dd.getValueName(field.getTag(), fieldMap.getString(field.getTag())) + " (" + value + ")"
                print prefix + dd.getFieldName(field.getTag()) + ": " + value 
        groupsKeys = fieldMap.groupKeyIterator();
        while groupsKeys.hasNext():
            groupCountTag = int(groupsKeys.next())
            print prefix + dd.getFieldName(groupCountTag) + ": count = " + fieldMap.getInt(groupCountTag))
            g = Group(groupCountTag, 0)
            i = 1;
            while fieldMap.hasGroup(i, groupCountTag):
                if i > 1:
                    print prefix + "  ----"
                fieldMap.getGroup(i, g)
                self.printFieldMap(prefix + "  ", dd, msgType, g)
                i += 1
    def isGroupCountField(self,dd,field):
        return dd.getFieldTypeEnum(field.getTag()) == FieldType.NumInGroup
 
    def mainTest(self):
        mp=MessagePrinter()
        symbol = mp.getFieldName("55")
        print "Symbol is "+symbol
        group = mp.getFieldName("269","0")
        print "group is "+group

    def getFieldName(self,tag):
        field_name=""
        try:
            fixdic = File("data/FIX44.xml")
            dbFactory = DocumentBuilderFactory.newInstance()
            dBuilder = dbFactory.newDocumentBuilder()
            parser = dBuilder.parse(fixdic)
            parser.getDocumentElement().normalize()
            fieldList = parser.getElementsByTagName("field")
            print "----------------------------------"
            for i in range(fieldList.getLength()):
                fieldNode = fieldList.item(i)
                if fieldNode.getNodeType() == Node.ELEMENT_NODE:
                    fieldElement = (Element) fieldNode;
                    field_number=fieldElement.getAttribute("number")
                    print "number : " + field_number
                    field_name=fieldElement.getAttribute("name");
                    print "Field Name : " + field_name
                    if tag == field_number:
                        return field_name
        except Exception, e:
            raise e
        return field_name
    
    def getFieldName(self,group,tag):
        field_name=""
        try:
            fixdic = File("data/FIX44.xml")
            dbFactory = DocumentBuilderFactory.newInstance()
            dBuilder = dbFactory.newDocumentBuilder()
            parser = dBuilder.parse(fixdic)
            parser.getDocumentElement().normalize()
            fieldList = parser.getElementsByTagName("field")

            for i in range(fieldList.getLength()):
                fieldNode = fieldList.item(i)
                if (fieldNode.getNodeType() == Node.ELEMENT_NODE) {
                    Element fieldElement = (Element) fieldNode;
                    String field_number=fieldElement.getAttribute("number");
                    field_name=fieldElement.getAttribute("name");
                    if(group.equals(field_number)){
                        NodeList value=fieldElement.getElementsByTagName("value");
                        for leaf in range(value.getLength()):
                            valueNode=value.item(leaf)
                            valueElement=(Element)valueNode
                            num=valueElement.getAttribute("enum")
                            field_name=valueElement.getAttribute("description")
                            if tag == num:
                                return field_name;
                        return field_name; 
        except Exception, e:
            raise e
        return field_name

    def getValue(self,s):
        if s.find("=") > 0: 
            s=s[s.find("=") + 1:]
        
        return s

    def getNum(self,s):
        if s.find("=") > 0: 
            s=s[s.find("=") + 1:]
        
        return s
    
    def getTag(self,s):
        if s.find("=") > 0: 
            s=s[0:s.find("=")]
        return s