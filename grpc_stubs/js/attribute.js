/**
 * @fileoverview
 * @enhanceable
 * @suppress {messageConventions} JS Compiler reports an error if a variable or
 *     field starts with 'MSG_' and isn't a translatable message.
 * @public
 */
// GENERATED CODE -- DO NOT EDIT!

goog.provide('proto.Attribute');

goog.require('jspb.BinaryReader');
goog.require('jspb.BinaryWriter');
goog.require('jspb.Message');
goog.require('proto.Image');
goog.require('proto.Matrix');
goog.require('proto.Point2D');
goog.require('proto.Rect');
goog.require('proto.Vector');

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
proto.Attribute = function(opt_data) {
  jspb.Message.initialize(this, opt_data, 0, -1, null, null);
};
goog.inherits(proto.Attribute, jspb.Message);
if (goog.DEBUG && !COMPILED) {
  /**
   * @public
   * @override
   */
  proto.Attribute.displayName = 'proto.Attribute';
}



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
proto.Attribute.prototype.toObject = function(opt_includeInstance) {
  return proto.Attribute.toObject(opt_includeInstance, this);
};


/**
 * Static version of the {@see toObject} method.
 * @param {boolean|undefined} includeInstance Deprecated. Whether to include
 *     the JSPB instance for transitional soy proto support:
 *     http://goto/soy-param-migration
 * @param {!proto.Attribute} msg The msg instance to transform.
 * @return {!Object}
 * @suppress {unusedLocalVariables} f is only used for nested messages
 */
