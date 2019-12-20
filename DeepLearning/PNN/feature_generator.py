#!/bin/python3
#coding:utf-8
#Copyright 2019 Alphaplato. All Rights Reserved.
#Desc:read tfrecord and generate feature columns
#=======================================================
import tensorflow as tf

class FeatureGenerator(object):
    def __init__(self,feature_json):
        self._feature_json = feature_json
        self._feature_generate()

    def _feature_generate(self):
        feature_columns = {}
        #deepfm lr feature columns process
        lr_feature_columns = {}
        for fea in self._feature_json['features']:
            if fea['feature_type'] == 'raw':
                lr_feature_columns[fea['feature_name']] = tf.feature_column.numeric_column(fea['feature_name'])
            elif fea['feature_type'] == 'id':
                x_feature = tf.feature_column.categorical_column_with_hash_bucket(fea['feature_name'],hash_bucket_size=fea['hash_size'])
                lr_feature_columns[fea['feature_name']] = tf.feature_column.embedding_column(x_feature,dimension=1)
        feature_columns['lr'] = lr_feature_columns
        #deepfm fm feature columns process
        fm_feature_columns = {}
        for fea in self._feature_json['features']:
            if fea['feature_type'] == 'raw':
                fm_feature_columns[fea['feature_name']] = tf.feature_column.numeric_column(fea['feature_name'])
            elif fea['feature_type'] == 'id':
                x_feature = tf.feature_column.categorical_column_with_hash_bucket(fea['feature_name'],hash_bucket_size=fea['hash_size'])
                fm_feature_columns[fea['feature_name']] = tf.feature_column.embedding_column(x_feature,dimension=fea['embedding'])
            raw_fields = [fea['feature_name'] for fea in self._feature_json['features']]
            x_feature = tf.feature_column.categorical_column_with_vocabulary_list('raw_fields',raw_fields)
            fm_feature_columns['raw_fields'] = tf.feature_column.embedding_column(x_feature,dimension=16)
          
        feature_columns['fm'] = fm_feature_columns       
        #deepfm deep feature columns process
        deep_feature_columns = {}
        for fea in self._feature_json['features']:
            if fea['feature_type'] == 'raw':
                deep_feature_columns[fea['feature_name']] = tf.feature_column.numeric_column(fea['feature_name'])
            elif fea['feature_type'] == 'id':
                x_feature = tf.feature_column.categorical_column_with_hash_bucket(fea['feature_name'],hash_bucket_size=fea['hash_size'])
                deep_feature_columns[fea['feature_name']] = tf.feature_column.embedding_column(x_feature,dimension=fea['embedding'])
        feature_columns['deep'] = deep_feature_columns
        self.feature_columns = feature_columns