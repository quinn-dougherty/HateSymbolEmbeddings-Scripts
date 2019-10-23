#!/usr/bin/env python

import os
import sys
from typing import List
from pathlib import Path
import pickle

from numpy import ndarray # type: ignore
from pandas import DataFrame # type: ignore
from sklearn.cluster import KMeans # type: ignore
from sklearn.decomposition import PCA # type: ignore
from sklearn.linear_model import LogisticRegression # type: ignore
from sklearn.pipeline import Pipeline # type: ignore

from basilica import Connection # type: ignore
from prefect import task, Flow

from settings import BASILICA_KEY, DIREC, FILES_DIR

@task
def get_jpgs_list(direc: str = DIREC) -> List[str]:
    jpgs_list = [f"{FILES_DIR}/{direc}/{f}" for f in os.listdir(f"{FILES_DIR}/{direc}")]
    # print(jpgs_list)

    if len(jpgs_list)==0:
        raise Exception("please scrape for images first!")
    else:
        return jpgs_list

@task
def get_embedding(jpg: str) -> List[float]:
    with Connection(BASILICA_KEY) as c:
        x = c.embed_image_file(jpg)

    return x

@task
def get_frame(embeddings: List[List[float]]) -> DataFrame:
    return DataFrame(embeddings)

@task
def label_frame(df: DataFrame, width_factor_PCA: int = 5, K: int = 10) -> DataFrame:
    df_ = DataFrame(PCA(n_components=df.shape[0]//width_factor_PCA).fit_transform(df))

    km = KMeans(n_clusters = K)
    km.fit(df_)
    return df.assign(labels=km.labels_)

with Flow("create and label dataframe of basilica embeddings, train model") as flow:

    # executor = DaskExecutor(local_processes=True)

    # make iterable of jpg files
    jpgs = get_jpgs_list()

    # send iterable to basilica
    embeddings = get_embedding.map(jpgs)

    df_ = get_frame(embeddings)

    # make labels (kmeans)
    df = label_frame(df_)

    # train model
    pipe = train_model(df)

    state = flow.run()

#     model = state.result[pipe].result

    dataframe = state.result[df].result

   
    if not state.is_failed():

        print("it appears we're in business. pickling dataframe and model now. ")
       
#       with open(f'{FILES_DIR}/model.pickle', "wb") as model_pickle:
#           pickle.dump(model, model_pickle)

        with open(f"{FILES_DIR}/dataframe.pickle", "wb") as df_pickle:
            pickle.dump(dataframe, df_pickle)

    else:
        print(f"sorry, no pickles for you. state: {state}")
        for stage, reason in state.result.items():
            print(stage, reason)
