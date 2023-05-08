import mlflow
import numpy as np
import pandas as pd
from airflow import DAG
from sklearn.datasets import load_iris
from datetime import datetime, timedelta
from sklearn.tree import DecisionTreeClassifier
from mlflow.models.signature import infer_signature
from sklearn.model_selection import train_test_split
from airflow.operators.python_operator import PythonOperator

default_args = {
    'owner': 'gustavo',
    'depends_on_past': False,
    'start_date': datetime(2023, 5, 6),
    'email': ['gust4vo-mlo@hotmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

dag = DAG(
    'train_iris_model',
    default_args=default_args,
    description='Train and log a decision tree model to MLflow',
    schedule_interval='0 0 15 * *', 
    tags=['ml', 'ds']
)

def train_model():

    iris = load_iris()
    iris.target = iris.target.reshape((iris.target.shape[0], 1))
    data = np.concatenate((iris.data, iris.target), axis=1)

    df = pd.DataFrame(data, columns = iris.feature_names + ['target'])
    X = df.drop('target', axis = 1)
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    clf = DecisionTreeClassifier()
    clf.fit(X_train, y_train)

    signature = infer_signature(X_train, clf.predict(X_train))
    score = clf.score(X_test, y_test)

    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("iris")
    with mlflow.start_run(run_name="run_" + datetime.now().strftime("%Y%m%d_%H%M%S")):
        mlflow.log_metric("score", score)
        mlflow.sklearn.log_model(clf, "decision_tree", signature=signature)

train_model_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag
)

train_model_task
