#!/usr/bin/env python

import pickle
import pandas as pd
from pandas import DataFrame
from sklearn.neighbors import NearestNeighbors

from prefect import task, Flow
from settings import FILES_DIR

@task
def load_df() -> DataFrame:
    with open(f"{FILES_DIR}/dataframe.pickle", "rb") as df_pickle:
        df = pickle.load(df_pickle)
    return df

@task
def train_neighbors(df: DataFrame) -> NearestNeighbors:
    knn = NearestNeighbors(n_neighbors=20)
    knn.fit(df)
    return knn

with Flow("training nearest neighbors") as flow:

    df = load_df()

    knn = train_neighbors(df)

    state = flow.run()

    neighbors = state.result[knn].result

    if not state.is_failed():
        print("k nearest neighbors success. pickling model now. ")
        with open(f"{FILES_DIR}/neighbors.pickle", 'wb') as neighbs_pickle:
            pickle.dump(neighbors, neighbs_pickle)
    else:
        print(f"sorry, we have a problem: {state}")
        for stage, reason in state.result.items():
            print(stage, reason)

