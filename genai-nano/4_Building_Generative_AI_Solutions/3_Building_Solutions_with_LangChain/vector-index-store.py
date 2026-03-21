from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders.csv_loader import CSVLoader

loader = CSVLoader(file_path='./tv-reviews.csv')

index = VectorstoreIndexCreator().from_loaders([loader])

query = "Based on the reviews in the context, tell me what people liked about the picture quality"
index.query(query)