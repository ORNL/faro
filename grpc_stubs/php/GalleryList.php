<?php
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: faro/proto/face_service.proto

use Google\Protobuf\Internal\GPBType;
use Google\Protobuf\Internal\RepeatedField;
use Google\Protobuf\Internal\GPBUtil;

/**
 * Generated from protobuf message <code>GalleryList</code>
 */
class GalleryList extends \Google\Protobuf\Internal\Message
{
    /**
     * Generated from protobuf field <code>repeated .GalleryInfo galleries = 1;</code>
     */
    private $galleries;

    /**
     * Constructor.
     *
     * @param array $data {
     *     Optional. Data for populating the Message object.
     *
     *     @type \GalleryInfo[]|\Google\Protobuf\Internal\RepeatedField $galleries
     * }
     */
    public function __construct($data = NULL) {
        \GPBMetadata\Faro\Proto\FaceService::initOnce();
        parent::__construct($data);
    }

    /**
     * Generated from protobuf field <code>repeated .GalleryInfo galleries = 1;</code>
     * @return \Google\Protobuf\Internal\RepeatedField
     */
    public function getGalleries()
    {
        return $this->galleries;
    }

    /**
     * Generated from protobuf field <code>repeated .GalleryInfo galleries = 1;</code>
     * @param \GalleryInfo[]|\Google\Protobuf\Internal\RepeatedField $var
     * @return $this
     */
    public function setGalleries($var)
    {
        $arr = GPBUtil::checkRepeatedField($var, \Google\Protobuf\Internal\GPBType::MESSAGE, \GalleryInfo::class);
        $this->galleries = $arr;

        return $this;
    }

}

