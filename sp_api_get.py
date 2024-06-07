class sp_api_get:
    def artist_by_playlist(self, pl_list: array):
        try:
            for playlist_url in pl_list:
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

    def by_artist_name(self, name):
