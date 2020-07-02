#if !defined(GPB_GRPC_PROTOCOL_ONLY) || !GPB_GRPC_PROTOCOL_ONLY
#import "faro/proto/FaceService.pbrpc.h"
#import "faro/proto/FaceService.pbobjc.h"
#import <ProtoRPC/ProtoRPCLegacy.h>
#import <RxLibrary/GRXWriter+Immediate.h>

#import "faro/proto/Image.pbobjc.h"
#import "faro/proto/Geometry.pbobjc.h"

@implementation FaceRecognition

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wobjc-designated-initializers"

// Designated initializer
- (instancetype)initWithHost:(NSString *)host callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [super initWithHost:host
                 packageName:@""
                 serviceName:@"FaceRecognition"
                 callOptions:callOptions];
}

- (instancetype)initWithHost:(NSString *)host {
  return [super initWithHost:host
                 packageName:@""
                 serviceName:@"FaceRecognition"];
}

#pragma clang diagnostic pop

// Override superclass initializer to disallow different package and service names.
- (instancetype)initWithHost:(NSString *)host
                 packageName:(NSString *)packageName
                 serviceName:(NSString *)serviceName {
  return [self initWithHost:host];
}

- (instancetype)initWithHost:(NSString *)host
                 packageName:(NSString *)packageName
                 serviceName:(NSString *)serviceName
                 callOptions:(GRPCCallOptions *)callOptions {
  return [self initWithHost:host callOptions:callOptions];
}

#pragma mark - Class Methods

+ (instancetype)serviceWithHost:(NSString *)host {
  return [[self alloc] initWithHost:host];
}

+ (instancetype)serviceWithHost:(NSString *)host callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [[self alloc] initWithHost:host callOptions:callOptions];
}

#pragma mark - Method Implementations

#pragma mark status(FaceStatusRequest) returns (FaceServiceInfo)

/**
 * Service info and defaults
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (void)statusWithRequest:(FaceStatusRequest *)request handler:(void(^)(FaceServiceInfo *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCTostatusWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
/**
 * Service info and defaults
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (GRPCProtoCall *)RPCTostatusWithRequest:(FaceStatusRequest *)request handler:(void(^)(FaceServiceInfo *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"status"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[FaceServiceInfo class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
/**
 * Service info and defaults
 */
- (GRPCUnaryProtoCall *)statusWithMessage:(FaceStatusRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"status"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[FaceServiceInfo class]];
}

#pragma mark detect(DetectRequest) returns (FaceRecordList)

/**
 * Simple operations
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (void)detectWithRequest:(DetectRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCTodetectWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
/**
 * Simple operations
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (GRPCProtoCall *)RPCTodetectWithRequest:(DetectRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"detect"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[FaceRecordList class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
/**
 * Simple operations
 */
- (GRPCUnaryProtoCall *)detectWithMessage:(DetectRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"detect"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[FaceRecordList class]];
}

#pragma mark extract(ExtractRequest) returns (FaceRecordList)

