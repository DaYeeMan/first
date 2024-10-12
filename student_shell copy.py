import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler, OneHotEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, root_mean_squared_error, r2_score
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
import numpy as np
import seaborn as sns
from sklearn import preprocessing
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from ucimlrepo import fetch_ucirepo 
from mlxtend.evaluate import paired_ttest_5x2cv
from scipy.stats import ttest_rel


# Function to run the AutoML pipeline
def run_pipeline():
    #getting user input
    xve = X_var_entry.get()
    yve = y_var_entry.get()
    fpv = file_path_var.get()
    p = problem_type_var.get()

    #imports data
    origData = pd.read_csv(fpv)
    df = origData

    #fills missing values using most frequent value in that column
    df = df.fillna(df.mode().iloc[0])
    #print(df.head())

    #scaling using standard scaler on all numerical columns
    numerical_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    if yve in numerical_columns:
        numerical_columns.remove(yve)
    scaler = StandardScaler()
    df[numerical_columns] = scaler.fit_transform(df[numerical_columns])
    """
    #oneHotEncoding
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
    encoder = OneHotEncoder(sparse_output=False)
    one_hot_encoded = encoder.fit_transform(df[categorical_columns])
    one_hot_df = pd.DataFrame(one_hot_encoded, columns=encoder.get_feature_names_out(categorical_columns))
    df_encoded = pd.concat([df, one_hot_df], axis=1)
    df_encoded = df_encoded.drop(categorical_columns, axis=1)

    #df.drop('Unnamed: 32', axis=1, inplace=True)
    """
    #encoding categorical columns with label encoding
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
    df[categorical_columns] = df[categorical_columns].apply(LabelEncoder().fit_transform)
    print(df.head())

    #getting the non target columns into X which will be used in classification
    #there is probably a better way to do this
    abc = df.columns.get_loc(yve)
    test2 = []
    test3 = []
    for i in range(len(df.columns)):
        if(i != abc):
            test2.append(i)
    for i in range(len(test2)):
        test3.append(df.columns[test2[i]])

    #i moved train test split and the models out of the loop so i can run k fold cross validation
    X = df[test3]
    y = df[yve]
    #80 20 train test split using random seed
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    #using logistic regression which finds a probability between 0 and 1 for each class
    #uses one vs rest for multi class classification problems
    #turns a multiclass problem into a binary one
    log_reg = OneVsRestClassifier(LogisticRegression(max_iter=1000))
    #using random forest classification which uses decision trees to classify data
    rf_clf = RandomForestClassifier(n_estimators=100, random_state=42)

    if(p == "Regression"):
        log_reg.fit(X_train, y_train)
        y_pred = log_reg.predict(X_test)
        #using accuracy f1 precision and recall as eval metrics
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        #printing scores/evaulation
        print(f'Accuracy (Log Reg): {accuracy}')
        print(f'F1 (Log Reg): {f1}')
        print(f'Precision (Log Reg): {precision}')
        print(f'Recall (Log Reg): {recall}')
        print('Classification Report (Log Reg):')
        print(classification_report(y_test, y_pred))
    else:
        rf_clf.fit(X_train, y_train)
        y_pred_rf = rf_clf.predict(X_test)
        #using accuracy f1 precision and recall as eval metrics
        accuracy_rf = accuracy_score(y_test, y_pred_rf)
        f1_rf = f1_score(y_test, y_pred_rf, average=None)
        precision_rf = precision_score(y_test, y_pred_rf, average=None)
        recall_rf = recall_score(y_test, y_pred_rf, average=None)
        #printing scores/evaulation
        print(f'Accuracy (Random Forest): {accuracy_rf}')
        print(f'F1 (Random Forest): {f1_rf}')
        print(f'Precision (Random Forest): {precision_rf}')
        print(f'Recall (Random Forest): {recall_rf}')
        print('Classification Report (Random Forest):')
        print(classification_report(y_test, y_pred_rf))

    #k fold cross validation
    k_folds = KFold(n_splits = 5)
    scoresLR = cross_val_score(log_reg, X, y, cv = k_folds)
    scoresRf = cross_val_score(rf_clf, X, y, cv = k_folds)

    print("Cross Validation Scores (log_reg): ", scoresLR)
    print("Average CV Score (log_reg): ", scoresLR.mean())

    print("Cross Validation Scores (rf): ", scoresRf)
    print("Average CV Score (rf): ", scoresRf.mean())

    #using a t test to compare the 2 models
    #t, p = paired_ttest_5x2cv(estimator1=log_reg,estimator2=rf_clf,X=X, y=y)
    t, p = ttest_rel(scoresLR, scoresRf)
    alpha = 0.05

    print('t statistic: %.3f' % t)
    print('aplha ', alpha)
    print('p value: %.3f' % p)

    #interpreting the t test results
    if p > alpha:
        print("No signifigant difference between the 2 models")
    else:
        print("Signifigant difference between the 2 models")
    pass

# Function to select file
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    file_path_var.set(file_path)

# Create the main window
root = tk.Tk()
root.title("AutoML Pipeline")

# Create and place the widgets
tk.Label(root, text="AutoML Pipeline", font=("Helvetica", 16)).grid(row=0, columnspan=2, pady=10)

tk.Label(root, text="Select Dataset:").grid(row=1, column=0, sticky=tk.W, padx=10)
file_path_var = tk.StringVar()
tk.Entry(root, textvariable=file_path_var, width=50).grid(row=1, column=1, padx=10)
tk.Button(root, text="Browse", command=select_file).grid(row=1, column=2, padx=10)

tk.Label(root, text="Predictor Variable (X):").grid(row=2, column=0, sticky=tk.W, padx=10)
X_var_entry = tk.Entry(root, width=20)
X_var_entry.grid(row=2, column=1, padx=10)

tk.Label(root, text="Target Variable (y):").grid(row=3, column=0, sticky=tk.W, padx=10)
y_var_entry = tk.Entry(root, width=20)
y_var_entry.grid(row=3, column=1, padx=10)

tk.Label(root, text="Problem Type:").grid(row=4, column=0, sticky=tk.W, padx=10)
problem_type_var = tk.StringVar(value="Classification")
tk.Radiobutton(root, text="Classification", variable=problem_type_var, value="Classification").grid(row=4, column=1, sticky=tk.W)
tk.Radiobutton(root, text="Logistic Regression", variable=problem_type_var, value="Regression").grid(row=4, column=1)

tk.Button(root, text="Run Pipeline", command=run_pipeline).grid(row=5, columnspan=3, pady=20)

results_label = tk.Label(root, text="", justify=tk.LEFT, font=("Helvetica", 12))
results_label.grid(row=6, columnspan=3, padx=10, pady=10)

# Run the application
root.mainloop()
