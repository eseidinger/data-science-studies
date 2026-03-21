from langchain.document_loaders import DuckDBLoader
from langchain.document_loaders.csv_loader import CSVLoader

loader = CSVLoader(file_path='./tv-reviews.csv')
data = loader.load()

print(data)

loader = DuckDBLoader("SELECT * FROM read_csv_auto('tv-reviews.csv')",
                        page_content_columns=["Review Title", "Review Text"],
                        metadata_columns=["TV Name", "Review Rating"])
data = loader.load()

print(data)
