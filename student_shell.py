import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
import numpy as np
import seaborn as sns
from sklearn import preprocessing

# Function to run the AutoML pipeline
def run_pipeline():
    xve = X_var_entry.get()
    yve = y_var_entry.get()
    fpv = file_path_var.get()
    p = problem_type_var.get()

    #imports data
    origData = pd.read_csv(fpv)
    df = origData
    #displays first 5 rows
    print(df.head())
    #checks for missing values
    print(df.isnull().any())

    #fills missing values
    df.fillna(df.mean(numeric_only=True).round(1), inplace=True)
    string_columns = df.select_dtypes(include=['object']).columns
    df[string_columns] = df[string_columns].fillna(df[string_columns].mode().iloc[0])
    #print(df.isnull().any())
    #changes categorical values to numbers
    le = preprocessing.LabelEncoder()
    for column_name in df.columns:
        if df[column_name].dtype == object:
            df[column_name] = le.fit_transform(df[column_name])
    else:
        pass
    #scales and normalizes data
    scaler = StandardScaler()
    ndf = scaler.fit_transform(df)
    normalized_df = pd.DataFrame(ndf, columns=df.columns)
    print("Raw Data")
    print(df.head())
    print("\nNormalized Data")
    print(normalized_df.head())
    if(p == "Regression"):
        X = df[[xve]]
        y = df[yve]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LinearRegression()
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        print(f'Mean Squared Error: {mse}')

        plt.figure(figsize=(10, 6))
        plt.scatter(X, y, color='blue', label='Data points')
        plt.plot(X, model.predict(X), color='red', linewidth=2, label='Regression line')
        plt.xlabel(xve)
        plt.ylabel(yve)
        plt.title('Linear Regression: '+ xve + " vs " + yve)
        plt.legend()
        plt.show()
    else:
        abc = df.columns.get_loc(yve)
        test2 = []
        test3 = []
        for i in range(len(df.columns)):
            if(i != abc):
                test2.append(i)
        limit = 5
        for i in range(len(test2)):
            if(i<limit):
                test3.append(df.columns[test2[i]])
        print(test3)

        X = df[test3]
        y = df[yve]
        X.to_numpy()
        y.to_numpy()

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        print(f'Accuracy: {accuracy}')
        print('Classification Report:')
        print(classification_report(y_test, y_pred))
        sns.pairplot(df, hue = yve, height=3, markers=["o", "s", "D"])
        plt.show()
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
