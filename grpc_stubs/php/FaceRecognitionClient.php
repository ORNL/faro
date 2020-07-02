<?php
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
namespace ;

/**
 */
class FaceRecognitionClient extends \Grpc\BaseStub {

    /**
     * @param string $hostname hostname
     * @param array $opts channel options
     * @param \Grpc\Channel $channel (optional) re-use channel object
     */
    public function __construct($hostname, $opts, $channel = null) {
        parent::__construct($hostname, $opts, $channel);
    }

    /**
     * Service info and defaults
     * @param \FaceStatusRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function status(\FaceStatusRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/status',
        $argument,
        ['\FaceServiceInfo', 'decode'],
        $metadata, $options);
    }

    /**
     * Simple operations
     * @param \DetectRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function detect(\DetectRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/detect',
        $argument,
        ['\FaceRecordList', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \ExtractRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function extract(\ExtractRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/extract',
        $argument,
        ['\FaceRecordList', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \ScoreRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function score(\ScoreRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/score',
        $argument,
        ['\Matrix', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \EnrollRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function enroll(\EnrollRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/enroll',
        $argument,
        ['\FaceRecordList', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \SearchRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function search(\SearchRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/search',
        $argument,
        ['\FaceRecordList', 'decode'],
        $metadata, $options);
    }

    /**
     * Combined opperations
     * @param \DetectExtractRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function detectExtract(\DetectExtractRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/detectExtract',
        $argument,
        ['\FaceRecordList', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \DetectExtractEnrollRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function detectExtractEnroll(\DetectExtractEnrollRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/detectExtractEnroll',
        $argument,
        ['\FaceRecordList', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \DetectExtractSearchRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function detectExtractSearch(\DetectExtractSearchRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/detectExtractSearch',
        $argument,
        ['\FaceRecordList', 'decode'],
        $metadata, $options);
    }

    /**
     * Gallery Management
     * @param \GalleryListRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function galleryList(\GalleryListRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/galleryList',
        $argument,
        ['\GalleryList', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \GalleryDeleteRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function galleryDelete(\GalleryDeleteRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/galleryDelete',
        $argument,
        ['\PBEmpty', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \EnrollmentListRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function enrollmentList(\EnrollmentListRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/enrollmentList',
        $argument,
        ['\FaceRecordList', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \EnrollmentDeleteRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function enrollmentDelete(\EnrollmentDeleteRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/enrollmentDelete',
        $argument,
        ['\FaceRecordList', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \EnrollmentDeleteRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function enrollmentDeleteConditional(\EnrollmentDeleteRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/enrollmentDeleteConditional',
        $argument,
        ['\FaceRecordList', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \EnrollmentDeleteRequest $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function enrollmentTransfer(\EnrollmentDeleteRequest $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/enrollmentTransfer',
        $argument,
        ['\FaceRecordList', 'decode'],
        $metadata, $options);
    }

    /**
     * Test
     * @param \Matrix $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function echo(\Matrix $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/FaceRecognition/echo',
        $argument,
        ['\Matrix', 'decode'],
        $metadata, $options);
    }

}
