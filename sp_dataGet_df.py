import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import requests
import time
import ast
import pandas as pd
from typing import List

class spAPIget:
    def __init__(self, sp: spotipy.Spotify):
        self.sp = sp
    
    # artists

    # returns list of JSON
    def artist_by_playlist(self, pl_list: List[str]) -> dict:
        artists_list = []
        for playlist_url in pl_list:
            try:
                playlist_url = playlist_url.rsplit('/', 1)[-1] # everything after the final '/' is the uri/id
                playlist = sp.playlist(playlist_url)
                for track in playlist['tracks']['items']:
                    if track['track']['artists'][0]['name'] not in artists_list:
                        artists_list.append(track['track']['artists'][0]['name'])
                    else:
                        pass
            except spotipy.exceptions.SpotifyException as e:
                print(f'Spotify Exception: {e}')
                print(f'Bad link: {playlist_url}')
            except Exception as e:
                print(f'An error occurred: {e}')
        return(artists_list)
    
    # returns individual JSON
    def artist_by_name(self, artist_name: str) -> dict: 
        try:
            top_result = self.sp.search(q = 'artist:' + artist_name, type = 'artist')['artists']['items'][0]
            info_dict = {
                'Name': top_result['name'],
                'URI': top_result['uri'],
                'Popularity': top_result['popularity'],
                'Genres': top_result['genres'],
                'Followers': top_result['followers']['total']
                }
            return(info_dict)
        except Exception as e:
            print(f'An error occured: {e} for the artist: {artist_name}')
            return None
    
    # individual JSON
    def artist_by_uri(self, artist_uri: str) -> dict:
        try:
            response = sp.artist(artist_uri)
            info_dict = {'name': response['name'], 
                        'artist_uri': response['uri'], 
                        'popularity': response['popularity'], 
                        'genres': response['genres'], 
                        'followers': response['followers']['total']}
            return(info_dict)
        except Exception as e:
            print(f'An error occured: {e} for the artist: {artist_uri}')
            return None
    
    # Albums
    def album_by_uri(self, artist_uri: str) -> List[dict]:
        results = sp.artist_albums(artist_uri)
        all_albums = []
        try:
            for album in results['items']:
                all_albums.append({'name': album['name'],
                                'id': album['id'],
                                'album_uri': album['uri'],
                                'album_group': album['album_group'],
                                'album_type': album['album_type'],
                                'type': album['type'],
                                'artists': album['artists'],
                                'release_date': album['release_date'],
                                'release_date_precision': album['release_date_precision'],
                                'total_tracks': album['total_tracks'],
                                'external_urls': album['external_urls'],
                                'artist_name': [artist['name'] for artist in album['artists']],
                                'artist_uri_list': [artist['uri'] for artist in album['artists']]
                                })
            return(all_albums) # list of dictionaries
        except Exception as e:
            print(f"An error occured: {e} for the album: {album['name']}")
            return None
    
    # Tracks
    def tracks_from_album(self, curr_album_uri: str, curr_album_name: str) -> List[dict]:
        try:
            response = sp.album_tracks(curr_album_uri)['items']
            tracks_list = []
            for song in response:
                tracks_list.append({'name': song['name'],
                                    'album_name': curr_album_name,
                                    'album_uri': curr_album_uri,
                                    'artists': song['artists'],
                                    'track_uri': song['uri'],
                                    'id': song['id'],
                                    'disc_num': song['disc_number'],
                                    'song_num': song['track_number'],
                                    'type': song['type'], # probably not necessary
                                    'duration_ms': song['duration_ms'],
                                    'explicit': song['explicit'],
                                    'is_local': song['is_local'],
                                    'external_urls': song['external_urls'],
                                    'href': song['href']})
            return(tracks_list)
        except Exception as e:
            print(f"An error occured: {e}")
            return(None)
    
    # Audio features
    def get_audio_fts(self, range_start, range_end) -> List[dict]:
        try:
            audio_feats_to_add = []
            while range_start < range_end:
                audio_feats_to_add.extend(sp.audio_features(missing_track_uris.uri[range_start:range_start + 100]))
                range_start += 100
            return(audio_feats_to_add)
        except Exception as e:
            print(f"An error occurred: {e}")

class add_to_df:
    # used in conjunction with the results from the spAPIget functions

    def to_artist_info(self, data_add: List[dict], path: str):
        artist_info = pd.read_csv(path)
        data_add_df = pd.json_normalize(data_add)
        new_df = pd.concat([artist_info, data_add_df], ignore_index = True)

        for col in new_df.columns:
            if new_df[col].apply(lambda x: isinstance(x, list)).any():
                new_df[col] = new_df[col].apply(str)
        
        new_df = new_df.drop_duplicates(subset = ['URI'])
        new_df.to_csv(path, index = False)
        return()
    
    def to_albums(self, data_add: List[dict], path: str):
        album_df = pd.read_csv(path)
        data_add_df = pd.json_normalize(data_add)
        new_df = pd.concat([album_df, data_add_df], ignore_index = True)

        new_df[['artist_name', 'artist_uri']] = new_df[['artist_name', 'artist_uri']].apply(str)
        new_df = new_df.drop_duplicates(subset = 'uri')
        new_df[['artist_name', 'artist_uri']] = new_df[['artist_name', 'artist_uri']].apply(ast.literal_eval)

        new_df.to_csv(path, index = False)
        return()
    
def to_tracks(self, data_add: List[dict], path: str):
    album_tracks = pd.read_csv(path)
    data_add_df = pd.json_normalize(data_add)
    new_df = pd.concat([album_tracks, data_add_df], ignore_index = True)

    for col in new_df.columns:
        if new_df[col].apply(lambda x: isinstance(x, list)).any():
            new_df[col] = new_df[col].apply(str)

    new_df = new_df.drop_duplicates()        
    new_df.to_csv(path, index = False)
    return()

def to_audioFeats(self, data_add: List[dict], path1: str, path2: str):
    feat_df = pd.read_csv(path1)
    album_tracks = pd.read_csv(path2)
    data_add_df = pd.json_normalize(data_add)
    new_df = pd.concat([feat_df, data_add_df], ignore_index = True)
    
    # adding in artist, album data
    new_df = new_df.merge(album_tracks[['uri', 'name', 'album_name', 'album_uri', 'artists']], on='uri', how='left', suffixes = ('', '_new'))
    new_df.drop(columns = [
        'name', 'album_name', 'album_uri', 'artists', 'id', 'type', 'track_href', 'analysis_url'
        ], inplace = True)
    new_df.rename(columns = {
        'name_new': 'name',
        'album_name_new': 'album_name',
        'album_uri_new': 'album_uri',
        'artists_new': 'artists',
        'uri': 'track_uri'
        }, inplace = True)
    
    new_df.drop_duplicates(inplace = True)
    new_df.dropna(inplace = True)
    new_df.to_csv(path1, index = False)