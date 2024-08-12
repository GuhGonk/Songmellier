import pandas as pd
import numpy as np
import ast
import textwrap
import time
from rapidfuzz import process, utils, fuzz

from sklearn.preprocessing import MinMaxScaler, MultiLabelBinarizer
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from joblib import Parallel, delayed

class feat_eng:
# These functions are usually used on dataframe columns with .apply()/.apply(lambda x: func(x))
    def extract_artist_uris(self, artist_raw):
        try:
            artist_liteval = ast.literal_eval(artist_raw)
            artist_list = [artist['uri'] for artist in artist_liteval]
            return(artist_list)
        except Exception as e:
            print(f'An error occurred: {e}')
    
    def extract_artist_name(artist_raw):
        if isinstance(artist_raw, str):
            artist_liteval = ast.literal_eval(artist_raw)
        else:
            artist_liteval = ast.literal_eval(artist_raw.item())

        artist_list = [artist['name'] for artist in artist_liteval]
        return(artist_list)

    def get_genres(uri_list, artist_df):
        try:
            all_genres = []
            for artist in uri_list:
                genre_series = artist_df['genres'].loc[artist_df['artist_uri'] == artist]
                for genre in genre_series:
                    all_genres.extend(genre)
            return(all_genres)
        except Exception as e:
            print(f'An error occurred: {e}')

    def mmScaler(df): # used with feat_df
        min_max_scaler = MinMaxScaler()
        audio_vecs = min_max_scaler.fit_transform(df[['loudness', 'tempo']]) 
        instr_vecs = min_max_scaler.fit_transform(df[['speechiness', 'acousticness', 'instrumentalness']])

        df[['loudness_scaled', 'tempo_scaled']] = audio_vecs
        df[['speechiness_scaled', 'acousticness_scaled', 'instrumentalness_scaled']] = instr_vecs
        return(df)
    
    def genre_ft(df):
        mlb = MultiLabelBinarizer()
        genre_vectors = mlb.fit_transform(df['genres'])
        genre_df = pd.DataFrame(genre_vectors, columns = mlb.classes_)
        genre_feat = pd.concat([df.uri, genre_df], axis = 1)
        genre_feat = genre_feat.set_index('uri')
        return(genre_feat)
    
