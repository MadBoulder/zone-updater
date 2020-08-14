import json
import urllib.request
from datetime import date

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
    
def update_zones():
    today = date.today()
    # dd-mm-yyyy
    current_date = today.strftime("%d-%m-%Y")
    with open('zones.json', 'r', encoding='utf-8') as f:
        current_data = json.load(f)
    # get new zones and sectors
    last_zone_update = current_data['zones']
    current_zones = get_playlists()
    new_zones = [zone for zone in current_zones if zone not in last_zone_update]
    # prepare new data
    updated_data = {
        'date': current_date,
        'zones': current_zones,
        'new_zones': new_zones,
        'previous_update': current_data['date']
    }
    with open('zones.json', 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=4, ensure_ascii=False, sort_keys=True)
    return new_zones


if __name__ == "__main__":
    update_zones()
