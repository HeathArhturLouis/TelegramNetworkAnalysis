from bertopic import BERTopic
import os

from sklearn.pipeline import make_pipeline
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

import config


def batched_lines(file_path, batch_size, right_column_offset=-2):
    with open(file_path, "r") as f:
        batch = []
        # Discard header
        f.readline()
        for line in f:
            cleaned_line = line.split(",")[right_column_offset]
            batch.append(cleaned_line)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch


def train_SVD_model(file_path, batch_size=1000, dim=100, n_topics=100, verbose=False):
    """
    Train a fast; CPU friendly bertopic model
    """
    # Initialize Model
    pipe = make_pipeline(TfidfVectorizer(), TruncatedSVD(dim))

    # Compute batch size, shouldn't load entire file into memory
    noBatches = sum([1 for line in open(file_path, "r")]) // batch_size

    topic_model = BERTopic(embedding_model=pipe, nr_topics=n_topics)

    count = 0

    for batch in batched_lines(file_path, batch_size):
        # do something with the batch of lines
        if verbose:
            print(f"Training on batch {count} of {noBatches}.")
        topic_model.fit(batch)
        count += 1

    return topic_model


def save_topic_model(topic_model, file_name, verbose=False):
    if verbose:
        print(f"Saving Model to {config.model_data_path}")
    path = os.path.join(config.model_data_path, file_name)
    topic_model.save(path)
    if verbose:
        print("Done.")
