import pandas
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler, OneHotEncoder

df = sns.load_dataset('iris')
x = df.iloc[:,0:4].values
y = df[['species']]
encoder = OneHotEncoder()
y = encoder.fit_transform(y).toarray()
print(y)