import json
import urllib.request
from datetime import date

MAX_ITEMS_API_QUERY = 50
Y_CRED = "AIzaSyAbPC02W3k-MFU7TmvYCSXfUPfH10jNB7g"
API_QUERY = 'https://www.googleapis.com/youtube/v3/playlists?part=snippet&maxResults={}&channelId={}&key={}&pageToken={}'

def get_playlists(channel_id="UCX9ok0rHnvnENLSK7jdnXxA", num_playlists=MAX_ITEMS_API_QUERY):
    """
    Get the playlists of a YouTube channel from the channel's id
    """
    api_key = None
    with open('credentials.txt', 'r', encoding='utf-8') as f:
        api_key = f.read()
    query_url = API_QUERY.format(
        num_playlists, channel_id, api_key, '')
    data = json.load(urllib.request.urlopen(query_url))
    
    total = data['pageInfo']['totalResults']
    zones = data['items']

    while len(zones) < total:
        next_page_token = data['nextPageToken']
        query_url = API_QUERY.format(
            num_playlists, channel_id, api_key, next_page_token
        )
        data = json.load(urllib.request.urlopen(query_url))
        new_zones = data['items']
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
        'previous_update': current_data['date'],
        'zones_total': len(current_zones),
        'new_zones': new_zones,
        'zones': current_zones
    }
    with open('zones.json', 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=4, ensure_ascii=False)
    return new_zones


if __name__ == "__main__":
    new_zones = update_zones()
    print("{} new zones".format(len(new_zones)))
    if new_zones:
        print(new_zones)