from transformers import pipeline

def summarizing(text: str) -> str:
  pipe_summa = pipeline("summarization","traintogpb/pko-t5-large-kor-for-colloquial-summarization-finetuned")
  return pipe_summa(text)
