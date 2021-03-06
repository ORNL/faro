/**
 * @fileoverview
 * @enhanceable
 * @suppress {messageConventions} JS Compiler reports an error if a variable or
 *     field starts with 'MSG_' and isn't a translatable message.
 * @public
 */
// GENERATED CODE -- DO NOT EDIT!

goog.provide('proto.Detection');

goog.require('jspb.BinaryReader');
goog.require('jspb.BinaryWriter');
goog.require('jspb.Message');
goog.require('proto.Attribute');
goog.require('proto.Rect');

/**
 * Generated by JsPbCodeGenerator.
 * @param {Array=} opt_data Optional initial data array, typically from a
 * server response, or constructed directly in Javascript. The array is used
 * in place and becomes part of the constructed object. It is not cloned.
 * If no data is provided, the constructed object will be empty, but still
 * valid.
 * @extends {jspb.Message}
 * @constructor
 */
proto.Detection = function(opt_data) {
  jspb.Message.initialize(this, opt_data, 0, -1, proto.Detection.repeatedFields_, null);
};
goog.inherits(proto.Detection, jspb.Message);
if (goog.DEBUG && !COMPILED) {
  /**
   * @public
   * @override
   */
  proto.Detection.displayName = 'proto.Detection';
}

/**
 * List of repeated fields within this message type.
 * @private {!Array<number>}
 * @const
 */
proto.Detection.repeatedFields_ = [5];



if (jspb.Message.GENERATE_TO_OBJECT) {
/**
 * Creates an object representation of this proto.
 * Field names that are reserved in JavaScript and will be renamed to pb_name.
 * Optional fields that are not set will be set to undefined.
 * To access a reserved field use, foo.pb_<name>, eg, foo.pb_default.
 * For the list of reserved names please see:
 *     net/proto2/compiler/js/internal/generator.cc#kKeyword.
 * @param {boolean=} opt_includeInstance Deprecated. whether to include the
 *     JSPB instance for transitional soy proto support:
 *     http://goto/soy-param-migration
 * @return {!Object}
 */
proto.Detection.prototype.toObject = function(opt_includeInstance) {
  return proto.Detection.toObject(opt_includeInstance, this);
};


/**
 * Static version of the {@see toObject} method.
 * @param {boolean|undefined} includeInstance Deprecated. Whether to include
 *     the JSPB instance for transitional soy proto support:
 *     http://goto/soy-param-migration
 * @param {!proto.Detection} msg The msg instance to transform.
 * @return {!Object}
 * @suppress {unusedLocalVariables} f is only used for nested messages
 */
proto.Detection.toObject = function(includeInstance, msg) {
  var f, obj = {
    score: jspb.Message.getFloatingPointFieldWithDefault(msg, 1, 0.0),
    location: (f = msg.getLocation()) && proto.Rect.toObject(includeInstance, f),
    detectionId: jspb.Message.getFieldWithDefault(msg, 3, 0),
    detectionClass: jspb.Message.getFieldWithDefault(msg, 4, ""),
    attributesList: jspb.Message.toObjectList(msg.getAttributesList(),
    proto.Attribute.toObject, includeInstance)
  };

  if (includeInstance) {
    obj.$jspbMessageInstance = msg;
  }
  return obj;
};
}


/**
 * Deserializes binary data (in protobuf wire format).
 * @param {jspb.ByteSource} bytes The bytes to deserialize.
 * @return {!proto.Detection}
 */
proto.Detection.deserializeBinary = function(bytes) {
  var reader = new jspb.BinaryReader(bytes);
  var msg = new proto.Detection;
  return proto.Detection.deserializeBinaryFromReader(msg, reader);
};


/**
 * Deserializes binary data (in protobuf wire format) from the
 * given reader into the given message object.
 * @param {!proto.Detection} msg The message object to deserialize into.
 * @param {!jspb.BinaryReader} reader The BinaryReader to use.
 * @return {!proto.Detection}
 */
proto.Detection.deserializeBinaryFromReader = function(msg, reader) {
  while (reader.nextField()) {
    if (reader.isEndGroup()) {
      break;
    }
    var field = reader.getFieldNumber();
    switch (field) {
    case 1:
      var value = /** @type {number} */ (reader.readFloat());
      msg.setScore(value);
      break;
    case 2:
      var value = new proto.Rect;
      reader.readMessage(value,proto.Rect.deserializeBinaryFromReader);
      msg.setLocation(value);
      break;
    case 3:
      var value = /** @type {number} */ (reader.readInt32());
      msg.setDetectionId(value);
      break;
    case 4:
      var value = /** @type {string} */ (reader.readString());
      msg.setDetectionClass(value);
      break;
    case 5:
      var value = new proto.Attribute;
      reader.readMessage(value,proto.Attribute.deserializeBinaryFromReader);
      msg.addAttributes(value);
      break;
    default:
      reader.skipField();
      break;
    }
  }
  return msg;
};


