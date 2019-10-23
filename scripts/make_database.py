#!/usr/bin/env python
import pickle
from pathlib import Path
from sqlalchemy import create_engine # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.types import Integer, PickleType, String # type: ignore
from sqlalchemy.schema import Column # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from sqlalchemy.exc import IntegrityError # type: ignore
#from prefect import task, Flow

FILES_DIR = 'files'
DB_URI = 'sqlite:///adlproj_db.sqlite3'

Base = declarative_base()

class Picture(Base):
    __tablename__ = 'pictures'
    img_id = Column(Integer, primary_key=True)
    embedding = Column(PickleType, nullable=False)
    label = Column(Integer, nullable=False)
    jpg_path = Column(String(120), nullable=False)


if __name__=='__main__':

    engine = create_engine(DB_URI)
    if len(Base.metadata.tables) < 1:
        print("making tables")
        Base.metadata.create_all(bind=engine, checkfirst=True)
    else:
        print("dropping than making")
        Base.metadata.drop_all(bind=engine, checkfirst=True)
        Base.metadata.create_all(bind=engine, checkfirst=True)

    Session = sessionmaker(bind=engine)
    sess = Session()

    with open(f"../{FILES_DIR}/dataframe.pickle", "rb") as df_pickle:
        print('loading dataframe')
        df = pickle.load(df_pickle)

    labels = df.labels
    embeddings = df.drop('labels', axis=1).values
    indices = df.index

    for label, embedding, index in zip(labels, embeddings, indices):
        path_str = f'../{FILES_DIR}/adl-jpgs/hate-symbols-db-{index:04d}.jpg'
        path = Path(path_str).resolve()
        embedding = Picture(img_id=index, embedding=embedding, label=label, jpg_path=str(path))
        sess.add(embedding)

    sess.commit()
    sess.close()