- (void)extractWithRequest:(ExtractRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCToextractWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
- (GRPCProtoCall *)RPCToextractWithRequest:(ExtractRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"extract"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[FaceRecordList class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
- (GRPCUnaryProtoCall *)extractWithMessage:(ExtractRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"extract"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[FaceRecordList class]];
}

#pragma mark score(ScoreRequest) returns (Matrix)

- (void)scoreWithRequest:(ScoreRequest *)request handler:(void(^)(Matrix *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCToscoreWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
- (GRPCProtoCall *)RPCToscoreWithRequest:(ScoreRequest *)request handler:(void(^)(Matrix *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"score"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[Matrix class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
- (GRPCUnaryProtoCall *)scoreWithMessage:(ScoreRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"score"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[Matrix class]];
}

#pragma mark enroll(EnrollRequest) returns (FaceRecordList)

- (void)enrollWithRequest:(EnrollRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCToenrollWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
- (GRPCProtoCall *)RPCToenrollWithRequest:(EnrollRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"enroll"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[FaceRecordList class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
- (GRPCUnaryProtoCall *)enrollWithMessage:(EnrollRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"enroll"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[FaceRecordList class]];
}

#pragma mark search(SearchRequest) returns (FaceRecordList)

- (void)searchWithRequest:(SearchRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCTosearchWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
- (GRPCProtoCall *)RPCTosearchWithRequest:(SearchRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"search"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[FaceRecordList class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
- (GRPCUnaryProtoCall *)searchWithMessage:(SearchRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"search"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[FaceRecordList class]];
}

#pragma mark detectExtract(DetectExtractRequest) returns (FaceRecordList)

/**
 * Combined opperations
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (void)detectExtractWithRequest:(DetectExtractRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCTodetectExtractWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
/**
 * Combined opperations
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (GRPCProtoCall *)RPCTodetectExtractWithRequest:(DetectExtractRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"detectExtract"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[FaceRecordList class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
/**
 * Combined opperations
 */
- (GRPCUnaryProtoCall *)detectExtractWithMessage:(DetectExtractRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"detectExtract"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[FaceRecordList class]];
}

#pragma mark detectExtractEnroll(DetectExtractEnrollRequest) returns (FaceRecordList)

- (void)detectExtractEnrollWithRequest:(DetectExtractEnrollRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCTodetectExtractEnrollWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
- (GRPCProtoCall *)RPCTodetectExtractEnrollWithRequest:(DetectExtractEnrollRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"detectExtractEnroll"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[FaceRecordList class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
- (GRPCUnaryProtoCall *)detectExtractEnrollWithMessage:(DetectExtractEnrollRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"detectExtractEnroll"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[FaceRecordList class]];
}

#pragma mark detectExtractSearch(DetectExtractSearchRequest) returns (FaceRecordList)

- (void)detectExtractSearchWithRequest:(DetectExtractSearchRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCTodetectExtractSearchWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
- (GRPCProtoCall *)RPCTodetectExtractSearchWithRequest:(DetectExtractSearchRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"detectExtractSearch"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[FaceRecordList class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
- (GRPCUnaryProtoCall *)detectExtractSearchWithMessage:(DetectExtractSearchRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"detectExtractSearch"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[FaceRecordList class]];
}

#pragma mark galleryList(GalleryListRequest) returns (GalleryList)

/**
 * Gallery Management
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (void)galleryListWithRequest:(GalleryListRequest *)request handler:(void(^)(GalleryList *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCTogalleryListWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
/**
 * Gallery Management
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (GRPCProtoCall *)RPCTogalleryListWithRequest:(GalleryListRequest *)request handler:(void(^)(GalleryList *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"galleryList"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[GalleryList class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
/**
 * Gallery Management
 */
- (GRPCUnaryProtoCall *)galleryListWithMessage:(GalleryListRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"galleryList"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[GalleryList class]];
}

#pragma mark galleryDelete(GalleryDeleteRequest) returns (Empty)

- (void)galleryDeleteWithRequest:(GalleryDeleteRequest *)request handler:(void(^)(Empty *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCTogalleryDeleteWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
- (GRPCProtoCall *)RPCTogalleryDeleteWithRequest:(GalleryDeleteRequest *)request handler:(void(^)(Empty *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"galleryDelete"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[Empty class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
- (GRPCUnaryProtoCall *)galleryDeleteWithMessage:(GalleryDeleteRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"galleryDelete"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[Empty class]];
}

#pragma mark enrollmentList(EnrollmentListRequest) returns (FaceRecordList)

- (void)enrollmentListWithRequest:(EnrollmentListRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCToenrollmentListWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
- (GRPCProtoCall *)RPCToenrollmentListWithRequest:(EnrollmentListRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"enrollmentList"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[FaceRecordList class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
- (GRPCUnaryProtoCall *)enrollmentListWithMessage:(EnrollmentListRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"enrollmentList"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[FaceRecordList class]];
}

#pragma mark enrollmentDelete(EnrollmentDeleteRequest) returns (FaceRecordList)

- (void)enrollmentDeleteWithRequest:(EnrollmentDeleteRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCToenrollmentDeleteWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
- (GRPCProtoCall *)RPCToenrollmentDeleteWithRequest:(EnrollmentDeleteRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"enrollmentDelete"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[FaceRecordList class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
- (GRPCUnaryProtoCall *)enrollmentDeleteWithMessage:(EnrollmentDeleteRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"enrollmentDelete"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[FaceRecordList class]];
}

#pragma mark enrollmentDeleteConditional(EnrollmentDeleteRequest) returns (FaceRecordList)

- (void)enrollmentDeleteConditionalWithRequest:(EnrollmentDeleteRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCToenrollmentDeleteConditionalWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
- (GRPCProtoCall *)RPCToenrollmentDeleteConditionalWithRequest:(EnrollmentDeleteRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"enrollmentDeleteConditional"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[FaceRecordList class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
- (GRPCUnaryProtoCall *)enrollmentDeleteConditionalWithMessage:(EnrollmentDeleteRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"enrollmentDeleteConditional"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[FaceRecordList class]];
}

#pragma mark enrollmentTransfer(EnrollmentDeleteRequest) returns (FaceRecordList)

- (void)enrollmentTransferWithRequest:(EnrollmentDeleteRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCToenrollmentTransferWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
- (GRPCProtoCall *)RPCToenrollmentTransferWithRequest:(EnrollmentDeleteRequest *)request handler:(void(^)(FaceRecordList *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"enrollmentTransfer"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[FaceRecordList class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
- (GRPCUnaryProtoCall *)enrollmentTransferWithMessage:(EnrollmentDeleteRequest *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"enrollmentTransfer"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[FaceRecordList class]];
}

#pragma mark echo(Matrix) returns (Matrix)

/**
 * Test
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (void)echoWithRequest:(Matrix *)request handler:(void(^)(Matrix *_Nullable response, NSError *_Nullable error))handler{
  [[self RPCToechoWithRequest:request handler:handler] start];
}
// Returns a not-yet-started RPC object.
/**
 * Test
 *
 * This method belongs to a set of APIs that have been deprecated. Using the v2 API is recommended.
 */
- (GRPCProtoCall *)RPCToechoWithRequest:(Matrix *)request handler:(void(^)(Matrix *_Nullable response, NSError *_Nullable error))handler{
  return [self RPCToMethod:@"echo"
            requestsWriter:[GRXWriter writerWithValue:request]
             responseClass:[Matrix class]
        responsesWriteable:[GRXWriteable writeableWithSingleHandler:handler]];
}
/**
 * Test
 */
- (GRPCUnaryProtoCall *)echoWithMessage:(Matrix *)message responseHandler:(id<GRPCProtoResponseHandler>)handler callOptions:(GRPCCallOptions *_Nullable)callOptions {
  return [self RPCToMethod:@"echo"
                   message:message
           responseHandler:handler
               callOptions:callOptions
             responseClass:[Matrix class]];
}

@end
#endif
