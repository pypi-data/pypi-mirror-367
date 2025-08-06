
from .corr import describe,jb_test,normalize,positivation,pearson
from .linearRegression import ols,gls,hetero_test,vif,backward_stepwise_regression
from .classification import (softmax_classifier, hierarchical_clustering, svm, decisiontree_classify,
                             random_forest_classify, DecisionTree, RandomForest, _replace_cluster_numbers_with_strings)
from .evaluation import calculate_metrics,time_series_decomposition,grey_relation_analysis,entropy_weight_method
from matplotlib import pyplot as plt
plt.rcParams['font.family'] = ['Times New Roman','Simhei']
plt.rcParams['axes.unicode_minus']= False
__all__=['describe','jb_test','normalize','positivation','pearson','gls','ols']