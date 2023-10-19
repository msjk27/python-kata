from transformers import pipeline

def sentiment_analysing(text):
  pipe_translation_ko_en = pipeline("translation", model="circulus/kobart-trans-ko-en-v2")
  dic = pipe_translation_ko_en(text ,max_length=1000)
  translated = dic[0]["translation_text"]
  pipe_senti = pipeline("sentiment-analysis")
  return pipe_senti(translated)
