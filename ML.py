import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import PolynomialFeatures
import matplotlib.pyplot as plt
from sklearn.utils import resample
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import scale
from sklearn.svm import SVC
from sklearn import metrics
from sklearn.metrics import ConfusionMatrixDisplay

class knn_create:
    x = []
    y = []
    c = []
    new_y = []
    new_x = []
    normaled = False
    def __init__(self, **kargs) -> None:
        self.n = kargs.get('n')
        self.knn = KNeighborsClassifier(n_neighbors=self.n)
    
    def get_arrays(self,X : list, Y: list, C: list):
        self.x = X
        self.y = Y
        self.c = C
    
    def set_neighbors(self, N : int):
        self.n = N
        self.knn = KNeighborsClassifier(n_neighbors=self.n)

    def fit_ML(self):
        self.data = list(zip(self.x, self.y))
        self.knn.fit(self.data, self.c)

    def predict(self, x : list, y : list):
        try:
            if self.normaled:
                for _ in range(len(x)):
                    self.new_x.append(x[_]/self.max_x)
                    self.new_y.append(y[_]/self.max_y)
            else:
                self.new_x = x
                self.new_y = y
        except:
            pass

        self.fit_ML()
        new_points = list(zip(x, y))
        prediction = []
        for point in new_points:
            prediction.append(self.knn.predict([point])[0])
        print(prediction)
        self.plot_knn(x, y, prediction)

    def normal(self):
        self.max_x = max(self.x)
        self.max_y = max(self.y)

        for i in range(len(self.x)):
            self.x[i] = (self.x[i]-min(self.x))/(self.max_x - min(self.x))
            self.y[i] = (self.y[i]-min(self.y))/(self.max_y - min(self.y))
        self.normaled = True
   
    def plot_knn(self, x = [], y = [], c = []):
        plt.scatter(self.x + x, self.y + y, c=self.c + c)
        for coord in range(len(x)):
            plt.text(x[coord], y[coord], s=f'{c[coord]}')
        plt.show() 

class Regression:
    def __init__(self, x : list, y : list, degree : int) -> None:
        self.x = np.array(x).reshape((-1, 1))
        self.y = np.array(y)
        self.degree = degree
        self.poly_reg = PolynomialFeatures(self.degree)
        self.x_poly = self.poly_reg.fit_transform(self.x)
        self.lin_reg_model = LinearRegression()
        self.lin_reg_model.fit(self.x_poly, self.y)
        self.y_pred = self.lin_reg_model.predict(self.x_poly)
        self.rmse = mean_squared_error(self.y, self.y_pred)
        print(self.rmse)
    
    def plot(self):
            plt.scatter(self.x, self.y, color='green', label='')
            plt.plot(self.x, self.y_pred, color="blue", label='')
            plt.title("Polynomial Regression")
            plt.xlabel('X')
            plt.ylabel('y')
            plt.show()
    
    def predict_new_point(self, x):
        res = self.lin_reg_model.intercept_
        for _ in range(1, len(self.lin_reg_model.coef_)):
            res += self.lin_reg_model.coef_[_] * pow(x, _)
        return res

class Regression1:
    def __init__(self, **kargs) -> None:
        self.modelcheck = False
        self.new_modelcheck = False
    
    def set_x(self, x : list):
        self.reg_x = x
    
    def set_y(self, y : list):
        self.reg_y = y

    def set_degree(self, degree : int):
        self.degree = degree
    
    def create_model(self):
        try:
            self.mymodel = np.poly1d(np.polyfit(self.reg_x, self.reg_y, self.degree))   
            self.modelcheck = True  
        except:
            self.modelcheck = False
            self.new_modelcheck = False

    def plot(self)->None:
        start = min(min(self.reg_x),min(self.reg_y))
        end = max(max(self.reg_x),max(self.reg_y))
        step = int((end-start)/0.1)
        self.myline = np.linspace(start, end, step)
        plt.scatter(self.reg_x, self.reg_y)
        plt.plot(self.myline, self.mymodel(self.myline))
        plt.show() 
    
    def predict_new_point(self, x : float|int)->None:
        try:
            self.new_x = x
            self.new_y = self.mymodel(self.new_x)
            self.new_modelcheck = True
        except:
            self.new_modelcheck = False

    def plot_new_point(self):
        start = min(self.reg_x + [self.new_x])
        end = max(self.reg_x + [self.new_x])
        step = (len(self.reg_x) + 1) * 10
        self.myline = np.linspace(start, end, step)
        plt.scatter(self.reg_x + [self.new_x], self.reg_y + [self.new_y])
        plt.plot(self.myline, self.mymodel(self.myline))
        plt.show() 
    
    def get_rmse(self):
        rmse = mean_squared_error(self.reg_y, self.mymodel(self.reg_x))
        return rmse

