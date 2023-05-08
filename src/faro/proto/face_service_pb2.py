# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: faro/proto/face_service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from faro.proto import image_pb2 as faro_dot_proto_dot_image__pb2
from faro.proto import geometry_pb2 as faro_dot_proto_dot_geometry__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1d\x66\x61ro/proto/face_service.proto\x1a\x16\x66\x61ro/proto/image.proto\x1a\x19\x66\x61ro/proto/geometry.proto\"\x8d\x02\n\tAttribute\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\x12\x0e\n\x06\x62uffer\x18\x03 \x01(\x0c\x12\x0e\n\x06\x66value\x18\x04 \x01(\x02\x12\x0e\n\x06ivalue\x18\x05 \x01(\x05\x12\x0c\n\x04text\x18\x06 \x01(\t\x12\x0e\n\x06pickle\x18\x07 \x01(\x0c\x12\x0c\n\x04json\x18\x08 \x01(\x0c\x12\x17\n\x06matrix\x18\t \x01(\x0b\x32\x07.Matrix\x12\x17\n\x06vector\x18\n \x01(\x0b\x32\x07.Vector\x12\x15\n\x05image\x18\x0b \x01(\x0b\x32\x06.Image\x12\x17\n\x05point\x18\x0c \x01(\x0b\x32\x08.Point2D\x12\x13\n\x04rect\x18\r \x01(\x0b\x32\x05.Rect\x12\x0b\n\x03xml\x18\x0e \x01(\x0c\"9\n\x0c\x45rrorMessage\x12\x12\n\nerror_code\x18\x03 \x01(\x05\x12\x15\n\rerror_message\x18\x04 \x01(\t\"\x82\x01\n\tDetection\x12\r\n\x05score\x18\x01 \x01(\x02\x12\x17\n\x08location\x18\x02 \x01(\x0b\x32\x05.Rect\x12\x14\n\x0c\x64\x65tection_id\x18\x03 \x01(\x05\x12\x17\n\x0f\x64\x65tection_class\x18\x04 \x01(\t\x12\x1e\n\nattributes\x18\x05 \x03(\x0b\x32\n.Attribute\";\n\x08Landmark\x12\x13\n\x0blandmark_id\x18\x01 \x01(\t\x12\x1a\n\x08location\x18\x02 \x01(\x0b\x32\x08.Point2D\"\xf5\x01\n\x10\x44\x65tectionOptions\x12\x14\n\x0c\x61lgorithm_id\x18\x01 \x01(\t\x12\x0c\n\x04\x62\x65st\x18\x02 \x01(\x08\x12\x11\n\tthreshold\x18\x03 \x01(\x02\x12\x14\n\x0cscale_levels\x18\x04 \x01(\x05\x12\x13\n\x0bscan_levels\x18\x05 \x01(\x05\x12\x14\n\x0cscan_overlap\x18\x06 \x01(\x02\x12\x10\n\x08min_size\x18\x07 \x01(\x05\x12\x14\n\x0csave_request\x18\t \x01(\x08\x12\r\n\x05\x64\x65\x62ug\x18\n \x01(\x08\x12\x12\n\ndownsample\x18\x0b \x01(\x05\x12\x1e\n\nattributes\x18\x08 \x03(\x0b\x32\n.Attribute\"k\n\x0e\x45xtractOptions\x12\x14\n\x0c\x61lgorithm_id\x18\x01 \x01(\t\x12\x14\n\x0csave_request\x18\x02 \x01(\x08\x12\r\n\x05\x64\x65\x62ug\x18\x03 \x01(\x08\x12\x1e\n\nattributes\x18\x08 \x03(\x0b\x32\n.Attribute\"T\n\rEnrollOptions\x12\x14\n\x0csave_request\x18\x02 \x01(\x08\x12\r\n\x05\x64\x65\x62ug\x18\x03 \x01(\x08\x12\x1e\n\nattributes\x18\x08 \x03(\x0b\x32\n.Attribute\"\xaf\x01\n\rDetectionList\x12\x1e\n\ndetections\x18\x01 \x03(\x0b\x32\n.Detection\x12\x16\n\x0e\x64\x65tection_time\x18\x02 \x01(\x02\x12\x13\n\x0bimage_width\x18\x03 \x01(\x05\x12\x14\n\x0cimage_height\x18\x04 \x01(\x05\x12\x17\n\x0f\x64\x65tection_count\x18\x05 \x01(\x05\x12\"\n\x07options\x18\x06 \x01(\x0b\x32\x11.DetectionOptions\"+\n\tMatchList\x12\x1e\n\nmatch_list\x18\x01 \x03(\x0b\x32\n.MatchInfo\"\x82\x01\n\tMatchInfo\x12\r\n\x05score\x18\x01 \x01(\x02\x12\x10\n\x08image_id\x18\x02 \x01(\t\x12\x14\n\x0c\x64\x65tection_id\x18\x03 \x01(\t\x12\x12\n\nsubject_id\x18\x04 \x01(\t\x12\x14\n\x0csubject_name\x18\x05 \x01(\t\x12\x14\n\x04\x66\x61\x63\x65\x18\x06 \x01(\x0b\x32\x06.Image\">\n\rTemplateInput\x12\x12\n\x02im\x18\x01 \x01(\x0b\x32\x06.Image\x12\x19\n\ndetections\x18\x02 \x03(\x0b\x32\x05.Rect\"H\n\x0c\x46\x61\x63\x65Template\x12\x15\n\x04\x64\x61ta\x18\x01 \x01(\x0b\x32\x07.Vector\x12\x0e\n\x06\x62uffer\x18\x02 \x01(\x0c\x12\x11\n\talgorithm\x18\x03 \x01(\t\"0\n\x0cTemplateList\x12 \n\ttemplates\x18\x01 \x03(\x0b\x32\r.FaceTemplate\"a\n\x0c\x41\x63\x63\x65ssRecord\x12\x10\n\x08\x64\x61tetime\x18\x01 \x01(\x02\x12\r\n\x05notes\x18\x02 \x01(\t\x12\x12\n\ncredential\x18\x03 \x01(\t\x12\x1c\n\x08metadata\x18\x04 \x03(\x0b\x32\n.Attribute\"\x83\x04\n\nFaceRecord\x12\x12\n\nsubject_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x05 \x01(\t\x12\x0e\n\x06source\x18\x04 \x01(\t\x12\r\n\x05\x66rame\x18\x0e \x01(\x03\x12\x11\n\talgorithm\x18\x14 \x01(\t\x12\r\n\x05notes\x18\x06 \x01(\t\x12\x13\n\x0bgallery_key\x18\x0f \x01(\t\x12\x17\n\x0f\x63ollection_date\x18\x10 \x01(\x02\x12\x17\n\x0f\x65nrollment_date\x18\x11 \x01(\x02\x12\x1c\n\x08metadata\x18\x12 \x03(\x0b\x32\n.Attribute\x12%\n\x0e\x61\x63\x63\x65ss_records\x18\x13 \x03(\x0b\x32\r.AccessRecord\x12\x14\n\x04view\x18\x07 \x01(\x0b\x32\x06.Image\x12\x17\n\x07\x61ligned\x18\t \x01(\x0b\x32\x06.Image\x12\x1d\n\tdetection\x18\x02 \x01(\x0b\x32\n.Detection\x12\x1c\n\tlandmarks\x18\x08 \x03(\x0b\x32\t.Landmark\x12\x1e\n\nattributes\x18\n \x03(\x0b\x32\n.Attribute\x12!\n\rinternal_data\x18\x0b \x03(\x0b\x32\n.Attribute\x12\x1f\n\x08template\x18\x03 \x01(\x0b\x32\r.FaceTemplate\x12\r\n\x05score\x18\x0c \x01(\x02\x12\'\n\x0esearch_results\x18\r \x01(\x0b\x32\x0f.FaceRecordList\"3\n\x0e\x46\x61\x63\x65RecordList\x12!\n\x0c\x66\x61\x63\x65_records\x18\x01 \x03(\x0b\x32\x0b.FaceRecord\"\\\n\x13VerificationRequest\x12\x0f\n\x07gallery\x18\x01 \x01(\t\x12\x12\n\nsubject_id\x18\x02 \x01(\t\x12 \n\x0b\x66\x61\x63\x65_record\x18\x03 \x03(\x0b\x32\x0b.FaceRecord\"\x84\x01\n\x14VerificationResponse\x12\x12\n\nerror_code\x18\x04 \x01(\x05\x12\x15\n\rerror_message\x18\x05 \x01(\t\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x12\n\nconfidence\x18\x02 \x01(\x02\x12\x1c\n\x07matches\x18\x03 \x03(\x0b\x32\x0b.FaceRecord\"p\n\rSearchRequest\x12\x16\n\x0esearch_gallery\x18\x01 \x01(\t\x12\x1f\n\x06probes\x18\x03 \x01(\x0b\x32\x0f.FaceRecordList\x12\x13\n\x0bmax_results\x18\x04 \x01(\x05\x12\x11\n\tthreshold\x18\x05 \x01(\x02\"Q\n\x0eSearchResponse\x12\x1e\n\x07message\x18\x01 \x01(\x0b\x32\r.ErrorMessage\x12\x1f\n\x06probes\x18\x02 \x01(\x0b\x32\x0f.FaceRecordList\"q\n\rEnrollRequest\x12\x16\n\x0e\x65nroll_gallery\x18\x01 \x01(\t\x12 \n\x07records\x18\x02 \x01(\x0b\x32\x0f.FaceRecordList\x12&\n\x0e\x65nroll_options\x18\n \x01(\x0b\x32\x0e.EnrollOptions\"\x9a\x01\n\rDetectRequest\x12\x15\n\x05image\x18\x01 \x01(\x0b\x32\x06.Image\x12\x0e\n\x06source\x18\x02 \x01(\t\x12\r\n\x05\x66rame\x18\x03 \x01(\x03\x12\x12\n\nsubject_id\x18\x04 \x01(\t\x12\x14\n\x0csubject_name\x18\x05 \x01(\t\x12)\n\x0e\x64\x65tect_options\x18\x08 \x01(\x0b\x32\x11.DetectionOptions\"s\n\x0e\x45xtractRequest\x12\x15\n\x05image\x18\x01 \x01(\x0b\x32\x06.Image\x12 \n\x07records\x18\x04 \x01(\x0b\x32\x0f.FaceRecordList\x12(\n\x0f\x65xtract_options\x18\t \x01(\x0b\x32\x0f.ExtractOptions\"\xac\x01\n\x0cScoreRequest\x12$\n\x0b\x66\x61\x63\x65_probes\x18\x01 \x01(\x0b\x32\x0f.FaceRecordList\x12%\n\x0c\x66\x61\x63\x65_gallery\x18\x02 \x01(\x0b\x32\x0f.FaceRecordList\x12&\n\x0ftemplate_probes\x18\x03 \x01(\x0b\x32\r.TemplateList\x12\'\n\x10template_gallery\x18\x04 \x01(\x0b\x32\r.TemplateList\"h\n\x14\x44\x65tectExtractRequest\x12&\n\x0e\x64\x65tect_request\x18\x01 \x01(\x0b\x32\x0e.DetectRequest\x12(\n\x0f\x65xtract_request\x18\x02 \x01(\x0b\x32\x0f.ExtractRequest\"\x96\x01\n\x1a\x44\x65tectExtractEnrollRequest\x12&\n\x0e\x64\x65tect_request\x18\x01 \x01(\x0b\x32\x0e.DetectRequest\x12(\n\x0f\x65xtract_request\x18\x02 \x01(\x0b\x32\x0f.ExtractRequest\x12&\n\x0e\x65nroll_request\x18\x03 \x01(\x0b\x32\x0e.EnrollRequest\"\x96\x01\n\x1a\x44\x65tectExtractSearchRequest\x12&\n\x0e\x64\x65tect_request\x18\x01 \x01(\x0b\x32\x0e.DetectRequest\x12(\n\x0f\x65xtract_request\x18\x02 \x01(\x0b\x32\x0f.ExtractRequest\x12&\n\x0esearch_request\x18\x03 \x01(\x0b\x32\x0e.SearchRequest\"\x13\n\x11\x46\x61\x63\x65StatusRequest\"\xd2\x02\n\x0f\x46\x61\x63\x65ServiceInfo\x12\x1e\n\x06status\x18\x01 \x01(\x0e\x32\x0e.ServiceStatus\x12\x14\n\x0cworker_count\x18\x02 \x01(\x05\x12\x19\n\x11\x64\x65tection_support\x18\x03 \x01(\x08\x12\x17\n\x0f\x65xtract_support\x18\x04 \x01(\x08\x12\x15\n\rscore_support\x18\x05 \x01(\x08\x12\x19\n\x11\x61ttribute_support\x18\x06 \x01(\x08\x12\x1e\n\nscore_type\x18\x07 \x01(\x0e\x32\n.ScoreType\x12\x1b\n\x13\x64\x65tection_threshold\x18\x08 \x01(\x02\x12\x17\n\x0fmatch_threshold\x18\t \x01(\x02\x12\x11\n\talgorithm\x18\n \x01(\t\x12\r\n\x05notes\x18\x0b \x01(\t\x12\x14\n\x0c\x66\x61ro_version\x18\x0c \x01(\t\x12\x15\n\rinstance_name\x18\r \x01(\t\"\x14\n\x12GalleryListRequest\",\n\x14GalleryDeleteRequest\x12\x14\n\x0cgallery_name\x18\x01 \x01(\t\"-\n\x15\x45nrollmentListRequest\x12\x14\n\x0cgallery_name\x18\x01 \x01(\t\"F\n\x0e\x45nrollmentInfo\x12\x12\n\nsubject_id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x12\n\nface_count\x18\x03 \x01(\x05\"T\n\x16\x45nrollmentListResponse\x12\x14\n\x0cgallery_name\x18\x01 \x01(\t\x12$\n\x0b\x65nrollments\x18\x02 \x03(\x0b\x32\x0f.EnrollmentInfo\"X\n\x17\x45nrollmentDeleteRequest\x12\x14\n\x0cgallery_name\x18\x01 \x01(\t\x12\x12\n\nsubject_id\x18\x02 \x01(\t\x12\x13\n\x0bgallery_key\x18\x03 \x01(\t\"0\n\x18\x45nrollmentDeleteResponse\x12\x14\n\x0c\x64\x65lete_count\x18\x01 \x01(\x03\"7\n\x0bGalleryInfo\x12\x14\n\x0cgallery_name\x18\x01 \x01(\t\x12\x12\n\nface_count\x18\x02 \x01(\x03\".\n\x0bGalleryList\x12\x1f\n\tgalleries\x18\x01 \x03(\x0b\x32\x0c.GalleryInfo\"\x07\n\x05\x45mpty*<\n\rServiceStatus\x12\x0b\n\x07UNKNOWN\x10\x00\x12\t\n\x05READY\x10\x01\x12\t\n\x05\x45RROR\x10\x02\x12\x08\n\x04\x42USY\x10\x03*k\n\x08\x44\x61taType\x12\t\n\x05\x45MPTY\x10\x00\x12\n\n\x06STRING\x10\x01\x12\x07\n\x03INT\x10\x02\x12\t\n\x05\x46LOAT\x10\x03\x12\t\n\x05\x42YTES\x10\x04\x12\n\n\x06VECTOR\x10\x05\x12\n\n\x06PICKLE\x10\x06\x12\x07\n\x03XML\x10\x07\x12\x08\n\x04JSON\x10\x08*4\n\tScoreType\x12\n\n\x06SERVER\x10\x00\x12\x06\n\x02L1\x10\x01\x12\x06\n\x02L2\x10\x02\x12\x0b\n\x07NEG_DOT\x10\x03\x32\xe2\x06\n\x0f\x46\x61\x63\x65Recognition\x12\x30\n\x06status\x12\x12.FaceStatusRequest\x1a\x10.FaceServiceInfo\"\x00\x12+\n\x06\x64\x65tect\x12\x0e.DetectRequest\x1a\x0f.FaceRecordList\"\x00\x12-\n\x07\x65xtract\x12\x0f.ExtractRequest\x1a\x0f.FaceRecordList\"\x00\x12!\n\x05score\x12\r.ScoreRequest\x1a\x07.Matrix\"\x00\x12+\n\x06\x65nroll\x12\x0e.EnrollRequest\x1a\x0f.FaceRecordList\"\x00\x12+\n\x06search\x12\x0e.SearchRequest\x1a\x0f.FaceRecordList\"\x00\x12\x39\n\rdetectExtract\x12\x15.DetectExtractRequest\x1a\x0f.FaceRecordList\"\x00\x12\x45\n\x13\x64\x65tectExtractEnroll\x12\x1b.DetectExtractEnrollRequest\x1a\x0f.FaceRecordList\"\x00\x12\x45\n\x13\x64\x65tectExtractSearch\x12\x1b.DetectExtractSearchRequest\x1a\x0f.FaceRecordList\"\x00\x12\x32\n\x0bgalleryList\x12\x13.GalleryListRequest\x1a\x0c.GalleryList\"\x00\x12\x30\n\rgalleryDelete\x12\x15.GalleryDeleteRequest\x1a\x06.Empty\"\x00\x12;\n\x0e\x65nrollmentList\x12\x16.EnrollmentListRequest\x1a\x0f.FaceRecordList\"\x00\x12\x34\n\x10trainFromGallery\x12\x16.EnrollmentListRequest\x1a\x06.Empty\"\x00\x12\x46\n\rsubjectDelete\x12\x18.EnrollmentDeleteRequest\x1a\x19.EnrollmentDeleteResponse\"\x00\x12>\n\x19generateMatchDistribution\x12\x16.EnrollmentListRequest\x1a\x07.Matrix\"\x00\x12\x1a\n\x04\x65\x63ho\x12\x07.Matrix\x1a\x07.Matrix\"\x00\x42\r\xaa\x02\nFaro.Protob\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'faro.proto.face_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\252\002\nFaro.Proto'
  _SERVICESTATUS._serialized_start=4557
  _SERVICESTATUS._serialized_end=4617
  _DATATYPE._serialized_start=4619
  _DATATYPE._serialized_end=4726
  _SCORETYPE._serialized_start=4728
  _SCORETYPE._serialized_end=4780
  _ATTRIBUTE._serialized_start=85
  _ATTRIBUTE._serialized_end=354
  _ERRORMESSAGE._serialized_start=356
  _ERRORMESSAGE._serialized_end=413
  _DETECTION._serialized_start=416
  _DETECTION._serialized_end=546
  _LANDMARK._serialized_start=548
  _LANDMARK._serialized_end=607
  _DETECTIONOPTIONS._serialized_start=610
  _DETECTIONOPTIONS._serialized_end=855
  _EXTRACTOPTIONS._serialized_start=857
  _EXTRACTOPTIONS._serialized_end=964
  _ENROLLOPTIONS._serialized_start=966
  _ENROLLOPTIONS._serialized_end=1050
  _DETECTIONLIST._serialized_start=1053
  _DETECTIONLIST._serialized_end=1228
  _MATCHLIST._serialized_start=1230
  _MATCHLIST._serialized_end=1273
  _MATCHINFO._serialized_start=1276
  _MATCHINFO._serialized_end=1406
  _TEMPLATEINPUT._serialized_start=1408
  _TEMPLATEINPUT._serialized_end=1470
  _FACETEMPLATE._serialized_start=1472
  _FACETEMPLATE._serialized_end=1544
  _TEMPLATELIST._serialized_start=1546
  _TEMPLATELIST._serialized_end=1594
  _ACCESSRECORD._serialized_start=1596
  _ACCESSRECORD._serialized_end=1693
  _FACERECORD._serialized_start=1696
  _FACERECORD._serialized_end=2211
  _FACERECORDLIST._serialized_start=2213
  _FACERECORDLIST._serialized_end=2264
  _VERIFICATIONREQUEST._serialized_start=2266
  _VERIFICATIONREQUEST._serialized_end=2358
  _VERIFICATIONRESPONSE._serialized_start=2361
  _VERIFICATIONRESPONSE._serialized_end=2493
  _SEARCHREQUEST._serialized_start=2495
  _SEARCHREQUEST._serialized_end=2607
  _SEARCHRESPONSE._serialized_start=2609
  _SEARCHRESPONSE._serialized_end=2690
  _ENROLLREQUEST._serialized_start=2692
  _ENROLLREQUEST._serialized_end=2805
  _DETECTREQUEST._serialized_start=2808
  _DETECTREQUEST._serialized_end=2962
  _EXTRACTREQUEST._serialized_start=2964
  _EXTRACTREQUEST._serialized_end=3079
  _SCOREREQUEST._serialized_start=3082
  _SCOREREQUEST._serialized_end=3254
  _DETECTEXTRACTREQUEST._serialized_start=3256
  _DETECTEXTRACTREQUEST._serialized_end=3360
  _DETECTEXTRACTENROLLREQUEST._serialized_start=3363
  _DETECTEXTRACTENROLLREQUEST._serialized_end=3513
  _DETECTEXTRACTSEARCHREQUEST._serialized_start=3516
  _DETECTEXTRACTSEARCHREQUEST._serialized_end=3666
  _FACESTATUSREQUEST._serialized_start=3668
  _FACESTATUSREQUEST._serialized_end=3687
  _FACESERVICEINFO._serialized_start=3690
  _FACESERVICEINFO._serialized_end=4028
  _GALLERYLISTREQUEST._serialized_start=4030
  _GALLERYLISTREQUEST._serialized_end=4050
  _GALLERYDELETEREQUEST._serialized_start=4052
  _GALLERYDELETEREQUEST._serialized_end=4096
  _ENROLLMENTLISTREQUEST._serialized_start=4098
  _ENROLLMENTLISTREQUEST._serialized_end=4143
  _ENROLLMENTINFO._serialized_start=4145
  _ENROLLMENTINFO._serialized_end=4215
  _ENROLLMENTLISTRESPONSE._serialized_start=4217
  _ENROLLMENTLISTRESPONSE._serialized_end=4301
  _ENROLLMENTDELETEREQUEST._serialized_start=4303
  _ENROLLMENTDELETEREQUEST._serialized_end=4391
  _ENROLLMENTDELETERESPONSE._serialized_start=4393
  _ENROLLMENTDELETERESPONSE._serialized_end=4441
  _GALLERYINFO._serialized_start=4443
  _GALLERYINFO._serialized_end=4498
  _GALLERYLIST._serialized_start=4500
  _GALLERYLIST._serialized_end=4546
  _EMPTY._serialized_start=4548
  _EMPTY._serialized_end=4555
  _FACERECOGNITION._serialized_start=4783
  _FACERECOGNITION._serialized_end=5649
# @@protoc_insertion_point(module_scope)
