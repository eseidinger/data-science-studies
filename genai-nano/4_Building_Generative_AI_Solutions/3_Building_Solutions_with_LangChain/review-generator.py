from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

import os

os.environ["OPENAI_API_KEY"] = "YOUR API KEY"
os.environ["OPENAI_API_BASE"] = "https://openai.vocareum.com/v1"

model_name = "gpt-3.5-turbo"
temperature = 0.0
llm = OpenAI(model_name=model_name, temperature=temperature, max_tokens = 4000)

data_gen_template="""
generate csv formatted reviews for two different imaginary TVs. come up with a name for each one. 
for each tv, generate {num_reviews} reviews, with random number of positive and negatives reviews. 
each review will have these fields in the csv: tv name, review title, review rating (1-10), review text
be creative in your reviews, amaze us, csv format is a must.  
"""
data_gen_prompt = PromptTemplate.from_template(data_gen_template)

print(llm(data_gen_prompt.format(num_reviews = 10)))