class SVM:
    def __init__(self, **kw) -> None:
        self.ignored_cols = []
        self.plot_text = ''
        self.random = kw.get('random')

    def Load(self, path):
        self.df = pd.read_csv(path, header=0)

    def convert_tree_to_df(self, Tree : list[list])->None:
        """converts a list of lists to a dataframe
        >>> creates self.df"""
        columns = Tree[0]
        data = []
        for id in range(1, len(Tree)):
            self.data.append(Tree[id])
        data = np.array(data)
        self.df = pd.DataFrame(data=data, columns=columns)
    
    def get_column_names(self, cls)->None:
        """takes the class column's name
        >>> create and modify self.cls
        >>> modify self.ignored_cols"""
        self.cls = cls #class column
        self.ignored_cols.append(self.cls)
    
    def get_data_columns(self, columns : list)->None:
        """takes specified columns for analysing
        >>> creates self.columns
        >>> update self.ignored_cols"""
        self.columns = columns
        for column in self.df.columns:
            if column not in columns:
                self.ignored_cols.append(column)
    
    def reset(self)->None:
        self.ignored_cols = []
        self.cls = None
                
    def training_data(self)->None:
        """splits columns and encodes
        >>> creates self.X, self.y and self.X_encoded
        >>> uses self.ignored_cols and self.cls and self.df"""
        self.X = self.df.drop(self.ignored_cols,axis=1)
        self.y = self.df[self.cls].copy()
        
    
    def main(self, optimize : bool = False, test_size : float = None, train_size : float = None)->None:
        """creates the support vector machine model after training_data
            >>> optimize : choose to optimize the results or not
                if True:
                    more accurate results
                    takes longer with analysing
                    worse with very small data bases but perfect for medium sized data bases
                if False:
                    less accurate results
                    takes less timer to generate the test results
                    works best with very small samples
            >>> test_size : choose to specify the size of the testing data, range= ]0, 1.0[ (default=0.25)
            >>> train_size : choose to specify the size of the training data, range= ]0, 1.0[ (default=0.75)"""
        if optimize:
            self.X_encoded = pd.get_dummies(self.X,columns=self.columns)
            self.X_train, self.X_test, Y_train, Y_test = train_test_split(self.X_encoded, self.y, test_size=test_size, train_size=train_size, random_state=self.random)
            
            self.X_train_scaled = scale(self.X_train)
            self.X_test_scaled = scale(self.X_test)
            param_grid={
                'C':[0.5,1,10,100],
                'gamma':['scale',1,0.1,0.01,0.001,0.0001],
                'kernel':['rbf']
            }
            optimal_params = GridSearchCV(SVC(),
                                        param_grid=param_grid,
                                        cv=5,
                                        scoring='accuracy',
                                        verbose=0)
            
            optimal_params.fit(self.X_train_scaled,Y_train)
            self.clf_svm = SVC(random_state=self.random, C=optimal_params.best_params_.get('C'), gamma=optimal_params.best_params_.get('gamma'),kernel=optimal_params.best_params_.get('kernel'),probability=True)
            self.clf_svm.fit(self.X_test_scaled, Y_test)
            self.plot_text = 'Optimized learing'
        
        else:
            self.X_train, self.X_test, Y_train, Y_test = train_test_split(self.X, self.y, test_size=test_size, train_size=train_size, random_state=self.random)
            self.X_train_scaled = scale(self.X_train)
            self.X_test_scaled = scale(self.X_test)
            self.clf_svm = SVC(random_state = self.random, probability=True)
            self.clf_svm.fit(self.X_train_scaled, Y_train)
            self.plot_text = 'Regular learning'

        # print(self.X_test)

        matrix = ConfusionMatrixDisplay.from_estimator(self.clf_svm,
                                                            X=self.X_test_scaled,
                                                            y=Y_test,
                                                            values_format='d')
        self.results(self.clf_svm,self.X_test_scaled,Y_test)
    
    #for large data bases
    def split_data_and_sample(self, n : int)->None:
        """ splits all classes into multiple dataframes inside a list
            called before training_data
            >>> n : number of samples taken from each class
            >>> modify self.df """
        #spliting columns based of class
        data = []
        for cls in self.df[self.cls].unique():
            data.append(self.df[self.df[self.cls] == cls])
        #getting n number of samples of each column
        sample = []
        for df in data:
            sample.append(resample(df,
                                    replace = False,
                                    n_samples = n,
                                    random_state = self.random))
        self.df = pd.concat([data for data in sample])

    def predict_point(self,optimize : bool = False, new_data : list = []):
        if not optimize:
            X = np.append(self.X_test, [new_data], axis=0)
            X = scale(X)
            y_pred = (self.clf_svm.predict([X[-1]]))
            y_prob = self.clf_svm.predict_proba([X[-1]])[0]
            print(y_pred)
            print(y_prob)
        else:
            cols = self.X_test.columns

            X = pd.DataFrame(data=[[False] * len(cols)], columns=cols)
            try:
                X.insert(len(X.columns),f'Age_{new_data[0]}',True)
            except ValueError:
                X[f'Age_{new_data[0]}'] = True
            try:
                X.insert(len(X.columns),f'Salary_{new_data[1]}',True)
            except ValueError:
                X[f'Salary_{new_data[1]}'] = True

            print(X)
            try:
                self.X_test.insert(len(self.X_test.columns), f'Age_{new_data[0]}', [False] * len(self.X_test.index))
            except ValueError:
                pass
            try:
                self.X_test.insert(len(self.X_test.columns), f'Salary_{new_data[1]}', [False] * len(self.X_test.index))
            except ValueError:
                pass

            X = np.append(self.X_test, X, axis=0)
            X = scale(X)
            y_pred = (self.clf_svm.predict([X[-1]]))
            y_prob = self.clf_svm.predict_proba([X[-1]])[0]
            print(y_pred)
            print(y_prob)

            
        

    def results(self, model : SVC, x_text, y_test):
        pred = model.predict(x_text)
        print('-'*40)
        print('accuracy:', metrics.accuracy_score(y_test,pred))
        print('precision:', metrics.precision_score(y_test,pred))
        print('recall:', metrics.recall_score(y_test,pred))
        print('F1-score:', metrics.f1_score(y_test,pred))
        print('-'*40)

    def plot_matrix(self):
        plt.title(self.plot_text)
        plt.show()
if __name__ == '__main__':
    """
    self.df contain all data from the tree
    self.X contain specified data
    self.y is the class data
    df = X + y
    """
    tree = [['Age','Salary','Purchased'],
            [1,2,1],
            [5,3,0],
            [3,3,0],
            [2,0,1],
            [5,2,0]]
    app = SVM(random=42)
    # app.convert_tree_to_df(tree)
    app.Load('customer_purchases.csv')
    app.get_column_names('Purchased')
    app.get_data_columns(['Age','Salary'])
    # app.split_data_and_sample(20)
    app.training_data()
    app.main(True)
    app.predict_point(optimize=True, new_data=[10,10000])
    # app.plot_matrix()
