# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: post_service.proto
# Protobuf Python Version: 6.30.1
"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC, 6, 30, 1, "", "post_service.proto"
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x12post_service.proto\x12\x04post"D\n\x11\x43reatePostRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t"!\n\x0eGetPostRequest\x12\x0f\n\x07post_id\x18\x01 \x01(\t"D\n\x10ListPostsRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x0c\n\x04page\x18\x02 \x01(\x05\x12\x11\n\tpage_size\x18\x03 \x01(\x05"=\n\x11ListPostsResponse\x12\x19\n\x05posts\x18\x01 \x03(\x0b\x32\n.post.Post\x12\r\n\x05total\x18\x02 \x01(\x05"D\n\x11UpdatePostRequest\x12\x0f\n\x07post_id\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t"5\n\x11\x44\x65letePostRequest\x12\x0f\n\x07post_id\x18\x01 \x01(\t\x12\x0f\n\x07user_id\x18\x02 \x01(\t"%\n\x12\x44\x65letePostResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08"k\n\x04Post\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0f\n\x07user_id\x18\x02 \x01(\t\x12\r\n\x05title\x18\x03 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x04 \x01(\t\x12\x12\n\ncreated_at\x18\x05 \x01(\t\x12\x12\n\nupdated_at\x18\x06 \x01(\t2\x9f\x02\n\x0bPostService\x12\x31\n\nCreatePost\x12\x17.post.CreatePostRequest\x1a\n.post.Post\x12+\n\x07GetPost\x12\x14.post.GetPostRequest\x1a\n.post.Post\x12<\n\tListPosts\x12\x16.post.ListPostsRequest\x1a\x17.post.ListPostsResponse\x12\x31\n\nUpdatePost\x12\x17.post.UpdatePostRequest\x1a\n.post.Post\x12?\n\nDeletePost\x12\x17.post.DeletePostRequest\x1a\x18.post.DeletePostResponseb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "post_service_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_CREATEPOSTREQUEST"]._serialized_start = 28
    _globals["_CREATEPOSTREQUEST"]._serialized_end = 96
    _globals["_GETPOSTREQUEST"]._serialized_start = 98
    _globals["_GETPOSTREQUEST"]._serialized_end = 131
    _globals["_LISTPOSTSREQUEST"]._serialized_start = 133
    _globals["_LISTPOSTSREQUEST"]._serialized_end = 201
    _globals["_LISTPOSTSRESPONSE"]._serialized_start = 203
    _globals["_LISTPOSTSRESPONSE"]._serialized_end = 264
    _globals["_UPDATEPOSTREQUEST"]._serialized_start = 266
    _globals["_UPDATEPOSTREQUEST"]._serialized_end = 334
    _globals["_DELETEPOSTREQUEST"]._serialized_start = 336
    _globals["_DELETEPOSTREQUEST"]._serialized_end = 389
    _globals["_DELETEPOSTRESPONSE"]._serialized_start = 391
    _globals["_DELETEPOSTRESPONSE"]._serialized_end = 428
    _globals["_POST"]._serialized_start = 430
    _globals["_POST"]._serialized_end = 537
    _globals["_POSTSERVICE"]._serialized_start = 540
    _globals["_POSTSERVICE"]._serialized_end = 827
# @@protoc_insertion_point(module_scope)
