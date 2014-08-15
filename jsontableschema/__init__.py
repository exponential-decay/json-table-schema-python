#!/usr/bin/env python
#coding: utf-8
#
# json-table-schema, an implementation of the JSON Table Schema format,
# by Martin Keegan
#
# Original: https://github.com/mk270/json-table-schema-python
# (Copyright (C) 2013  Martin Keegan)
#
# Latest, provides partial support for 1.0-pre3.1
# Copyright (C) 2014  Ross Spencer
#
# More info: http://www.dataprotocols.org/en/latest/json-table-schema.html
#
# This programme is free software; you may redistribute and/or modify
# it under the terms of the Apache Software Licence v2.0

import json
import sys

class FormatError(Exception): pass
class DuplicateFieldId(Exception): pass
class NotJSONError(Exception): pass

class JSONTableSchema(object):

   __valid_type_names__ = [
      ["string", "http://www.w3.org/2001/XMLSchema#string"],                                                               # a string (of arbitrary length)
      ["number", "http://www.w3.org/2001/XMLSchema#float"],                                                                # a number including floating point numbers
      ["integer", "http://www.w3.org/2001/XMLSchema#int", "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"],          # an integer
      ["date"],                                                                                                            # a date. This MUST be in ISO6801 format YYYY-MM-DD or, if not, a format field must describe the structure
      ["time"],                                                                                                            # a time without a date
      ["date-time", "http://www.w3.org/2001/XMLSchema#dateTime"],                                                          # a date-time. This MUST be in ISO8601 format of YYYY-MM-DDThh:mm:ssZ in UTC time or, if not, a format field must be provided
      ["boolean", "http://www.w3.org/2001/XMLSchema#boolean"],                                                             # a boolean value (1/0, true/false)
      ["binary"],                                                                                                          # base64 representation of binary data
      ["object", "http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/mapping-object-type.html"],        # (alias json) a JSON-encoded object
      ["geopoint", "http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/mapping-geo-point-type.html"],   # has one of the following structures
      ["geojson"],                                                                                                         # as per <<http://http://geojson.org/>>
      ["array", "http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/mapping-array-type.html"],          # an array
      ["any", "http://www.w3.org/2001/XMLSchema#anyURI"]                                                                   # value of field may be any type
   ]

   __format_version__ = "1.0-pre3.1"

   required_field_descriptor_keys = ["name", "type"]

   def __init__(self, json_string=None):
      # Initialise JSONTableSchema object, optionally from a JSON string
      
      self.fields = []
      self.format_version = self.__format_version__
      
      if json_string is not None:
         try:
            self.read_json(json.loads(json_string))
         except ValueError:
            sys.stderr.write("Invalid JSON object the likely cause. Please chack and try again.")
        
   def read_json(self, json_string):
      
      if "fields" not in json_string:
         raise FormatError("JSON array `fields' must be present JSON Table Schema hash.")
 
      field_list = json_string["fields"]
      if not isinstance(field_list, list):
         raise FormatError("JSON key `fields' must be array")

      for i, stanza in enumerate(field_list):
      
         if not isinstance(stanza, dict):
            err_str = "Field descriptor %d must be a dictionary" % idx
            raise FormatError(err_str)

         for key in self.required_field_descriptor_keys:
            if key not in stanza:
               err_tmpl = "Field descriptor %d must contain key `%s'" % (i, key)
               raise FormatError(err_tmpl)

         self.add_field(field_name=stanza["name"], field_type=stanza["type"])

         self.format_version = json_string.get("json_table_schema_version",
            self.__format_version__)

   @property
   def field_ids(self):
      return [ i["name"] for i in self.fields ]
            
   def add_field(self, field_name=None, field_type=None):
      if not isinstance(field_name, (str, unicode)):
         raise FormatError("Field `name' must be a string")
      if not isinstance(field_type, (str, unicode)):
         raise FormatError("Field `type' must be a string")

      if field_name in self.field_ids:
         raise DuplicateFieldId("field_name")
      
      self.check_type(field_type, field_name)

      self.fields.append({
         "name": field_name,
         "type": field_type
      })
        
   def remove_field(self, field_id):
      if field_id not in self.field_ids:
         raise KeyError
      self.fields = filter(lambda i: i["id"] != field_id, self.fields)

   def as_json(self):
      return json.dumps(self.as_dict(), indent=2)

   def as_dict(self):
      return {
         "json_table_schema_version": self.format_version, "fields": self.fields
      }

   def check_type(self, field_type, field_name):
      type_found = False
      for field_category in self.__valid_type_names__:
         for type in field_category:
            if field_type == type:
               type_found = True
               break
      
      if type_found != True:
         err_tmpl = "Invalid type `%s' in field descriptor for `%s'" % (field_type, field_name)
         raise FormatError(err_tmpl)
         
         
 