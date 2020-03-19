#!/bin/python3
#coding:utf-8
#Copyright 2019 Alphaplato. All Rights Reserved.
#Desc:structed model
#=======================================================
import tensorflow as tf
import multiprocessing

MULTI_THREADING = True

class Model(object):
    def __init__(self,fg,md):
        self.fg = fg
        self.md = md

    def _parser(self,record):
        fea_dict = {}
        for fea in self.fg._feature_json['features']:
            if fea['value_type'] == 'Double':
                fea_dict[fea['feature_name']] = tf.FixedLenFeature(shape=[1],dtype=tf.float32)
            elif fea['value_type'] == 'String':
                fea_dict[fea['feature_name']] = tf.VarLenFeature(tf.string)
        fea_dict['label'] = tf.FixedLenFeature(shape=[1],dtype=tf.int64)
        features = tf.parse_single_example(record, fea_dict)
        label =  features.pop('label')
        return features,label

    def input_fn(self,data_path,mode=tf.estimator.ModeKeys.TRAIN,batch_size=1,num_epochs=1):
        num_threads = multiprocessing.cpu_count() if MULTI_THREADING else 1
        dataset = tf.data.TFRecordDataset(data_path,num_parallel_reads=num_threads)
        dataset = dataset.map(self._parser).repeat(num_epochs).batch(batch_size)
        features,label = dataset.make_one_shot_iterator().get_next()
        return features,label

    def model_fn(self,features,labels,mode,params): 
        optimizer = params['optimizer'] 
        learning_rate = params['learning_rate']

        y_out = self.md.build_logits(features,mode,params)
        
        labels = tf.cast(labels,tf.float32)
        pred = tf.sigmoid(y_out) 

        predictions={"prob": pred}
        if mode == tf.estimator.ModeKeys.PREDICT:
            return tf.estimator.EstimatorSpec(
                mode=mode,
                predictions=predictions,
                export_outputs=export_outputs)

        export_outputs = {tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: tf.estimator.export.PredictOutput(predictions)}            
        
        loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=y_out, labels=labels)) + \
            tf.losses.get_regularization_loss()
        eval_metric_ops = {
            "auc": tf.metrics.auc(labels, pred)
            }
        if mode == tf.estimator.ModeKeys.EVAL:
            return tf.estimator.EstimatorSpec(
                mode=mode,
                predictions=predictions,
                loss=loss,
                eval_metric_ops=eval_metric_ops)

        if optimizer == 'Adam':
            optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate, beta1=0.9, beta2=0.999, epsilon=1e-8)
        elif optimizer == 'Adagrad':
            optimizer = tf.train.AdagradOptimizer(learning_rate=learning_rate, initial_accumulator_value=1e-8)
        elif optimizer == 'Momentum':
            optimizer = tf.train.MomentumOptimizer(learning_rate=learning_rate, momentum=0.95)
        elif optimizer == 'ftrl':
            optimizer = tf.train.FtrlOptimizer(learning_rate)

        train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())

        if mode == tf.estimator.ModeKeys.TRAIN:
            return tf.estimator.EstimatorSpec(
                mode=mode,
                predictions=predictions,
                loss=loss,
                train_op=train_op)