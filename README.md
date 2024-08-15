# Spotify Recommendation System
Using data from Spotify's API to create a recommender primarily using the data from the 'audio features' data.

# Models
## Batch Cosine Similarity with PCA Reduction
* Use PCA reduction on the 'genre' feature to drastically lower overall feature count
* Generate cosine similarity matrices on batches of size n (currently n = 15000), selecting the top 1000 results, generate another cosine similarity matrix on the aggregated results
* Using the result matrix, function will return the top (however much the user input) results

## PySpark, EMR, Dimension Independent Matrix Square (DIMSUM) - Deprecated
Stored in separate respository: https://github.com/GuhGonk/KaggleSpotify6K

Utilized cloud computing tools (AWS EC2, S3, EMR) and Databricks to leverage PySpark's cluster computing. 

No longer in use due to maintenance costs.

Process:
* TF-IDF vectorization hashing (genres, playlists, categorical, confidence measures/music attributes)
* VectorAssembler to create 1 large overarching feature vector
* Pipeline, fit, transform model
* RDD for PySpark
* Compute similarity matrix with DIMSUM
