#if !defined(GPB_GRPC_FORWARD_DECLARE_MESSAGE_PROTO) || !GPB_GRPC_FORWARD_DECLARE_MESSAGE_PROTO
#import "faro/proto/FaceService.pbobjc.h"
#endif

#if !defined(GPB_GRPC_PROTOCOL_ONLY) || !GPB_GRPC_PROTOCOL_ONLY
#import <ProtoRPC/ProtoService.h>
#import <ProtoRPC/ProtoRPCLegacy.h>
#import <RxLibrary/GRXWriteable.h>
#import <RxLibrary/GRXWriter.h>
#endif

@class DetectExtractEnrollRequest;
@class DetectExtractRequest;
@class DetectExtractSearchRequest;
@class DetectRequest;
@class Empty;
@class EnrollRequest;
@class EnrollmentDeleteRequest;
@class EnrollmentListRequest;
@class ExtractRequest;
@class FaceRecordList;
@class FaceServiceInfo;
@class FaceStatusRequest;
@class GalleryDeleteRequest;
@class GalleryList;
@class GalleryListRequest;
@class Matrix;
@class ScoreRequest;
@class SearchRequest;

#if !defined(GPB_GRPC_FORWARD_DECLARE_MESSAGE_PROTO) || !GPB_GRPC_FORWARD_DECLARE_MESSAGE_PROTO
  #import "faro/proto/Image.pbobjc.h"
  #import "faro/proto/Geometry.pbobjc.h"
#endif

@class GRPCUnaryProtoCall;
@class GRPCStreamingProtoCall;
@class GRPCCallOptions;
@protocol GRPCProtoResponseHandler;
@class GRPCProtoCall;


NS_ASSUME_NONNULL_BEGIN

@protocol FaceRecognition2 <NSObject>

#pragma mark status(FaceStatusRequest) returns (FaceServiceInfo)

/**
 * Service info and defaults
 */