proto.Attribute.toObject = function(includeInstance, msg) {
  var f, obj = {
    key: jspb.Message.getFieldWithDefault(msg, 1, ""),
    description: jspb.Message.getFieldWithDefault(msg, 2, ""),
    buffer: msg.getBuffer_asB64(),
    fvalue: jspb.Message.getFloatingPointFieldWithDefault(msg, 4, 0.0),
    ivalue: jspb.Message.getFieldWithDefault(msg, 5, 0),
    text: jspb.Message.getFieldWithDefault(msg, 6, ""),
    pickle: msg.getPickle_asB64(),
    json: msg.getJson_asB64(),
    matrix: (f = msg.getMatrix()) && proto.Matrix.toObject(includeInstance, f),
    vector: (f = msg.getVector()) && proto.Vector.toObject(includeInstance, f),
    image: (f = msg.getImage()) && proto.Image.toObject(includeInstance, f),
    point: (f = msg.getPoint()) && proto.Point2D.toObject(includeInstance, f),
    rect: (f = msg.getRect()) && proto.Rect.toObject(includeInstance, f),
    xml: msg.getXml_asB64()
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
 * @return {!proto.Attribute}
 */
proto.Attribute.deserializeBinary = function(bytes) {
  var reader = new jspb.BinaryReader(bytes);
  var msg = new proto.Attribute;
  return proto.Attribute.deserializeBinaryFromReader(msg, reader);
};


/**
 * Deserializes binary data (in protobuf wire format) from the
 * given reader into the given message object.
 * @param {!proto.Attribute} msg The message object to deserialize into.
 * @param {!jspb.BinaryReader} reader The BinaryReader to use.
 * @return {!proto.Attribute}
 */
proto.Attribute.deserializeBinaryFromReader = function(msg, reader) {
  while (reader.nextField()) {
    if (reader.isEndGroup()) {
      break;
    }
    var field = reader.getFieldNumber();
    switch (field) {
    case 1:
      var value = /** @type {string} */ (reader.readString());
      msg.setKey(value);
      break;
    case 2:
      var value = /** @type {string} */ (reader.readString());
      msg.setDescription(value);
      break;
    case 3:
      var value = /** @type {!Uint8Array} */ (reader.readBytes());
      msg.setBuffer(value);
      break;
    case 4:
      var value = /** @type {number} */ (reader.readFloat());
      msg.setFvalue(value);
      break;
    case 5:
      var value = /** @type {number} */ (reader.readInt32());
      msg.setIvalue(value);
      break;
    case 6:
      var value = /** @type {string} */ (reader.readString());
      msg.setText(value);
      break;
    case 7:
      var value = /** @type {!Uint8Array} */ (reader.readBytes());
      msg.setPickle(value);
      break;
    case 8:
      var value = /** @type {!Uint8Array} */ (reader.readBytes());
      msg.setJson(value);
      break;
    case 9:
      var value = new proto.Matrix;
      reader.readMessage(value,proto.Matrix.deserializeBinaryFromReader);
      msg.setMatrix(value);
      break;
    case 10:
      var value = new proto.Vector;
      reader.readMessage(value,proto.Vector.deserializeBinaryFromReader);
      msg.setVector(value);
      break;
    case 11:
      var value = new proto.Image;
      reader.readMessage(value,proto.Image.deserializeBinaryFromReader);
      msg.setImage(value);
      break;
    case 12:
      var value = new proto.Point2D;
      reader.readMessage(value,proto.Point2D.deserializeBinaryFromReader);
      msg.setPoint(value);
      break;
    case 13:
      var value = new proto.Rect;
      reader.readMessage(value,proto.Rect.deserializeBinaryFromReader);
      msg.setRect(value);
      break;
    case 14:
      var value = /** @type {!Uint8Array} */ (reader.readBytes());
      msg.setXml(value);
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
proto.Attribute.prototype.serializeBinary = function() {
  var writer = new jspb.BinaryWriter();
  proto.Attribute.serializeBinaryToWriter(this, writer);
  return writer.getResultBuffer();
};


/**
 * Serializes the given message to binary data (in protobuf wire
 * format), writing to the given BinaryWriter.
 * @param {!proto.Attribute} message
 * @param {!jspb.BinaryWriter} writer
 * @suppress {unusedLocalVariables} f is only used for nested messages
 */
proto.Attribute.serializeBinaryToWriter = function(message, writer) {
  var f = undefined;
  f = message.getKey();
  if (f.length > 0) {
    writer.writeString(
      1,
      f
    );
  }
  f = message.getDescription();
  if (f.length > 0) {
    writer.writeString(
      2,
      f
    );
  }
  f = message.getBuffer_asU8();
  if (f.length > 0) {
    writer.writeBytes(
      3,
      f
    );
  }
  f = message.getFvalue();
  if (f !== 0.0) {
    writer.writeFloat(
      4,
      f
    );
  }
  f = message.getIvalue();
  if (f !== 0) {
    writer.writeInt32(
      5,
      f
    );
  }
  f = message.getText();
  if (f.length > 0) {
    writer.writeString(
      6,
      f
    );
  }
  f = message.getPickle_asU8();
  if (f.length > 0) {
    writer.writeBytes(
      7,
      f
    );
  }
  f = message.getJson_asU8();
  if (f.length > 0) {
    writer.writeBytes(
      8,
      f
    );
  }
  f = message.getMatrix();
  if (f != null) {
    writer.writeMessage(
      9,
      f,
      proto.Matrix.serializeBinaryToWriter
    );
  }
  f = message.getVector();
  if (f != null) {
    writer.writeMessage(
      10,
      f,
      proto.Vector.serializeBinaryToWriter
    );
  }
  f = message.getImage();
  if (f != null) {
    writer.writeMessage(
      11,
      f,
      proto.Image.serializeBinaryToWriter
    );
  }
  f = message.getPoint();
  if (f != null) {
    writer.writeMessage(
      12,
      f,
      proto.Point2D.serializeBinaryToWriter
    );
  }
  f = message.getRect();
  if (f != null) {
    writer.writeMessage(
      13,
      f,
      proto.Rect.serializeBinaryToWriter
    );
  }
  f = message.getXml_asU8();
  if (f.length > 0) {
    writer.writeBytes(
      14,
      f
    );
  }
};


/**
 * optional string key = 1;
 * @return {string}
 */
proto.Attribute.prototype.getKey = function() {
  return /** @type {string} */ (jspb.Message.getFieldWithDefault(this, 1, ""));
};


/** @param {string} value */
proto.Attribute.prototype.setKey = function(value) {
  jspb.Message.setProto3StringField(this, 1, value);
};


/**
 * optional string description = 2;
 * @return {string}
 */
proto.Attribute.prototype.getDescription = function() {
  return /** @type {string} */ (jspb.Message.getFieldWithDefault(this, 2, ""));
};


/** @param {string} value */
proto.Attribute.prototype.setDescription = function(value) {
  jspb.Message.setProto3StringField(this, 2, value);
};


/**
 * optional bytes buffer = 3;
 * @return {string}
 */
proto.Attribute.prototype.getBuffer = function() {
  return /** @type {string} */ (jspb.Message.getFieldWithDefault(this, 3, ""));
};


/**
 * optional bytes buffer = 3;
 * This is a type-conversion wrapper around `getBuffer()`
 * @return {string}
 */
proto.Attribute.prototype.getBuffer_asB64 = function() {
  return /** @type {string} */ (jspb.Message.bytesAsB64(
      this.getBuffer()));
};


/**
 * optional bytes buffer = 3;
 * Note that Uint8Array is not supported on all browsers.
 * @see http://caniuse.com/Uint8Array
 * This is a type-conversion wrapper around `getBuffer()`
 * @return {!Uint8Array}
 */
proto.Attribute.prototype.getBuffer_asU8 = function() {
  return /** @type {!Uint8Array} */ (jspb.Message.bytesAsU8(
      this.getBuffer()));
};


/** @param {!(string|Uint8Array)} value */
proto.Attribute.prototype.setBuffer = function(value) {
  jspb.Message.setProto3BytesField(this, 3, value);
};


/**
 * optional float fvalue = 4;
 * @return {number}
 */
proto.Attribute.prototype.getFvalue = function() {
  return /** @type {number} */ (jspb.Message.getFloatingPointFieldWithDefault(this, 4, 0.0));
};


/** @param {number} value */
proto.Attribute.prototype.setFvalue = function(value) {
  jspb.Message.setProto3FloatField(this, 4, value);
};


/**
 * optional int32 ivalue = 5;
 * @return {number}
 */
proto.Attribute.prototype.getIvalue = function() {
  return /** @type {number} */ (jspb.Message.getFieldWithDefault(this, 5, 0));
};


/** @param {number} value */
proto.Attribute.prototype.setIvalue = function(value) {
  jspb.Message.setProto3IntField(this, 5, value);
};


/**
 * optional string text = 6;
 * @return {string}
 */
proto.Attribute.prototype.getText = function() {
  return /** @type {string} */ (jspb.Message.getFieldWithDefault(this, 6, ""));
};


/** @param {string} value */
proto.Attribute.prototype.setText = function(value) {
  jspb.Message.setProto3StringField(this, 6, value);
};


/**
 * optional bytes pickle = 7;
 * @return {string}
 */
proto.Attribute.prototype.getPickle = function() {
  return /** @type {string} */ (jspb.Message.getFieldWithDefault(this, 7, ""));
};


/**
 * optional bytes pickle = 7;
 * This is a type-conversion wrapper around `getPickle()`
 * @return {string}
 */
proto.Attribute.prototype.getPickle_asB64 = function() {
  return /** @type {string} */ (jspb.Message.bytesAsB64(
      this.getPickle()));
};


/**
 * optional bytes pickle = 7;
 * Note that Uint8Array is not supported on all browsers.
 * @see http://caniuse.com/Uint8Array
 * This is a type-conversion wrapper around `getPickle()`
 * @return {!Uint8Array}
 */
proto.Attribute.prototype.getPickle_asU8 = function() {
  return /** @type {!Uint8Array} */ (jspb.Message.bytesAsU8(
      this.getPickle()));
};


/** @param {!(string|Uint8Array)} value */
proto.Attribute.prototype.setPickle = function(value) {
  jspb.Message.setProto3BytesField(this, 7, value);
};


/**
 * optional bytes json = 8;
 * @return {string}
 */
proto.Attribute.prototype.getJson = function() {
  return /** @type {string} */ (jspb.Message.getFieldWithDefault(this, 8, ""));
};


/**
 * optional bytes json = 8;
 * This is a type-conversion wrapper around `getJson()`
 * @return {string}
 */
proto.Attribute.prototype.getJson_asB64 = function() {
  return /** @type {string} */ (jspb.Message.bytesAsB64(
      this.getJson()));
};


/**
 * optional bytes json = 8;
 * Note that Uint8Array is not supported on all browsers.
 * @see http://caniuse.com/Uint8Array
 * This is a type-conversion wrapper around `getJson()`
 * @return {!Uint8Array}
 */
proto.Attribute.prototype.getJson_asU8 = function() {
  return /** @type {!Uint8Array} */ (jspb.Message.bytesAsU8(
      this.getJson()));
};


/** @param {!(string|Uint8Array)} value */
proto.Attribute.prototype.setJson = function(value) {
  jspb.Message.setProto3BytesField(this, 8, value);
};


/**
 * optional Matrix matrix = 9;
 * @return {?proto.Matrix}
 */
proto.Attribute.prototype.getMatrix = function() {
  return /** @type{?proto.Matrix} */ (
    jspb.Message.getWrapperField(this, proto.Matrix, 9));
};


/** @param {?proto.Matrix|undefined} value */
proto.Attribute.prototype.setMatrix = function(value) {
  jspb.Message.setWrapperField(this, 9, value);
};


/**
 * Clears the message field making it undefined.
 */
proto.Attribute.prototype.clearMatrix = function() {
  this.setMatrix(undefined);
};


/**
 * Returns whether this field is set.
 * @return {boolean}
 */
proto.Attribute.prototype.hasMatrix = function() {
  return jspb.Message.getField(this, 9) != null;
};


/**
 * optional Vector vector = 10;
 * @return {?proto.Vector}
 */
proto.Attribute.prototype.getVector = function() {
  return /** @type{?proto.Vector} */ (
    jspb.Message.getWrapperField(this, proto.Vector, 10));
};


/** @param {?proto.Vector|undefined} value */
proto.Attribute.prototype.setVector = function(value) {
  jspb.Message.setWrapperField(this, 10, value);
};


/**
 * Clears the message field making it undefined.
 */
proto.Attribute.prototype.clearVector = function() {
  this.setVector(undefined);
};


/**
 * Returns whether this field is set.
 * @return {boolean}
 */
proto.Attribute.prototype.hasVector = function() {
  return jspb.Message.getField(this, 10) != null;
};


/**
 * optional Image image = 11;
 * @return {?proto.Image}
 */
proto.Attribute.prototype.getImage = function() {
  return /** @type{?proto.Image} */ (
    jspb.Message.getWrapperField(this, proto.Image, 11));
};


/** @param {?proto.Image|undefined} value */
proto.Attribute.prototype.setImage = function(value) {
  jspb.Message.setWrapperField(this, 11, value);
};


/**
 * Clears the message field making it undefined.
 */
proto.Attribute.prototype.clearImage = function() {
  this.setImage(undefined);
};


/**
 * Returns whether this field is set.
 * @return {boolean}
 */
proto.Attribute.prototype.hasImage = function() {
  return jspb.Message.getField(this, 11) != null;
};


/**
 * optional Point2D point = 12;
 * @return {?proto.Point2D}
 */
proto.Attribute.prototype.getPoint = function() {
  return /** @type{?proto.Point2D} */ (
    jspb.Message.getWrapperField(this, proto.Point2D, 12));
};


/** @param {?proto.Point2D|undefined} value */
proto.Attribute.prototype.setPoint = function(value) {
  jspb.Message.setWrapperField(this, 12, value);
};


/**
 * Clears the message field making it undefined.
 */
proto.Attribute.prototype.clearPoint = function() {
  this.setPoint(undefined);
};


/**
 * Returns whether this field is set.
 * @return {boolean}
 */
proto.Attribute.prototype.hasPoint = function() {
  return jspb.Message.getField(this, 12) != null;
};


/**
 * optional Rect rect = 13;
 * @return {?proto.Rect}
 */
proto.Attribute.prototype.getRect = function() {
  return /** @type{?proto.Rect} */ (
    jspb.Message.getWrapperField(this, proto.Rect, 13));
};


/** @param {?proto.Rect|undefined} value */
proto.Attribute.prototype.setRect = function(value) {
  jspb.Message.setWrapperField(this, 13, value);
};


/**
 * Clears the message field making it undefined.
 */
proto.Attribute.prototype.clearRect = function() {
  this.setRect(undefined);
};


/**
 * Returns whether this field is set.
 * @return {boolean}
 */
proto.Attribute.prototype.hasRect = function() {
  return jspb.Message.getField(this, 13) != null;
};


/**
 * optional bytes xml = 14;
 * @return {string}
 */
proto.Attribute.prototype.getXml = function() {
  return /** @type {string} */ (jspb.Message.getFieldWithDefault(this, 14, ""));
};


/**
 * optional bytes xml = 14;
 * This is a type-conversion wrapper around `getXml()`
 * @return {string}
 */
proto.Attribute.prototype.getXml_asB64 = function() {
  return /** @type {string} */ (jspb.Message.bytesAsB64(
      this.getXml()));
};


/**
 * optional bytes xml = 14;
 * Note that Uint8Array is not supported on all browsers.
 * @see http://caniuse.com/Uint8Array
 * This is a type-conversion wrapper around `getXml()`
 * @return {!Uint8Array}
 */
proto.Attribute.prototype.getXml_asU8 = function() {
  return /** @type {!Uint8Array} */ (jspb.Message.bytesAsU8(
      this.getXml()));
};


/** @param {!(string|Uint8Array)} value */
proto.Attribute.prototype.setXml = function(value) {
  jspb.Message.setProto3BytesField(this, 14, value);
};


