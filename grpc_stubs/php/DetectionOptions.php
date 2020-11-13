<?php
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: faro/proto/face_service.proto

use Google\Protobuf\Internal\GPBType;
use Google\Protobuf\Internal\RepeatedField;
use Google\Protobuf\Internal\GPBUtil;

/**
 * Generated from protobuf message <code>DetectionOptions</code>
 */
class DetectionOptions extends \Google\Protobuf\Internal\Message
{
    /**
     * Generated from protobuf field <code>string algorithm_id = 1;</code>
     */
    private $algorithm_id = '';
    /**
     * Generated from protobuf field <code>bool best = 2;</code>
     */
    private $best = false;
    /**
     * Generated from protobuf field <code>float threshold = 3;</code>
     */
    private $threshold = 0.0;
    /**
     * optional - break the image up for larger images
     *
     * Generated from protobuf field <code>int32 scale_levels = 4;</code>
     */
    private $scale_levels = 0;
    /**
     * number of times to reduce the image by half and then scan using the detector
     *
     * Generated from protobuf field <code>int32 scan_levels = 5;</code>
     */
    private $scan_levels = 0;
    /**
     * amount of overlap to use at each scan level.
     *
     * Generated from protobuf field <code>float scan_overlap = 6;</code>
     */
    private $scan_overlap = 0.0;
    /**
     * Generated from protobuf field <code>int32 min_size = 7;</code>
     */
    private $min_size = 0;
    /**
     * log the image on the server - Useful for debugging and record keeping
     *
     * Generated from protobuf field <code>bool save_request = 9;</code>
     */
    private $save_request = false;
    /**
     * Save or print more info on the server side
     *
     * Generated from protobuf field <code>bool debug = 10;</code>
     */
    private $debug = false;
    /**
     * Used for passing algorithm specific options
     *
     * Generated from protobuf field <code>repeated .Attribute attributes = 8;</code>
     */
    private $attributes;

    /**
     * Constructor.
     *
     * @param array $data {
     *     Optional. Data for populating the Message object.
     *
     *     @type string $algorithm_id
     *     @type bool $best
     *     @type float $threshold
     *     @type int $scale_levels
     *           optional - break the image up for larger images
     *     @type int $scan_levels
     *           number of times to reduce the image by half and then scan using the detector
     *     @type float $scan_overlap
     *           amount of overlap to use at each scan level.
     *     @type int $min_size
     *     @type bool $save_request
     *           log the image on the server - Useful for debugging and record keeping
     *     @type bool $debug
     *           Save or print more info on the server side
     *     @type \Attribute[]|\Google\Protobuf\Internal\RepeatedField $attributes
     *           Used for passing algorithm specific options
     * }
     */
    public function __construct($data = NULL) {
        \GPBMetadata\Faro\Proto\FaceService::initOnce();
        parent::__construct($data);
    }

    /**
     * Generated from protobuf field <code>string algorithm_id = 1;</code>
     * @return string
     */
    public function getAlgorithmId()
    {
        return $this->algorithm_id;
    }

    /**
     * Generated from protobuf field <code>string algorithm_id = 1;</code>
     * @param string $var
     * @return $this
     */
    public function setAlgorithmId($var)
    {
        GPBUtil::checkString($var, True);
        $this->algorithm_id = $var;

        return $this;
    }

    /**
     * Generated from protobuf field <code>bool best = 2;</code>
     * @return bool
     */
    public function getBest()
    {
        return $this->best;
    }

    /**
     * Generated from protobuf field <code>bool best = 2;</code>
     * @param bool $var
     * @return $this
     */
    public function setBest($var)
    {
        GPBUtil::checkBool($var);
        $this->best = $var;

        return $this;
    }

    /**
     * Generated from protobuf field <code>float threshold = 3;</code>
     * @return float
     */
    public function getThreshold()
    {
        return $this->threshold;
    }

    /**
     * Generated from protobuf field <code>float threshold = 3;</code>
     * @param float $var
     * @return $this
     */
    public function setThreshold($var)
    {
        GPBUtil::checkFloat($var);
        $this->threshold = $var;

        return $this;
    }