/**
 * Serializes the message to binary data (in protobuf wire format).
 * @return {!Uint8Array}
 */
proto.Detection.prototype.serializeBinary = function() {
  var writer = new jspb.BinaryWriter();
  proto.Detection.serializeBinaryToWriter(this, writer);
  return writer.getResultBuffer();
};


/**
 * Serializes the given message to binary data (in protobuf wire
 * format), writing to the given BinaryWriter.
 * @param {!proto.Detection} message
 * @param {!jspb.BinaryWriter} writer
 * @suppress {unusedLocalVariables} f is only used for nested messages
 */
proto.Detection.serializeBinaryToWriter = function(message, writer) {
  var f = undefined;
  f = message.getScore();
  if (f !== 0.0) {
    writer.writeFloat(
      1,
      f
    );
  }
  f = message.getLocation();
  if (f != null) {
    writer.writeMessage(
      2,
      f,
      proto.Rect.serializeBinaryToWriter
    );
  }
  f = message.getDetectionId();
  if (f !== 0) {
    writer.writeInt32(
      3,
      f
    );
  }
  f = message.getDetectionClass();
  if (f.length > 0) {
    writer.writeString(
      4,
      f
    );
  }
  f = message.getAttributesList();
  if (f.length > 0) {
    writer.writeRepeatedMessage(
      5,
      f,
      proto.Attribute.serializeBinaryToWriter
    );
  }
};


/**
 * optional float score = 1;
 * @return {number}
 */
proto.Detection.prototype.getScore = function() {
  return /** @type {number} */ (jspb.Message.getFloatingPointFieldWithDefault(this, 1, 0.0));
};


/** @param {number} value */
proto.Detection.prototype.setScore = function(value) {
  jspb.Message.setProto3FloatField(this, 1, value);
};


/**
 * optional Rect location = 2;
 * @return {?proto.Rect}
 */
proto.Detection.prototype.getLocation = function() {
  return /** @type{?proto.Rect} */ (
    jspb.Message.getWrapperField(this, proto.Rect, 2));
};


/** @param {?proto.Rect|undefined} value */
proto.Detection.prototype.setLocation = function(value) {
  jspb.Message.setWrapperField(this, 2, value);
};


/**
 * Clears the message field making it undefined.
 */
proto.Detection.prototype.clearLocation = function() {
  this.setLocation(undefined);
};


/**
 * Returns whether this field is set.
 * @return {boolean}
 */
proto.Detection.prototype.hasLocation = function() {
  return jspb.Message.getField(this, 2) != null;
};


/**
 * optional int32 detection_id = 3;
 * @return {number}
 */
proto.Detection.prototype.getDetectionId = function() {
  return /** @type {number} */ (jspb.Message.getFieldWithDefault(this, 3, 0));
};


/** @param {number} value */
proto.Detection.prototype.setDetectionId = function(value) {
  jspb.Message.setProto3IntField(this, 3, value);
};


/**
 * optional string detection_class = 4;
 * @return {string}
 */
proto.Detection.prototype.getDetectionClass = function() {
  return /** @type {string} */ (jspb.Message.getFieldWithDefault(this, 4, ""));
};


/** @param {string} value */
proto.Detection.prototype.setDetectionClass = function(value) {
  jspb.Message.setProto3StringField(this, 4, value);
};


/**
 * repeated Attribute attributes = 5;
 * @return {!Array<!proto.Attribute>}
 */
proto.Detection.prototype.getAttributesList = function() {
  return /** @type{!Array<!proto.Attribute>} */ (
    jspb.Message.getRepeatedWrapperField(this, proto.Attribute, 5));
};


/** @param {!Array<!proto.Attribute>} value */
proto.Detection.prototype.setAttributesList = function(value) {
  jspb.Message.setRepeatedWrapperField(this, 5, value);
};


/**
 * @param {!proto.Attribute=} opt_value
 * @param {number=} opt_index
 * @return {!proto.Attribute}
 */
proto.Detection.prototype.addAttributes = function(opt_value, opt_index) {
  return jspb.Message.addToRepeatedWrapperField(this, 5, opt_value, proto.Attribute, opt_index);
};


/**
 * Clears the list making it empty but non-null.
 */
proto.Detection.prototype.clearAttributesList = function() {
  this.setAttributesList([]);
};


