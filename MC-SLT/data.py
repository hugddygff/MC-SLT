# coding: utf-8
"""
Data module
"""
import os
import sys
import random

import torch
from torchtext import data
from torchtext.data import Dataset, Iterator
import socket
from signjoey.dataset import SignTranslationDataset, SignTranslationDataset_signer
from signjoey.vocabulary import (
    build_vocab,
    Vocabulary,
    UNK_TOKEN,
    EOS_TOKEN,
    BOS_TOKEN,
    PAD_TOKEN,
)

from IPython import embed


def load_data(data_cfg: dict) -> (Dataset, Dataset, Dataset, Vocabulary, Vocabulary):
    """
    Load train, dev and optionally test data as specified in configuration.
    Vocabularies are created from the training set with a limit of `voc_limit`
    tokens and a minimum token frequency of `voc_min_freq`
    (specified in the configuration dictionary).

    The training data is filtered to include sentences up to `max_sent_length`
    on source and target side.

    If you set ``random_train_subset``, a random selection of this size is used
    from the training set instead of the full training set.

    If you set ``random_dev_subset``, a random selection of this size is used
    from the dev development instead of the full development set.

    :param data_cfg: configuration dictionary for data
        ("data" part of configuration file)
    :return:
        - train_data: training dataset
        - dev_data: development dataset
        - test_data: test dataset if given, otherwise None
        - gls_vocab: gloss vocabulary extracted from training data
        - txt_vocab: spoken text vocabulary extracted from training data
    """

    data_path = data_cfg.get("data_path", "./data")

    if isinstance(data_cfg["train"], list):
        train_paths = [os.path.join(data_path, x) for x in data_cfg["train"]]
        dev_paths = [os.path.join(data_path, x) for x in data_cfg["dev"]]
        test_paths = [os.path.join(data_path, x) for x in data_cfg["test"]]
        pad_feature_size = sum(data_cfg["feature_size"])

    else:
        train_paths = os.path.join(data_path, data_cfg["train"])
        dev_paths = os.path.join(data_path, data_cfg["dev"])
        test_paths = os.path.join(data_path, data_cfg["test"])
        pad_feature_size = data_cfg["feature_size"]

    level = data_cfg["level"]
    txt_lowercase = data_cfg["txt_lowercase"]
    max_sent_length = data_cfg["max_sent_length"]

    def tokenize_text(text):
        if level == "char":
            return list(text)
        else:
            return text.split()

    def tokenize_features(features):
        ft_list = torch.split(features, 1, dim=0)
        return [ft.squeeze() for ft in ft_list]

    # NOTE (Cihan): The something was necessary to match the function signature.
    def stack_features(features, something):
        return torch.stack([torch.stack(ft, dim=0) for ft in features], dim=0)

    sequence_field = data.RawField()
    signer_field = data.RawField()

    sgn_field = data.Field(
        use_vocab=False,
        init_token=None,
        dtype=torch.float32,
        preprocessing=tokenize_features,
        tokenize=lambda features: features,  # TODO (Cihan): is this necessary?
        batch_first=True,
        include_lengths=True,
        postprocessing=stack_features,
        pad_token=torch.zeros((pad_feature_size,)),
    )

    gls_field = data.Field(
        pad_token=PAD_TOKEN,
        tokenize=tokenize_text,
        batch_first=True,
        lower=False,
        include_lengths=True,
    )

    txt_field = data.Field(
        init_token=BOS_TOKEN,
        eos_token=EOS_TOKEN,
        pad_token=PAD_TOKEN,
        tokenize=tokenize_text,
        unk_token=UNK_TOKEN,
        batch_first=True,
        lower=txt_lowercase,
        include_lengths=True,
    )

    pos_field = data.Field(
        init_token=BOS_TOKEN,
        eos_token=EOS_TOKEN,
        pad_token=PAD_TOKEN,
        tokenize=tokenize_text,
        unk_token=UNK_TOKEN,
        batch_first=True,
        lower=False,
        include_lengths=True,
    )



    full_path = [train_paths, dev_paths, test_paths]

    source_support = "/home/jintao/slt-master-dg/data/PHOENIX2014T/ph.support.source"
    source_query = "/home/jintao/slt-master-dg/data/PHOENIX2014T/ph.query.source"


    dev_set = "/home/jintao/slt-master-dg/data/PHOENIX2014T/ph.query.target"

    source_support = "/home/jintao/data/CSL-daily/csl_i3d_pre.support.source"
    source_query = "/home/jintao/data/CSL-daily/csl_i3d_pre.query.source"
    dev_set = "/home/jintao/data/CSL-daily/csl_i3d_pre.query.target"

    train_data = SignTranslationDataset(
        path=dev_set,
        fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
        filter_pred=lambda x: len(vars(x)["sgn"]) <= max_sent_length
        and len(vars(x)["txt"]) <= max_sent_length,
    )

    s1_data = SignTranslationDataset_signer(
        path=source_support,
        #person="Signer01",
        person="0",
        fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
        filter_pred=lambda x: len(vars(x)["sgn"]) <= max_sent_length
                              and len(vars(x)["txt"]) <= max_sent_length,
    )

    s2_data = SignTranslationDataset_signer(
        path=source_support,
        #person="Signer04",
        person="8",
        fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
        filter_pred=lambda x: len(vars(x)["sgn"]) <= max_sent_length
                              and len(vars(x)["txt"]) <= max_sent_length,
    )

    s3_data = SignTranslationDataset_signer(
        path=source_support,
        #person="Signer05",
        person="3",
        fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
        filter_pred=lambda x: len(vars(x)["sgn"]) <= max_sent_length
                              and len(vars(x)["txt"]) <= max_sent_length,
    )

    s4_data = SignTranslationDataset_signer(
        path=source_support,
        #person="Signer08",
        person="9",
        fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
        filter_pred=lambda x: len(vars(x)["sgn"]) <= max_sent_length
                              and len(vars(x)["txt"]) <= max_sent_length,
    )

    s5_data = SignTranslationDataset_signer(
        path=source_query,
        #person="Signer01",
        person="0",
        fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
        filter_pred=lambda x: len(vars(x)["sgn"]) <= max_sent_length
                              and len(vars(x)["txt"]) <= max_sent_length,
    )


    s6_data = SignTranslationDataset_signer(
        path=source_query,
        #person="Signer04",
        person="8",
        fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
        filter_pred=lambda x: len(vars(x)["sgn"]) <= max_sent_length
                              and len(vars(x)["txt"]) <= max_sent_length,
    )

    s7_data = SignTranslationDataset_signer(
        path=source_query,
        #person="Signer05",
        person="3",
        fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
        filter_pred=lambda x: len(vars(x)["sgn"]) <= max_sent_length
                              and len(vars(x)["txt"]) <= max_sent_length,
    )

    s8_data = SignTranslationDataset_signer(
        path=source_query,
        #person="Signer08",
        person="9",
        fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
        filter_pred=lambda x: len(vars(x)["sgn"]) <= max_sent_length
                              and len(vars(x)["txt"]) <= max_sent_length,
    )



    #s5_data = SignTranslationDataset_signer(
    #    path=full_path,
    #    person="Signer05",
    #    fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
    #    filter_pred=lambda x: len(vars(x)["sgn"]) <= max_sent_length
    #                          and len(vars(x)["txt"]) <= max_sent_length,
    #)

    #s7_data = SignTranslationDataset_signer(
    #    path=full_path,
    #    person="Signer07",
    #    fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
    #    filter_pred=lambda x: len(vars(x)["sgn"]) <= max_sent_length
    #                          and len(vars(x)["txt"]) <= max_sent_length,
    #)

    #s8_data = SignTranslationDataset_signer(
    #    path=full_path,
    #   person="Signer08",
    #    fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
    #    filter_pred=lambda x: len(vars(x)["sgn"]) <= max_sent_length
    #                          and len(vars(x)["txt"]) <= max_sent_length,
    #)

    #s9_data = SignTranslationDataset_signer(
    #    path=full_path,
    #    person="Signer09",
    #    fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
    #    filter_pred=lambda x: len(vars(x)["sgn"]) <= max_sent_length
    #                          and len(vars(x)["txt"]) <= max_sent_length,
    #)



    #embed()

    gls_max_size = data_cfg.get("gls_voc_limit", sys.maxsize)
    gls_min_freq = data_cfg.get("gls_voc_min_freq", 1)
    txt_max_size = data_cfg.get("txt_voc_limit", sys.maxsize)
    txt_min_freq = data_cfg.get("txt_voc_min_freq", 1)

    gls_vocab_file = data_cfg.get("gls_vocab", None)
    txt_vocab_file = data_cfg.get("txt_vocab", None)
    pos_vocab_file = data_cfg.get("pos_vocab", None)

    gls_vocab = build_vocab(
        field="gls",
        min_freq=gls_min_freq,
        max_size=gls_max_size,
        dataset=train_data,
        vocab_file=gls_vocab_file,
    )
    txt_vocab = build_vocab(
        field="txt",
        min_freq=txt_min_freq,
        max_size=txt_max_size,
        dataset=train_data,
        vocab_file=txt_vocab_file,
    )

    pos_vocab = build_vocab(
        field="pos",
        min_freq=0,
        max_size=10000,
        dataset=train_data,
        vocab_file=pos_vocab_file,
    )

    #embed()




    random_train_subset = data_cfg.get("random_train_subset", -1)
    if random_train_subset > -1:
        # select this many training examples randomly and discard the rest
        keep_ratio = random_train_subset / len(train_data)
        keep, _ = train_data.split(
            split_ratio=[keep_ratio, 1 - keep_ratio], random_state=random.getstate()
        )
        train_data = keep

    #dev_data = SignTranslationDataset(
    #    path=full_path,
    #    fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
    #)

    dev_data = train_data


    random_dev_subset = data_cfg.get("random_dev_subset", -1)
    if random_dev_subset > -1:
        # select this many development examples randomly and discard the rest
        keep_ratio = random_dev_subset / len(dev_data)
        keep, _ = dev_data.split(
            split_ratio=[keep_ratio, 1 - keep_ratio], random_state=random.getstate()
        )
        dev_data = keep

    # check if target exists
    #test_data = SignTranslationDataset(
    #    path=full_path,
    #    fields=(sequence_field, signer_field, sgn_field, gls_field, txt_field, pos_field),
    #)

    test_data = train_data

    gls_field.vocab = gls_vocab
    txt_field.vocab = txt_vocab
    pos_field.vocab = pos_vocab


    return train_data, dev_data, test_data, gls_vocab, txt_vocab, pos_vocab, s1_data, s2_data, s3_data, s4_data, s5_data, s6_data, s7_data, s8_data


