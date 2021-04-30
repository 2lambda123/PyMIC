# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import csv 
import sys
import math
import pandas as pd
import random
import configparser
import numpy as np
import sklearn.metrics as metrics
from scipy import ndimage
from pymic.io.image_read_write import *
from pymic.util.image_process import *
from pymic.util.parse_config import parse_config

def accuracy(gt_label, pred_label):
    correct_pred = gt_label == pred_label
    acc = (correct_pred.sum() + 0.0 ) / len(gt_label)
    return acc 

def sensitivity(gt_label, pred_label):
    pos_pred = gt_label * pred_label
    senst = (pos_pred.sum() + 0.0) / gt_label.sum() 
    return senst

def specificity(gt_label, pred_label):
    gt_label = 1 - gt_label
    pred_label = 1 - pred_label
    neg_pred = gt_label * pred_label
    spec = (neg_pred.sum() + 0.0) / gt_label.sum() 
    return spec 

def get_evaluation_score(gt_label, pred_prob, metric):
    """
    the gt_label is 1-d array
    currently only binary classification is considered
    """
    pred_lab = np.argmax(pred_prob, axis = 1)
    if(metric == "accuracy"):
        score = metrics.accuracy_score(gt_label, pred_lab)
    elif(metric == "recall" or metric == "sensitivity"):
        score = metrics.recall_score(gt_label, pred_lab)
    elif(metric == "specificity"):
        score = metrics.recall_score(1 - gt_label, 1 - pred_lab)
    elif(metric == "precision"):
        score = metrics.precision_score(gt_label, pred_lab)
    elif(metric == "auc"):
        score = metrics.roc_auc_score(gt_label, pred_prob[:,1])
    else:
        raise ValueError("undefined metric: {0:}".format(metric))
    return score

def binary_evaluation(config_file):
    config = parse_config(config_file)['evaluation']
    metric_list = config['metric_list']
    gt_csv  = config['ground_truth_csv']
    prob_csv= config['predict_prob_csv']
    gt_items  = pd.read_csv(gt_csv)
    prob_items = pd.read_csv(prob_csv)
    assert(len(gt_items) == len(prob_items))
    for i in range(len(gt_items)):
        assert(gt_items.iloc[i, 0] == prob_items.iloc[i, 0])
    
    gt_data  = np.asarray(gt_items.iloc[:, 1])
    prob_data = np.asarray(prob_items.iloc[:, 1:])
    score_list = []
    for metric in metric_list:
        score = get_evaluation_score(gt_data, prob_data, metric)
        score_list.append(score)
        print("{0:}: {1:}".format(metric, score))


def main():
    if(len(sys.argv) < 2):
        print('Number of arguments should be 2. e.g.')
        print('    pymic_evaluate_cls config.cfg')
        exit()
    config_file = str(sys.argv[1])
    assert(os.path.isfile(config_file))
    binary_evaluation(config_file)
    
if __name__ == '__main__':
    main()