    /**
     * optional - break the image up for larger images
     *
     * Generated from protobuf field <code>int32 scale_levels = 4;</code>
     * @return int
     */
    public function getScaleLevels()
    {
        return $this->scale_levels;
    }

    /**
     * optional - break the image up for larger images
     *
     * Generated from protobuf field <code>int32 scale_levels = 4;</code>
     * @param int $var
     * @return $this
     */
    public function setScaleLevels($var)
    {
        GPBUtil::checkInt32($var);
        $this->scale_levels = $var;

        return $this;
    }

    /**
     * number of times to reduce the image by half and then scan using the detector
     *
     * Generated from protobuf field <code>int32 scan_levels = 5;</code>
     * @return int
     */
    public function getScanLevels()
    {
        return $this->scan_levels;
    }

    /**
     * number of times to reduce the image by half and then scan using the detector
     *
     * Generated from protobuf field <code>int32 scan_levels = 5;</code>
     * @param int $var
     * @return $this
     */
    public function setScanLevels($var)
    {
        GPBUtil::checkInt32($var);
        $this->scan_levels = $var;

        return $this;
    }

    /**
     * amount of overlap to use at each scan level.
     *
     * Generated from protobuf field <code>float scan_overlap = 6;</code>
     * @return float
     */
    public function getScanOverlap()
    {
        return $this->scan_overlap;
    }

    /**
     * amount of overlap to use at each scan level.
     *
     * Generated from protobuf field <code>float scan_overlap = 6;</code>
     * @param float $var
     * @return $this
     */
    public function setScanOverlap($var)
    {
        GPBUtil::checkFloat($var);
        $this->scan_overlap = $var;

        return $this;
    }

    /**
     * Generated from protobuf field <code>int32 min_size = 7;</code>
     * @return int
     */
    public function getMinSize()
    {
        return $this->min_size;
    }

    /**
     * Generated from protobuf field <code>int32 min_size = 7;</code>
     * @param int $var
     * @return $this
     */
    public function setMinSize($var)
    {
        GPBUtil::checkInt32($var);
        $this->min_size = $var;

        return $this;
    }

    /**
     * log the image on the server - Useful for debugging and record keeping
     *
     * Generated from protobuf field <code>bool save_request = 9;</code>
     * @return bool
     */
    public function getSaveRequest()
    {
        return $this->save_request;
    }

    /**
     * log the image on the server - Useful for debugging and record keeping
     *
     * Generated from protobuf field <code>bool save_request = 9;</code>
     * @param bool $var
     * @return $this
     */
    public function setSaveRequest($var)
    {
        GPBUtil::checkBool($var);
        $this->save_request = $var;

        return $this;
    }

    /**
     * Save or print more info on the server side
     *
     * Generated from protobuf field <code>bool debug = 10;</code>
     * @return bool
     */
    public function getDebug()
    {
        return $this->debug;
    }

    /**
     * Save or print more info on the server side
     *
     * Generated from protobuf field <code>bool debug = 10;</code>
     * @param bool $var
     * @return $this
     */
    public function setDebug($var)
    {
        GPBUtil::checkBool($var);
        $this->debug = $var;

        return $this;
    }

    /**
     * Used for passing algorithm specific options
     *
     * Generated from protobuf field <code>repeated .Attribute attributes = 8;</code>
     * @return \Google\Protobuf\Internal\RepeatedField
     */
    public function getAttributes()
    {
        return $this->attributes;
    }

    /**
     * Used for passing algorithm specific options
     *
     * Generated from protobuf field <code>repeated .Attribute attributes = 8;</code>
     * @param \Attribute[]|\Google\Protobuf\Internal\RepeatedField $var
     * @return $this
     */
    public function setAttributes($var)
    {
        $arr = GPBUtil::checkRepeatedField($var, \Google\Protobuf\Internal\GPBType::MESSAGE, \Attribute::class);
        $this->attributes = $arr;

        return $this;
    }

}
