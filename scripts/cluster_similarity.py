#!/usr/bin/env python
import pickle

from prefect import task, Flow
from numpy import ndarray # type: ignore
from pandas import DataFrame # type: ignore
from sklearn.cluster import KMeans # type: ignore
from sklearn.decomposition import PCA # type: ignore
from sklearn.linear_model import LogisticRegression # type: ignore
from sklearn.pipeline import Pipeline # type: ignore

from settings import DIREC, FILES_DIR


@task
def load_df() -> DataFrame:
    with open(f"{FILES_DIR}/dataframe.pickle", "rb") as df_pickle:
        df = pickle.load(df_pickle)
    return df

@task
def train_model(df: DataFrame, width_factor: int = 5) -> Pipeline:
    X = df.drop('labels', axis=1)
    y = df.labels

    lr = LogisticRegression(solver='lbfgs', multi_class='auto', max_iter=1000)
    pca = PCA(n_components = df.shape[0]//width_factor)

    pipe = Pipeline([
        ('pca', pca),
        ('lr', lr)
    ])

    pipe.fit(X, y)
    return pipe

with Flow("train logistic regression") as flow:

    # get df
    df = load_df()

    pipe = train_model(df)

    state = flow.run()

    classifier = state.result[pipe].result

    if not state.is_failed():
        print("logistic regression success. pickling model now")

        with open(f'{FILES_DIR}/classifier.pickle', 'wb') as classifier_pickle:
            pickle.dump(classifier, classifier_pickle)
    else:
        print(f"sorry, we have a problem: {state}")
        for stage, reason in state.result.items():
            print(stage, reason)
