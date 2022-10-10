# CS425-project

### Dataset Setup
#### Movies Dataset
* Download Movies dataset from ```https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset?resource=download```
* Move dataset into project directory
* ```mkdir datasets```
* ```mv ./archive ./datasets/movies```

#### Movies Wiki Dataset
* Download Movies Wiki dataset from ``````

### Architecture
* chatbot <- dialog_flow, qna_chatbot
* dialog_flow <- recommender, profile_generator
* recommender <- movies_data
* profile_generator <- movies_data
* qna_chatbot <- wiki_data