# TODO (Cihan): I don't like this use of globals.
#  Need to find a more elegant solution for this it at some point.
# pylint: disable=global-at-module-level
global max_sgn_in_batch, max_gls_in_batch, max_txt_in_batch


# pylint: disable=unused-argument,global-variable-undefined
def token_batch_size_fn(new, count, sofar):
    """Compute batch size based on number of tokens (+padding)"""
    global max_sgn_in_batch, max_gls_in_batch, max_txt_in_batch
    if count == 1:
        max_sgn_in_batch = 0
        max_gls_in_batch = 0
        max_txt_in_batch = 0
    max_sgn_in_batch = max(max_sgn_in_batch, len(new.sgn))
    max_gls_in_batch = max(max_gls_in_batch, len(new.gls))
    max_txt_in_batch = max(max_txt_in_batch, len(new.txt) + 2)
    sgn_elements = count * max_sgn_in_batch
    gls_elements = count * max_gls_in_batch
    txt_elements = count * max_txt_in_batch
    return max(sgn_elements, gls_elements, txt_elements)


def make_data_iter(
    dataset: Dataset,
    batch_size: int,
    batch_type: str = "sentence",
    train: bool = False,
    shuffle: bool = False,
) -> Iterator:
    """
    Returns a torchtext iterator for a torchtext dataset.

    :param dataset: torchtext dataset containing sgn and optionally txt
    :param batch_size: size of the batches the iterator prepares
    :param batch_type: measure batch size by sentence count or by token count
    :param train: whether it's training time, when turned off,
        bucketing, sorting within batches and shuffling is disabled
    :param shuffle: whether to shuffle the data before each epoch
        (no effect if set to True for testing)
    :return: torchtext iterator
    """


    #embed()

    batch_size_fn = token_batch_size_fn if batch_type == "token" else None

    if train:
        # optionally shuffle and sort during training
        data_iter = data.BucketIterator(
            repeat=False,
            sort=False,
            dataset=dataset,
            batch_size=batch_size,
            batch_size_fn=batch_size_fn,
            train=True,
            sort_within_batch=True,
            sort_key=lambda x: len(x.sgn),
            shuffle=shuffle,
        )
    else:
        # don't sort/shuffle for validation/inference
        data_iter = data.BucketIterator(
            repeat=False,
            dataset=dataset,
            batch_size=batch_size,
            batch_size_fn=batch_size_fn,
            train=False,
            sort=False,)

    #for bat in iter(data_iter
    #                ):
    #    embed()
    #    print (bat.txt)
    return data_iter
