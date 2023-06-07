#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  Description: train a SVM model for remove the soil
  Author: yulu_ye16@163.com
'''

import numpy as np
from sklearn.svm import SVC
from sklearn import model_selection
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
from sklearn import metrics
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

os.chdir(r"F:\yeyulu\pythonProject\RGB")

df = np.loadtxt('samples.txt', skiprows=1)
x = df[:, 1:4]
y = df[:, 0].astype(int)

x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, test_size=0.2, random_state=1, shuffle=True)

reSoil_svc = SVC(kernel='poly', degree=3, decision_function_shape='ovo')

reSoil_svc.fit(x_train, y_train)
# 预测
train_predict = reSoil_svc.predict(x_train)
test_predict = reSoil_svc.predict(x_test)

#准确率
train_acc = accuracy_score(y_train, train_predict)
test_acc = accuracy_score(y_test, test_predict)
print ("SVM训练集准确率: {0:.3f}, SVM测试集准确率: {1:.3f}".format(train_acc, test_acc))

## 混淆矩阵
confusion_matrix_result = metrics.confusion_matrix(test_predict, y_test)
np.set_printoptions(precision=2)
confusion_matrix = confusion_matrix_result.astype('float') / confusion_matrix_result.sum(axis=1)[:, np.newaxis]
plt.figure(figsize=(8, 6), dpi=300)
sns.heatmap(confusion_matrix,annot=True, cmap='Blues')
plt.xlabel('Predicted labels')
plt.ylabel('True labels')
#print(confusion_matrix)
plt.show()

# K折交叉验证模块
from sklearn.model_selection import cross_val_score
#使用K折交叉验证模块
scores = cross_val_score(reSoil_svc, x, y, cv=10, scoring='accuracy', n_jobs=5)
#将10次的预测准确率打印出
print(scores)
print(scores.mean())

# 基于svm 实现分类  # 基于网格搜索获取最优模型
model = SVC(probability=True)
params = [
#{'kernel':['linear'],'C':[1,10,100,1000]},
#{'kernel':['poly'],'C':[1,10],'degree':[2,3]},
{'kernel':['rbf'],'C':[1,10,100,1000],
 'gamma':[1,0.1, 0.01, 0.001]}]
model = GridSearchCV(estimator=model, param_grid=params, cv=5)
model.fit(x, y)

# 网格搜索训练
print("模型的最优参数：", model.best_params_)
print("最优模型分数：", model.best_score_)
print("最优模型对象：", model.best_estimator_)

#最优参数训练
best_parameters = model.best_params_
reSoil_svc = SVC(**best_parameters)

reSoil_svc.fit(x_train, y_train)
train_predict = reSoil_svc.predict(x_train)
test_predict = reSoil_svc.predict(x_test)

#保存模型
joblib.dump(reSoil_svc, "/test/SvmRemoveSoil.m")
