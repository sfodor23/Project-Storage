from bertopic import BERTopic
import pandas as pd

Dataframe = pd.read_csv("ProcessedData.csv", nrows=70000)

Dataframe = Dataframe[Dataframe["Class"] == "suicide"]

if "Text" not in Dataframe.columns:
	raise ValueError("ProcessedData.csv must contain a 'Text' column.")

Documents = (
	Dataframe["Text"]
	.dropna()
	.astype(str)
	.str.strip()
)

Documents = Documents[Documents != ""].tolist()

if not Documents:
	raise ValueError("No valid text rows found in 'Text' after cleaning.")

TopicModel = BERTopic(embedding_model="all-MiniLM-L6-v2")

Topics, Probs = TopicModel.fit_transform(Documents)

Figure = TopicModel.visualize_topics()
Figure.write_html("topics.html")
print("Saved interactive topic visualization to topics.html")



