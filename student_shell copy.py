import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.linear_model import LogisticRegression, LinearRegression
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

# Function to run the AutoML pipeline
def run_pipeline():
    xve = X_var_entry.get()
    yve = y_var_entry.get()
    fpv = file_path_var.get()
    p = problem_type_var.get()

    #imports data
    origData = pd.read_csv(fpv)
    df = origData
    #del df['full_name']

    #checks for missing values
    #print(df.isnull().any())

    #fills missing values
    df = df.fillna(df.mode().iloc[0])
    #print(df.head())

    #scaling
    numerical_columns = df.select_dtypes(include=[np.number]).columns.tolist()
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
    df_encoded = df.apply(LabelEncoder().fit_transform)
    print(df_encoded.head())
    #getting columns in x
    abc = df_encoded.columns.get_loc(yve)
    #abcd = df_encoded.columns.get_loc('Unnamed: 32')
    test2 = []
    test3 = []
    for i in range(len(df_encoded.columns)):
        if(i != abc):
            test2.append(i)
    for i in range(len(test2)):
        test3.append(df_encoded.columns[test2[i]])

    #sets x and y
    if(p == "Regression"):
        X = df_encoded[[xve]]
        y = df_encoded[yve]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LinearRegression()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        rmse = root_mean_squared_error(y_test, y_pred)
        print(f'Root Mean Squared Error: {rmse}')

        plt.figure(figsize=(10, 6))
        plt.scatter(X, y, color='blue', label='Data points')
        plt.plot(X, model.predict(X), color='red', linewidth=2, label='Regression line')
        plt.xlabel(xve)
        plt.ylabel(yve)
        plt.title('Linear Regression: '+ xve + " vs " + yve)
        plt.legend()
        plt.show()
    else:
        X = df_encoded[test3]
        y = df_encoded[yve]
        #X.to_numpy()
        #y.to_numpy()

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        rf_clf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_clf.fit(X_train, y_train)
        y_pred_rf = rf_clf.predict(X_test)
        accuracy_rf = accuracy_score(y_test, y_pred_rf)
        f1_rf = f1_score(y_test, y_pred_rf)
        precision_rf = precision_score(y_test, y_pred_rf)
        recall_rf = recall_score(y_test, y_pred_rf)
        #printing scores/evaulation
        print(f'Accuracy (Random Forest): {accuracy_rf}')
        print(f'F1 (Random Forest): {f1_rf}')
        print(f'Precision (Random Forest): {precision_rf}')
        print(f'Recall (Random Forest): {recall_rf}')
        print('Classification Report (Random Forest):')
        print(classification_report(y_test, y_pred_rf))
    # TODO Write this function - DO NOT use ChatGPT, if you have trouble updating the GUI print to the console
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
tk.Radiobutton(root, text="Regression", variable=problem_type_var, value="Regression").grid(row=4, column=1)

tk.Button(root, text="Run Pipeline", command=run_pipeline).grid(row=5, columnspan=3, pady=20)

results_label = tk.Label(root, text="", justify=tk.LEFT, font=("Helvetica", 12))
results_label.grid(row=6, columnspan=3, padx=10, pady=10)

# Run the application
root.mainloop()
