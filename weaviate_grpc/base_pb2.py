# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: base.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nbase.proto\x12\x0cweaviategrpc\x1a\x1cgoogle/protobuf/struct.proto\":\n\x15NumberArrayProperties\x12\x0e\n\x06values\x18\x01 \x03(\x01\x12\x11\n\tprop_name\x18\x02 \x01(\t\"7\n\x12IntArrayProperties\x12\x0e\n\x06values\x18\x01 \x03(\x03\x12\x11\n\tprop_name\x18\x02 \x01(\t\"8\n\x13TextArrayProperties\x12\x0e\n\x06values\x18\x01 \x03(\t\x12\x11\n\tprop_name\x18\x02 \x01(\t\";\n\x16\x42ooleanArrayProperties\x12\x0e\n\x06values\x18\x01 \x03(\x08\x12\x11\n\tprop_name\x18\x02 \x01(\t\"\xdd\x03\n\x15ObjectPropertiesValue\x12\x33\n\x12non_ref_properties\x18\x01 \x01(\x0b\x32\x17.google.protobuf.Struct\x12\x44\n\x17number_array_properties\x18\x02 \x03(\x0b\x32#.weaviategrpc.NumberArrayProperties\x12>\n\x14int_array_properties\x18\x03 \x03(\x0b\x32 .weaviategrpc.IntArrayProperties\x12@\n\x15text_array_properties\x18\x04 \x03(\x0b\x32!.weaviategrpc.TextArrayProperties\x12\x46\n\x18\x62oolean_array_properties\x18\x05 \x03(\x0b\x32$.weaviategrpc.BooleanArrayProperties\x12\x39\n\x11object_properties\x18\x06 \x03(\x0b\x32\x1e.weaviategrpc.ObjectProperties\x12\x44\n\x17object_array_properties\x18\x07 \x03(\x0b\x32#.weaviategrpc.ObjectArrayProperties\"_\n\x15ObjectArrayProperties\x12\x33\n\x06values\x18\x01 \x03(\x0b\x32#.weaviategrpc.ObjectPropertiesValue\x12\x11\n\tprop_name\x18\x02 \x01(\t\"Y\n\x10ObjectProperties\x12\x32\n\x05value\x18\x01 \x01(\x0b\x32#.weaviategrpc.ObjectPropertiesValue\x12\x11\n\tprop_name\x18\x02 \x01(\t*\x89\x01\n\x10\x43onsistencyLevel\x12!\n\x1d\x43ONSISTENCY_LEVEL_UNSPECIFIED\x10\x00\x12\x19\n\x15\x43ONSISTENCY_LEVEL_ONE\x10\x01\x12\x1c\n\x18\x43ONSISTENCY_LEVEL_QUORUM\x10\x02\x12\x19\n\x15\x43ONSISTENCY_LEVEL_ALL\x10\x03\x42\x64\n\x19io.weaviate.grpc.protocolB\x11WeaviateProtoBaseZ4github.com/weaviate/weaviate/grpc/generated;protocolb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'base_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\031io.weaviate.grpc.protocolB\021WeaviateProtoBaseZ4github.com/weaviate/weaviate/grpc/generated;protocol'
  _globals['_CONSISTENCYLEVEL']._serialized_start=963
  _globals['_CONSISTENCYLEVEL']._serialized_end=1100
  _globals['_NUMBERARRAYPROPERTIES']._serialized_start=58
  _globals['_NUMBERARRAYPROPERTIES']._serialized_end=116
  _globals['_INTARRAYPROPERTIES']._serialized_start=118
  _globals['_INTARRAYPROPERTIES']._serialized_end=173
  _globals['_TEXTARRAYPROPERTIES']._serialized_start=175
  _globals['_TEXTARRAYPROPERTIES']._serialized_end=231
  _globals['_BOOLEANARRAYPROPERTIES']._serialized_start=233
  _globals['_BOOLEANARRAYPROPERTIES']._serialized_end=292
  _globals['_OBJECTPROPERTIESVALUE']._serialized_start=295
  _globals['_OBJECTPROPERTIESVALUE']._serialized_end=772
  _globals['_OBJECTARRAYPROPERTIES']._serialized_start=774
  _globals['_OBJECTARRAYPROPERTIES']._serialized_end=869
  _globals['_OBJECTPROPERTIES']._serialized_start=871
  _globals['_OBJECTPROPERTIES']._serialized_end=960
# @@protoc_insertion_point(module_scope)