- (GRPCUnaryProtoCall *)statusWithMessage:(FaceStatusRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark detect(DetectRequest) returns (FaceRecordList)

/**
 * Simple operations
 */
- (GRPCUnaryProtoCall *)detectWithMessage:(DetectRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark extract(ExtractRequest) returns (FaceRecordList)

- (GRPCUnaryProtoCall *)extractWithMessage:(ExtractRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark score(ScoreRequest) returns (Matrix)

- (GRPCUnaryProtoCall *)scoreWithMessage:(ScoreRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark enroll(EnrollRequest) returns (FaceRecordList)

- (GRPCUnaryProtoCall *)enrollWithMessage:(EnrollRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark search(SearchRequest) returns (FaceRecordList)

- (GRPCUnaryProtoCall *)searchWithMessage:(SearchRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark detectExtract(DetectExtractRequest) returns (FaceRecordList)

/**
 * Combined opperations
 */
- (GRPCUnaryProtoCall *)detectExtractWithMessage:(DetectExtractRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark detectExtractEnroll(DetectExtractEnrollRequest) returns (FaceRecordList)

- (GRPCUnaryProtoCall *)detectExtractEnrollWithMessage:(DetectExtractEnrollRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark detectExtractSearch(DetectExtractSearchRequest) returns (FaceRecordList)

- (GRPCUnaryProtoCall *)detectExtractSearchWithMessage:(DetectExtractSearchRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark galleryList(GalleryListRequest) returns (GalleryList)

/**
 * Gallery Management
 */
- (GRPCUnaryProtoCall *)galleryListWithMessage:(GalleryListRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark galleryDelete(GalleryDeleteRequest) returns (Empty)

- (GRPCUnaryProtoCall *)galleryDeleteWithMessage:(GalleryDeleteRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark enrollmentList(EnrollmentListRequest) returns (FaceRecordList)

- (GRPCUnaryProtoCall *)enrollmentListWithMessage:(EnrollmentListRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark enrollmentDelete(EnrollmentDeleteRequest) returns (FaceRecordList)

- (GRPCUnaryProtoCall *)enrollmentDeleteWithMessage:(EnrollmentDeleteRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark enrollmentDeleteConditional(EnrollmentDeleteRequest) returns (FaceRecordList)

- (GRPCUnaryProtoCall *)enrollmentDeleteConditionalWithMessage:(EnrollmentDeleteRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark enrollmentTransfer(EnrollmentDeleteRequest) returns (FaceRecordList)

- (GRPCUnaryProtoCall *)enrollmentTransferWithMessage:(EnrollmentDeleteRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

#pragma mark echo(Matrix) returns (Matrix)

/**
 * Test
 */
- (GRPCUnaryProtoCall *)echoWithMessage:(Matrix *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions;

@end

/**
 * The methods in this protocol belong to a set of old APIs that have been deprecated. They do not
 * recognize call options provided in the initializer. Using the v2 protocol is recommended.
 */
@protocol FaceRecognition <NSObject>

#pragma mark status(FaceStatusRequest) returns (FaceServiceInfo)

/**
 * Service info and defaults
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (void)statusWithRequest:(FaceStatusRequest *)request handler:(void(^)(FaceServiceInfo *_Nullable response, NSError *_Nullable error))handler;

/**
 * Service info and defaults
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (GRPCProtoCall *)RPCTostatusWithRequest:(FaceStatusRequest *)request handler:(void(^)(FaceServiceInfo *_Nullable response, NSError *_Nullable error))handler;


#pragma mark detect(DetectRequest) returns (FaceRecordList)

/**
 * Simple operations
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (void)detectWithRequest:(DetectRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;

/**
 * Simple operations
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (GRPCProtoCall *)RPCTodetectWithRequest:(DetectRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;


#pragma mark extract(ExtractRequest) returns (FaceRecordList)

- (void)extractWithRequest:(ExtractRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;

- (GRPCProtoCall *)RPCToextractWithRequest:(ExtractRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;


#pragma mark score(ScoreRequest) returns (Matrix)

- (void)scoreWithRequest:(ScoreRequest *)request handler:(void(^)(Matrix *_Nullable response, NSError *_Nullable error))handler;

- (GRPCProtoCall *)RPCToscoreWithRequest:(ScoreRequest *)request handler:(void(^)(Matrix *_Nullable response, NSError *_Nullable error))handler;


#pragma mark enroll(EnrollRequest) returns (FaceRecordList)

- (void)enrollWithRequest:(EnrollRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;

- (GRPCProtoCall *)RPCToenrollWithRequest:(EnrollRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;


#pragma mark search(SearchRequest) returns (FaceRecordList)

- (void)searchWithRequest:(SearchRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;

- (GRPCProtoCall *)RPCTosearchWithRequest:(SearchRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;


#pragma mark detectExtract(DetectExtractRequest) returns (FaceRecordList)

/**
 * Combined opperations
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (void)detectExtractWithRequest:(DetectExtractRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;

/**
 * Combined opperations
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (GRPCProtoCall *)RPCTodetectExtractWithRequest:(DetectExtractRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;


#pragma mark detectExtractEnroll(DetectExtractEnrollRequest) returns (FaceRecordList)

- (void)detectExtractEnrollWithRequest:(DetectExtractEnrollRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;

- (GRPCProtoCall *)RPCTodetectExtractEnrollWithRequest:(DetectExtractEnrollRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;


#pragma mark detectExtractSearch(DetectExtractSearchRequest) returns (FaceRecordList)

- (void)detectExtractSearchWithRequest:(DetectExtractSearchRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;

- (GRPCProtoCall *)RPCTodetectExtractSearchWithRequest:(DetectExtractSearchRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;


#pragma mark galleryList(GalleryListRequest) returns (GalleryList)

/**
 * Gallery Management
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (void)galleryListWithRequest:(GalleryListRequest *)request handler:(void(^)(GalleryList *_Nullable response, NSError *_Nullable error))handler;

/**
 * Gallery Management
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (GRPCProtoCall *)RPCTogalleryListWithRequest:(GalleryListRequest *)request handler:(void(^)(GalleryList *_Nullable response, NSError *_Nullable error))handler;


#pragma mark galleryDelete(GalleryDeleteRequest) returns (Empty)

- (void)galleryDeleteWithRequest:(GalleryDeleteRequest *)request handler:(void(^)(Empty *_Nullable response, NSError *_Nullable error))handler;

- (GRPCProtoCall *)RPCTogalleryDeleteWithRequest:(GalleryDeleteRequest *)request handler:(void(^)(Empty *_Nullable response, NSError *_Nullable error))handler;


#pragma mark enrollmentList(EnrollmentListRequest) returns (FaceRecordList)

- (void)enrollmentListWithRequest:(EnrollmentListRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;

- (GRPCProtoCall *)RPCToenrollmentListWithRequest:(EnrollmentListRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;


#pragma mark enrollmentDelete(EnrollmentDeleteRequest) returns (FaceRecordList)

- (void)enrollmentDeleteWithRequest:(EnrollmentDeleteRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;

- (GRPCProtoCall *)RPCToenrollmentDeleteWithRequest:(EnrollmentDeleteRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;


#pragma mark enrollmentDeleteConditional(EnrollmentDeleteRequest) returns (FaceRecordList)

- (void)enrollmentDeleteConditionalWithRequest:(EnrollmentDeleteRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;

- (GRPCProtoCall *)RPCToenrollmentDeleteConditionalWithRequest:(EnrollmentDeleteRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;


#pragma mark enrollmentTransfer(EnrollmentDeleteRequest) returns (FaceRecordList)

- (void)enrollmentTransferWithRequest:(EnrollmentDeleteRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;

- (GRPCProtoCall *)RPCToenrollmentTransferWithRequest:(EnrollmentDeleteRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler;


#pragma mark echo(Matrix) returns (Matrix)

/**
 * Test
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (void)echoWithRequest:(Matrix *)request handler:(void(^)(Matrix *_Nullable response, NSError *_Nullable error))handler;

/**
 * Test
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (GRPCProtoCall *)RPCToechoWithRequest:(Matrix *)request handler:(void(^)(Matrix *_Nullable response, NSError *_Nullable error))handler;


@end


#if !defined(GPB_GRPC_PROTOCOL_ONLY) || !GPB_GRPC_PROTOCOL_ONLY
/**
 * Basic service implementation, over gRPC, that only does
 * marshalling and parsing.
 */
@interface FaceRecognition : GRPCProtoService<FaceRecognition2, FaceRecognition>
- (instancetype)initWithHost:(NSString *)host callOptions:(GRPCCallOptions *_Nullable)callOptions NS_DESIGNATED_INITIALIZER;
+ (instancetype)serviceWithHost:(NSString *)host callOptions:(GRPCCallOptions *_Nullable)callOptions;
// The following methods belong to a set of old APIs that have been deprecated.
- (instancetype)initWithHost:(NSString *)host;
+ (instancetype)serviceWithHost:(NSString *)host;
@end
#endif

NS_ASSUME_NONNULL_END

