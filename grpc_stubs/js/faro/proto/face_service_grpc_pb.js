// GENERATED CODE -- DO NOT EDIT!

// Original file comments:
//
// MIT License
//
// Copyright 2019 Oak Ridge National Laboratory
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//
'use strict';
var grpc = require('grpc');
var faro_proto_face_service_pb = require('../../faro/proto/face_service_pb.js');
var faro_proto_image_pb = require('../../faro/proto/image_pb.js');
var faro_proto_geometry_pb = require('../../faro/proto/geometry_pb.js');

function serialize_DetectExtractEnrollRequest(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.DetectExtractEnrollRequest)) {
    throw new Error('Expected argument of type DetectExtractEnrollRequest');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_DetectExtractEnrollRequest(buffer_arg) {
  return faro_proto_face_service_pb.DetectExtractEnrollRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_DetectExtractRequest(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.DetectExtractRequest)) {
    throw new Error('Expected argument of type DetectExtractRequest');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_DetectExtractRequest(buffer_arg) {
  return faro_proto_face_service_pb.DetectExtractRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_DetectExtractSearchRequest(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.DetectExtractSearchRequest)) {
    throw new Error('Expected argument of type DetectExtractSearchRequest');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_DetectExtractSearchRequest(buffer_arg) {
  return faro_proto_face_service_pb.DetectExtractSearchRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_DetectRequest(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.DetectRequest)) {
    throw new Error('Expected argument of type DetectRequest');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_DetectRequest(buffer_arg) {
  return faro_proto_face_service_pb.DetectRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_Empty(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.Empty)) {
    throw new Error('Expected argument of type Empty');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_Empty(buffer_arg) {
  return faro_proto_face_service_pb.Empty.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_EnrollRequest(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.EnrollRequest)) {
    throw new Error('Expected argument of type EnrollRequest');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_EnrollRequest(buffer_arg) {
  return faro_proto_face_service_pb.EnrollRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_EnrollmentDeleteRequest(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.EnrollmentDeleteRequest)) {
    throw new Error('Expected argument of type EnrollmentDeleteRequest');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_EnrollmentDeleteRequest(buffer_arg) {
  return faro_proto_face_service_pb.EnrollmentDeleteRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_EnrollmentListRequest(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.EnrollmentListRequest)) {
    throw new Error('Expected argument of type EnrollmentListRequest');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_EnrollmentListRequest(buffer_arg) {
  return faro_proto_face_service_pb.EnrollmentListRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_ExtractRequest(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.ExtractRequest)) {
    throw new Error('Expected argument of type ExtractRequest');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_ExtractRequest(buffer_arg) {
  return faro_proto_face_service_pb.ExtractRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_FaceRecordList(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.FaceRecordList)) {
    throw new Error('Expected argument of type FaceRecordList');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_FaceRecordList(buffer_arg) {
  return faro_proto_face_service_pb.FaceRecordList.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_FaceServiceInfo(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.FaceServiceInfo)) {
    throw new Error('Expected argument of type FaceServiceInfo');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_FaceServiceInfo(buffer_arg) {
  return faro_proto_face_service_pb.FaceServiceInfo.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_FaceStatusRequest(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.FaceStatusRequest)) {
    throw new Error('Expected argument of type FaceStatusRequest');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_FaceStatusRequest(buffer_arg) {
  return faro_proto_face_service_pb.FaceStatusRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_GalleryDeleteRequest(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.GalleryDeleteRequest)) {
    throw new Error('Expected argument of type GalleryDeleteRequest');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_GalleryDeleteRequest(buffer_arg) {
  return faro_proto_face_service_pb.GalleryDeleteRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_GalleryList(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.GalleryList)) {
    throw new Error('Expected argument of type GalleryList');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_GalleryList(buffer_arg) {
  return faro_proto_face_service_pb.GalleryList.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_GalleryListRequest(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.GalleryListRequest)) {
    throw new Error('Expected argument of type GalleryListRequest');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_GalleryListRequest(buffer_arg) {
  return faro_proto_face_service_pb.GalleryListRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_Matrix(arg) {
  if (!(arg instanceof faro_proto_geometry_pb.Matrix)) {
    throw new Error('Expected argument of type Matrix');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_Matrix(buffer_arg) {
  return faro_proto_geometry_pb.Matrix.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_ScoreRequest(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.ScoreRequest)) {
    throw new Error('Expected argument of type ScoreRequest');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_ScoreRequest(buffer_arg) {
  return faro_proto_face_service_pb.ScoreRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_SearchRequest(arg) {
  if (!(arg instanceof faro_proto_face_service_pb.SearchRequest)) {
    throw new Error('Expected argument of type SearchRequest');
  }
  return new Buffer(arg.serializeBinary());
}

function deserialize_SearchRequest(buffer_arg) {
  return faro_proto_face_service_pb.SearchRequest.deserializeBinary(new Uint8Array(buffer_arg));
}


var FaceRecognitionService = exports.FaceRecognitionService = {
  // Service info and defaults
  status: {
    path: '/FaceRecognition/status',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.FaceStatusRequest,
    responseType: faro_proto_face_service_pb.FaceServiceInfo,
    requestSerialize: serialize_FaceStatusRequest,
    requestDeserialize: deserialize_FaceStatusRequest,
    responseSerialize: serialize_FaceServiceInfo,
    responseDeserialize: deserialize_FaceServiceInfo,
  },
  // Simple operations
  detect: {
    path: '/FaceRecognition/detect',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.DetectRequest,
    responseType: faro_proto_face_service_pb.FaceRecordList,
    requestSerialize: serialize_DetectRequest,
    requestDeserialize: deserialize_DetectRequest,
    responseSerialize: serialize_FaceRecordList,
    responseDeserialize: deserialize_FaceRecordList,
  },
  extract: {
    path: '/FaceRecognition/extract',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.ExtractRequest,
    responseType: faro_proto_face_service_pb.FaceRecordList,
    requestSerialize: serialize_ExtractRequest,
    requestDeserialize: deserialize_ExtractRequest,
    responseSerialize: serialize_FaceRecordList,
    responseDeserialize: deserialize_FaceRecordList,
  },
  score: {
    path: '/FaceRecognition/score',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.ScoreRequest,
    responseType: faro_proto_geometry_pb.Matrix,
    requestSerialize: serialize_ScoreRequest,
    requestDeserialize: deserialize_ScoreRequest,
    responseSerialize: serialize_Matrix,
    responseDeserialize: deserialize_Matrix,
  },
  enroll: {
    path: '/FaceRecognition/enroll',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.EnrollRequest,
    responseType: faro_proto_face_service_pb.FaceRecordList,
    requestSerialize: serialize_EnrollRequest,
    requestDeserialize: deserialize_EnrollRequest,
    responseSerialize: serialize_FaceRecordList,
    responseDeserialize: deserialize_FaceRecordList,
  },
  search: {
    path: '/FaceRecognition/search',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.SearchRequest,
    responseType: faro_proto_face_service_pb.FaceRecordList,
    requestSerialize: serialize_SearchRequest,
    requestDeserialize: deserialize_SearchRequest,
    responseSerialize: serialize_FaceRecordList,
    responseDeserialize: deserialize_FaceRecordList,
  },
  // Combined opperations
  detectExtract: {
    path: '/FaceRecognition/detectExtract',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.DetectExtractRequest,
    responseType: faro_proto_face_service_pb.FaceRecordList,
    requestSerialize: serialize_DetectExtractRequest,
    requestDeserialize: deserialize_DetectExtractRequest,
    responseSerialize: serialize_FaceRecordList,
    responseDeserialize: deserialize_FaceRecordList,
  },
  detectExtractEnroll: {
    path: '/FaceRecognition/detectExtractEnroll',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.DetectExtractEnrollRequest,
    responseType: faro_proto_face_service_pb.FaceRecordList,
    requestSerialize: serialize_DetectExtractEnrollRequest,
    requestDeserialize: deserialize_DetectExtractEnrollRequest,
    responseSerialize: serialize_FaceRecordList,
    responseDeserialize: deserialize_FaceRecordList,
  },
  detectExtractSearch: {
    path: '/FaceRecognition/detectExtractSearch',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.DetectExtractSearchRequest,
    responseType: faro_proto_face_service_pb.FaceRecordList,
    requestSerialize: serialize_DetectExtractSearchRequest,
    requestDeserialize: deserialize_DetectExtractSearchRequest,
    responseSerialize: serialize_FaceRecordList,
    responseDeserialize: deserialize_FaceRecordList,
  },
  // Gallery Management
  galleryList: {
    path: '/FaceRecognition/galleryList',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.GalleryListRequest,
    responseType: faro_proto_face_service_pb.GalleryList,
    requestSerialize: serialize_GalleryListRequest,
    requestDeserialize: deserialize_GalleryListRequest,
    responseSerialize: serialize_GalleryList,
    responseDeserialize: deserialize_GalleryList,
  },
  galleryDelete: {
    path: '/FaceRecognition/galleryDelete',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.GalleryDeleteRequest,
    responseType: faro_proto_face_service_pb.Empty,
    requestSerialize: serialize_GalleryDeleteRequest,
    requestDeserialize: deserialize_GalleryDeleteRequest,
    responseSerialize: serialize_Empty,
    responseDeserialize: deserialize_Empty,
  },
  enrollmentList: {
    path: '/FaceRecognition/enrollmentList',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.EnrollmentListRequest,
    responseType: faro_proto_face_service_pb.FaceRecordList,
    requestSerialize: serialize_EnrollmentListRequest,
    requestDeserialize: deserialize_EnrollmentListRequest,
    responseSerialize: serialize_FaceRecordList,
    responseDeserialize: deserialize_FaceRecordList,
  },
  enrollmentDelete: {
    path: '/FaceRecognition/enrollmentDelete',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.EnrollmentDeleteRequest,
    responseType: faro_proto_face_service_pb.FaceRecordList,
    requestSerialize: serialize_EnrollmentDeleteRequest,
    requestDeserialize: deserialize_EnrollmentDeleteRequest,
    responseSerialize: serialize_FaceRecordList,
    responseDeserialize: deserialize_FaceRecordList,
  },
  enrollmentDeleteConditional: {
    path: '/FaceRecognition/enrollmentDeleteConditional',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.EnrollmentDeleteRequest,
    responseType: faro_proto_face_service_pb.FaceRecordList,
    requestSerialize: serialize_EnrollmentDeleteRequest,
    requestDeserialize: deserialize_EnrollmentDeleteRequest,
    responseSerialize: serialize_FaceRecordList,
    responseDeserialize: deserialize_FaceRecordList,
  },
  enrollmentTransfer: {
    path: '/FaceRecognition/enrollmentTransfer',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_face_service_pb.EnrollmentDeleteRequest,
    responseType: faro_proto_face_service_pb.FaceRecordList,
    requestSerialize: serialize_EnrollmentDeleteRequest,
    requestDeserialize: deserialize_EnrollmentDeleteRequest,
    responseSerialize: serialize_FaceRecordList,
    responseDeserialize: deserialize_FaceRecordList,
  },
  // Test
  echo: {
    path: '/FaceRecognition/echo',
    requestStream: false,
    responseStream: false,
    requestType: faro_proto_geometry_pb.Matrix,
    responseType: faro_proto_geometry_pb.Matrix,
    requestSerialize: serialize_Matrix,
    requestDeserialize: deserialize_Matrix,
    responseSerialize: serialize_Matrix,
    responseDeserialize: deserialize_Matrix,
  },
};

exports.FaceRecognitionClient = grpc.makeGenericClientConstructor(FaceRecognitionService);
