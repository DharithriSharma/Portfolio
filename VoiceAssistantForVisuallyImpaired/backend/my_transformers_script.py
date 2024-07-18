#transformers
from transformers import pipeline

# Create a pipeline for question answering
qa_pipeline = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")


def answer_question(query, context):
    result = qa_pipeline(question=query, context=context)
    return result['answer']