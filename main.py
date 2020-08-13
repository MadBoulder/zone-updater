import json
import urllib.request

MAX_ITEMS_API_QUERY = 50
Y_CRED = "AIzaSyAbPC02W3k-MFU7TmvYCSXfUPfH10jNB7g"


def get_playlists(channel_id="UCX9ok0rHnvnENLSK7jdnXxA", num_playlists=MAX_ITEMS_API_QUERY):
    """
    Get the playlists of a YouTube channel from the channel's id
    """
    api_key = None
    with open('credentials.txt', 'r', encoding='utf-8') as f:
        api_key = f.read()
    query_url = 'https://www.googleapis.com/youtube/v3/playlists?part=snippet&maxResults={}&channelId={}&key={}'.format(
        num_playlists, channel_id, api_key)
    inp = urllib.request.urlopen(query_url)
    data = json.load(inp)
    
    total = data['pageInfo']['totalResults']
    zones = data['items']
    retrieved = len(zones)

    while retrieved < total:
        next_page_token = data['nextPageToken']
        query_url = 'https://www.googleapis.com/youtube/v3/playlists?part=snippet&maxResults={}&channelId={}&key={}&pageToken={}'.format(
            num_playlists, channel_id, api_key, next_page_token
        )
        inp = urllib.request.urlopen(query_url)
        data = json.load(inp)
        new_zones = data['items']
        retrieved += len(new_zones)
        zones += new_zones
        
    return [i['snippet']['title'] for i in zones]

if __name__ == "__main__":
    print(get_playlists())