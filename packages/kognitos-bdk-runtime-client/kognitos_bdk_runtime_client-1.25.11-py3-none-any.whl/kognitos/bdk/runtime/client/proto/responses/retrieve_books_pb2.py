"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 5, 27, 3, '', 'responses/retrieve_books.proto')
_sym_db = _symbol_database.Default()
from ..types import book_descriptor_pb2 as types_dot_book__descriptor__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1eresponses/retrieve_books.proto\x12\x08protocol\x1a\x1btypes/book_descriptor.proto"G\n\x15RetrieveBooksResponse\x12.\n\x05books\x18\x01 \x03(\x0b2\x18.protocol.BookDescriptorR\x05booksB\x1fZ\x1dgithub.com/kognitos/bdk-protob\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'responses.retrieve_books_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'Z\x1dgithub.com/kognitos/bdk-proto'
    _globals['_RETRIEVEBOOKSRESPONSE']._serialized_start = 73
    _globals['_RETRIEVEBOOKSRESPONSE']._serialized_end = 144