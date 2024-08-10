# Spotify Recommendation System
Using data from Spotify's API to create a recommender primarily using the data from 'audio features' 

# Models
## Batch Cosine Similarity with PCA Reduction
Use PCA reduction on the 'genre' feature to drastically lower overall feature count. Then, generate cosine similarity matrices on batches of size n (currently n = 15000), selecting the top 1000 results, generate another cosine similarity matrix on the aggregated results. Using the result matrix, function will return the top (however much the user input) results.

