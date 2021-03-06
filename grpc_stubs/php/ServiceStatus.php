<?php
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: faro/proto/face_service.proto

/**
 * Protobuf type <code>ServiceStatus</code>
 */
class ServiceStatus
{
    /**
     * Generated from protobuf enum <code>UNKNOWN = 0;</code>
     */
    const UNKNOWN = 0;
    /**
     * Generated from protobuf enum <code>READY = 1;</code>
     */
    const READY = 1;
    /**
     * Generated from protobuf enum <code>ERROR = 2;</code>
     */
    const ERROR = 2;
    /**
     * Generated from protobuf enum <code>BUSY = 3;</code>
     */
    const BUSY = 3;

    private static $valueToName = [
        self::UNKNOWN => 'UNKNOWN',
        self::READY => 'READY',
        self::ERROR => 'ERROR',
        self::BUSY => 'BUSY',
    ];

    public static function name($value)
    {
        if (!isset(self::$valueToName[$value])) {
            throw new UnexpectedValueException(sprintf(
                    'Enum %s has no name defined for value %s', __CLASS__, $value));
        }
        return self::$valueToName[$value];
    }


    public static function value($name)
    {
        $const = __CLASS__ . '::' . strtoupper($name);
        if (!defined($const)) {
            throw new UnexpectedValueException(sprintf(
                    'Enum %s has no value defined for name %s', __CLASS__, $name));
        }
        return constant($const);
    }
}

