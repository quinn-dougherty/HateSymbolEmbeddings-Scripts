#!/usr/bin/env bash

# set env vars
FILES_DIR=files
JPGS_DIR=adl-jpgs

# i haven't verified whether this is strictly necessary.
source activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)

# check for files and files/adl-jpgs directories,
# creating them if they don't exist
if test -d "$FILES_DIR" ; then
    echo "directory $FILES_DIR exists"
    if test -d "$FILES_DIR/$JPGS_DIR" ; then
        echo "directory $FILES_DIR/$JPGS_DIR exists"
    else
        echo "making $FILES_DIR/$JPGS_DIR directory" && \
        mkdir "$FILES_DIR/$JPGS_DIR"
    fi
else
    echo "making $FILES_DIR directory" && mkdir "$FILES_DIR"
    echo "making $FILES_DIR/$JPGS_DIR directory" && \
        mkdir "$FILES_DIR/$JPGS_DIR"
fi

# if adl-jpgs is empty then run python script to fill it,
# else assume it's full
if [ "$(ls -A $FILES_DIR/$JPGS_DIR)" ]; then
     echo "photos are already downloaded"
else
    echo "i'll download photos. "
    python scripts/download_jpgs.py
fi

# if *.pickle not in files then run python script to build it
# else assume *.pickles are there
if [ "$(ls $FILES_DIR | grep dataframe)" ]; then
    echo "dataframe is already created. "
else
    echo "making dataframe"
    python scripts/build_df.py
fi

if [ "$(ls $FILES_DIR | grep classifier)" ]; then
    echo "classifier is already trained"
else
    echo "training classifier"
    python scripts/cluster_similarity.py
fi

if [ "$(ls $FILES_DIR | grep neighbors)" ]; then
    echo "neighbors is already trained"
else
    echo "training neighbors"
    python scripts/nearest_neighbors.py
fi
