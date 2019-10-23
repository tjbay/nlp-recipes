# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import collections
from torch.utils.data import Dataset


class SCDataSet(Dataset):
    def __init__(self, df, text_col, label_col):
        self.df = df

        if isinstance(text_col, int):
            self.text_col = text_col
        elif isinstance(text_col, str):
            self.text_col = df.columns.index(text_col)
        else:
            raise TypeError("text_col must be of type int or str")

        if isinstance(label_col, int):
            self.label_col = label_col
        elif isinstance(label_col, str):
            self.label_col = df.columns.index(label_col)
        else:
            raise TypeError("label_col must be of type int or str")

    def __getitem__(self, idx):
        return (self.df.iloc[idx, self.text_col], self.df.iloc[idx, self.label_col])

    def __len__(self):
        return self.df.shape[0]


# QAInput is a data structure representing an unique document-question-answer triplet.
# Args:
#    doc_text (str): Input document text.
#    question_text(str): Input question text.
#    qa_id (int or str): An unique id identifying a document-question-answer sample.
#    is_impossible (bool): If the question is impossible to answer based on the input document.
#    answer_start (int or list): Index of the answer start word in doc_text. For testing data,
#        this can be a list of integers for multiple ground truth answers.
#    answer_text (str or list): Text of the answer. For testing data, this can be a list of strings
#        for multiple ground truth answers.
QAInput = collections.namedtuple(
    "QAInput",
    ["doc_text", "question_text", "qa_id", "is_impossible", "answer_start", "answer_text"],
)


class QADataset(Dataset):
    def __init__(
        self,
        df,
        doc_text_col,
        question_text_col,
        qa_id_col=None,
        answer_start_col=None,
        answer_text_col=None,
        is_impossible_col=None,
    ):
        """
        A standard dataset structure for question answering that can be processed by
        :meth:`utils_nlp.models.transformers.question_answering.QAProcessor.preprocess`

        Args:
            df (pandas.DataFrame): Input data frame.
            doc_text_col (str): Name of the column containing the document texts.
            question_text_col (str): Name of the column containing the question texts.
            qa_id_col (str, optional): Name of the column containing the unique ids identifying
                document-question-answer samples. If not provided, a "qa_id" column is
                automatically created. Defaults to None.
            answer_start_col (str, optional): Name of the column containing answer start indices.
                For testing data, each value in the column can be a list of integers for multiple
                ground truth answers. Defaults to None.
            answer_text_col (str, optional): Name of the column containing answer texts. For
                testing data, each value in the column can be a list of strings for multiple
                ground truth answers. Defaults to None.
            is_impossible_col (str, optional): Name of the column containing boolean values
                indicating if the question is impossible to answer. If not provided,
                a "is_impossible" column is automatically created and populated with False.
                Defaults to None.
        """
        self.df = df.copy()
        self.doc_text_col = doc_text_col
        self.question_text_col = question_text_col

        if qa_id_col is None:
            self.qa_id_col = "qa_id"
            self.df[self.qa_id_col] = list(range(self.df.shape[0]))
        else:
            self.qa_id_col = qa_id_col

        if is_impossible_col is None:
            self.is_impossible_col = "is_impossible"
            self.df[self.is_impossible_col] = False
        else:
            self.is_impossible_col = is_impossible_col

        if answer_start_col is not None and answer_text_col is not None:
            self.actual_answer_available = True
        else:
            self.actual_answer_available = False
        self.answer_start_col = answer_start_col
        self.answer_text_col = answer_text_col

    def __getitem__(self, idx):
        current_item = self.df.iloc[idx,]
        if self.actual_answer_available:
            return QAInput(
                doc_text=current_item[self.doc_text_col],
                question_text=current_item[self.question_text_col],
                qa_id=current_item[self.qa_id_col],
                is_impossible=current_item[self.is_impossible_col],
                answer_start=current_item[self.answer_start_col],
                answer_text=current_item[self.answer_text_col],
            )
        else:
            return QAInput(
                doc_text=current_item[self.doc_text_col],
                question_text=current_item[self.question_text_col],
                qa_id=current_item[self.qa_id_col],
                is_impossible=current_item[self.is_impossible_col],
                answer_start=-1,
                answer_text="",
            )

    def __len__(self):
        return self.df.shape[0]