class model_work:
    def pca_reduce_genre(df, n_comp):
        # start_time = time.time()

        pca = PCA(n_components = n_comp)
        genre_feat_PCA = pd.DataFrame(pca.fit_transform(df), index = df.index)

        # print("pca_reduce_genre: --- %s seconds ---" % (time.time() - start_time))
        return(genre_feat_PCA)
    
    def batch_cosine_genre(df, uri):
        all_start_time = time.time()
    
        uri_slice = df.loc[df.index == uri]
        df_other = df.loc[~(df.index == uri)]
        
        top_res = []
        
        batch_size = 15000
        num_batches = len(df_other) // batch_size + (1 if len(df_other) % batch_size != 0 else 0)
        
        for i in range(num_batches):
            # start_time = time.time()

            start = i * batch_size
            end = start + batch_size
            batch = df_other[start:end]
            batch = pd.concat([batch, uri_slice])
            
            batch_cs = cosine_similarity(batch)
            batch_cs_df = pd.DataFrame(batch_cs, index = batch.index)
            index_pos = batch_cs_df.index.get_loc(uri_slice.index[0])
            batch_sim_scores = batch_cs_df.iloc[:, index_pos]
            batch_top_1000 = batch_sim_scores.nlargest(1000).index
            top_res.append(batch_top_1000)

            # print(f"Batch {i} time: --- %s seconds ---" % (time.time() - start_time))
            # time.sleep(0.1)
        
        # Length of top_res is not actually (num_batches * 1000) because there are duplicated values of the uri_slice in each batch
        #  so (num_batches * 1000) - (num_batches)
        top_res_list = [item for sublist in top_res for item in sublist]
        # top_res_select = df_other[df_other.index.isin(top_res_list)]

        # print("batch_cosine_genre: --- %s seconds ---" % (time.time() - all_start_time))
        return(top_res_list)
    
    # Goes back to the feature dataframe and performs cosine
    def get_rec(df, tracks_df, uri, uri_list, top_n):
        start_time = time.time()
        
        df_select = df[df.uri.isin(uri_list)]
        df_select = df_select.set_index('uri')
        # df_select = df_select.drop(columns = ['genres', 'vibe_vector']) # ad hoc

        if len(uri_list) < 15000:
            cs_res = cosine_similarity(df_select)
            cs_res = pd.DataFrame(cs_res, index = df_select.index)
            recs_raw =  cs_res[cs_res.index.get_loc(uri)].nlargest(top_n).index.to_list()
            
            target_slice = tracks_df[tracks_df.uri == uri]
            recs_df = tracks_df[tracks_df.uri.isin(recs_raw)]
            
            print(textwrap.dedent(f"""
            -------- Original Song --------
            Song: {target_slice.name.item()}
            Album: {target_slice.album_name.item()} 
            Artist(s): {extract_artist_name(target_slice.artists)}
            -------------------------------
            """))
            
            for i in range(top_n):
                if (recs_df.index[i] == target_slice.index):
                    pass
                else:
                    print(textwrap.dedent(f"""
                    -------- Recommendation {i + 1} --------
                    Song: {recs_df.iloc[i]['name']}
                    Album: {recs_df.iloc[i]['album_name']}
                    Artist(s): {extract_artist_name(recs_df.iloc[i].artists)}
                    ----------------------------------
                    """))
    #     else:
    #         uri_slice = df_select.loc[df_select.index == uri]
    #         df_other = df_select.loc[~(df_select.index == uri)]
            
    #         batch_size = 15000
    #         num_batches = len(df_other) // batch_size + (1 if len(df_other) % batch_size != 0 else 0)
        
    #         for i in range(num_batches):
    #             # start_time = time.time()
    #             start = i * batch_size
    #             end = start + batch_size
    #             batch = df_other[start:end]
    #             batch = pd.concat([batch, uri_slice])
                
    #             batch_cs = cosine_similarity(batch)
    #             batch_cs = cosine_similarity(batch)
    #             batch_cs_df = pd.DataFrame(batch_cs, index = batch.index)
    #             index_pos = batch_cs_df.index.get_loc(uri_slice.index[0])
    #             batch_sim_scores = batch_cs_df.iloc[:, index_pos]
        print("get_rec: --- %s seconds ---" % (time.time() - start_time))           
        return(recs_df)

    def y_n_handler():
        user_resp = input("Please input 'yes' or 'no': ")

        while True:
            if user_resp in ['yes', 'no']:
                return user_resp
            else:
                user_resp = input("Please input 'yes' or 'no': ")
            

    def uri_lookup(df):
        song_name = input("Enter the song name: ")
        artist = input("Enter the artist name: ")
        
        df['song_artist_key'] = df.apply(lambda row: f"{row['name']} - {row['artists_clean'][0]}", axis=1)
        df['matching_ratio'] = df.apply(lambda x: fuzz.ratio(x.song_artist_key, song_name + '-' + artist), axis=1).to_list()
        df = df.sort_values('matching_ratio', ascending = False)
        
        for i in range(len(df)):
            print(textwrap.dedent(f"""
            Is this the song you were looking for?
                Song: {df.iloc[i]['name']}
                Album: {df.iloc[i]['album_name']}
                Artists: {df.iloc[i]['artists_clean']}
            """))
            
            resp = y_n_handler()
            if resp == 'no':
                continue
            elif resp == 'yes':
                # print('Hooray!')
                return(df.iloc[i]['uri'])
            

    def full_model():
        # Load in data
        feat_df = pd.read_csv('data/feat_df.csv')
        artist_df = pd.read_csv('data/artist_info.csv')
        album_tracks = pd.read_csv('data/album_tracks.csv')
        album_df = pd.read_csv('data/album_info.csv')

        
        target_uri = uri_lookup(album_tracks)
        genre_feat = pca_reduce_genre(genre_feat, 500)
        reduced_feats = batch_cosine_genre(genre_feat)
        