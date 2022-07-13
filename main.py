import json
import os
import urllib.request
from datetime import date

MAX_ITEMS_API_QUERY = 50
Y_CRED = "AIzaSyAbPC02W3k-MFU7TmvYCSXfUPfH10jNB7g"
SNIPPET = 'snippet'
CONTENT_DETAILS = 'contentDetails'
API_QUERY = 'https://www.googleapis.com/youtube/v3/playlists?part={}&maxResults={}&channelId={}&key={}&pageToken={}'
PLAYLIST_API_QUERY = 'https://www.googleapis.com/youtube/v3/playlists?part={}&key={}&id={}'


def get_playlists(channel_id="UCX9ok0rHnvnENLSK7jdnXxA",
                  num_playlists=MAX_ITEMS_API_QUERY):
    """
    Get all the playlists of a YouTube channel from the channel's id
    """
    api_key = None
    with open('credentials.txt', 'r', encoding='utf-8') as f:
        api_key = f.read()
    query_url = API_QUERY.format(SNIPPET, num_playlists, channel_id, api_key,
                                 '')
    # Get the total number of playlists in the channel
    data = json.load(urllib.request.urlopen(query_url))
    total = data['pageInfo']['totalResults']
    zones = data['items']

    while len(zones) < total:
        # while len(zones) < total:
        next_page_token = data['nextPageToken']
        query_url = API_QUERY.format(','.join([SNIPPET, CONTENT_DETAILS]),
                                     num_playlists, channel_id, api_key,
                                     next_page_token)
        data = json.load(urllib.request.urlopen(query_url))
        new_zones = data['items']
        zones += new_zones

    for zone in zones:
        if not zone.get(CONTENT_DETAILS, {}).get('itemCount', ''):
            # Make a specific API query for this list
            query_url = PLAYLIST_API_QUERY.format(
                ','.join([SNIPPET, CONTENT_DETAILS]), api_key, zone.get('id'))
            zone_data = json.load(urllib.request.urlopen(query_url))
            zone[CONTENT_DETAILS] = zone_data['items'][0][CONTENT_DETAILS]

    return {
        i.get(SNIPPET, {}).get('title', 'Unknown'):
        i.get(CONTENT_DETAILS, {}).get('itemCount', -1)
        for i in zones
    }


def update_zones():
    """
    Retrieve the current list of playlists, compare it with the previous
    one and detect which ones have been added since the last update 
    """
    today = date.today()
    # dd-mm-yyyy
    current_date = today.strftime("%d-%m-%Y")
    with open('zones.json', 'r', encoding='utf-8') as f:
        current_data = json.load(f)
    # get new zones and sectors
    last_zone_update = current_data['zones']
    current_zones = get_playlists()
    new_zones = {
        key: val
        for key, val in current_zones.items()
        if key not in last_zone_update.keys()
    }
    # new_zones = [zone for zone in current_zones if zone not in last_zone_update]
    # check which ones are not included yet
    # not_included = list_not_added(current_zones, get_all_included_zones_and_sectors())
    # prepare new data
    previous_update = current_data['date']
    # if more than one update is being made on the same day, do not update previous_date
    if current_date == current_data['date']:
        previous_update = current_data['previous_update']

    increased_videos = {
        key: val
        for key, val in current_zones.items()
        if has_number_of_videos_changed(key, val, current_zones)
    }

    to_be_listed = zones_to_be_listed(current_zones)

    updated_data = {
        'date': current_date,
        'previous_update': previous_update,
        'zones_total': len(current_zones),
        'new_zones': new_zones,
        'increased_videos': increased_videos,
        'missing_zones': update_zones_to_list(to_be_listed),
        'zones_that_should_be_listed': to_be_listed,
        'zones': current_zones
        # 'not_included': not_included
    }
    with open('zones.json', 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=4, ensure_ascii=False)

    return new_zones


def zones_to_be_listed(current_zones, threshold=6):
    return {
        key: val
        for key, val in current_zones.items()
        if val >= threshold and 'sector' not in key.lower() and ':' not in key.lower()
    }


def has_number_of_videos_changed(zone_title, video_count, current_zones):
    """
    Returns True if the number of videos in the playlist 
    has increased since the last update
    """
    if current_zones.get(zone_title, -1) > video_count:
        return True
    return False


def get_all_included_zones_and_sectors(rel_path='../BetaLibrary/'):
    """
    Get the list of sectors and zones included in the web
    """
    # walk all data
    areas = next(os.walk(rel_path + 'data/zones/'))[1]
    listed = []
    for area in areas:
        # Load data zone map
        datafile = rel_path + 'data/zones/' + area + '/' + area + '.txt'
        area_data = {}
        with open(datafile, encoding='utf-8') as data:
            area_data = json.load(data)
        listed += [area_data['name']]
        listed += [
            area_data['name'] + ': ' + sector['name']
            for sector in area_data['sectors']
        ]
    return listed


def list_not_added(current_zones, included_zones):
    """
    List the sectors and zones that have a playlist but haven't been 
    added to the web yet.
    """
    return list(set(current_zones) - set(included_zones))

def update_zones_to_list(to_be_listed):
    # read zones that should be listed from zones.json
    # read zones from zones_included.json
    # write the difference
    zones_to_be_listed = set(to_be_listed)
    zones_listed = None
    with open('zones_included.json', 'r', encoding='utf-8') as f:
        zone_data = json.load(f)
        zones_listed = set(zone_data.get('zones', []))
    
    return list(zones_to_be_listed - zones_listed)

if __name__ == "__main__":
    new_zones = update_zones()
    print("{} new zones".format(len(new_zones)))
    if new_zones:
        print([key for key, _ in new_zones.items()])
