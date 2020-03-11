"""
Manages the matching of incoming audio files
"""

from app import app, mongo

USERS_COLLECTION = mongo.db.users
VIDEOS_COLLECTION = mongo.db.videos  # holds reference to user
ULTRASOUND_COLLECTION = mongo.db.ultrasound  # holds reference to video

# holds reference to links
US_FINGERPRINTS_COLLECTION = mongo.db.ultrasound_fingerprints
AU_FINGERPRINTS_COLLECTION = mongo.db.audible_fingerprints


def match(fingerprints, mode):
    """
    takes in array of fingerprints and mode
    returns (string ultrasound_id, int max_delta_count
    """
    target_zone_map = {}  # { (string ultrasound_id, int absolute_time): [int delta] }

    time_coherency_map = {}  # { string ultrasound_id: { int delta: int count } }

    match_dict = {}

    if mode == 'ultrasound':
        FINGERPRINTS_COLLECTION = US_FINGERPRINTS_COLLECTION
    else:
        FINGERPRINTS_COLLECTION = AU_FINGERPRINTS_COLLECTION

    for fingerprint in fingerprints:
        # print('looking for address: {}'.format(fingerprint['address']))

        db_fingerprint = FINGERPRINTS_COLLECTION.find_one(
            {"address": fingerprint["address"]}
        )
        # db_fingerprint = FINGERPRINTS_COLLECTION.find_one({'address': 'a1858p1885d2'})
        if db_fingerprint:
            db_couples = db_fingerprint["couple"]
            for db_couple in db_couples:
                ultrasound_id = db_couple["ultrasound_id"]
                absolute_time = int(db_couple["absolute_time"])
                delta = int(fingerprint["absolute_time"] - absolute_time)
                couple = (ultrasound_id, absolute_time)  # holds ints
                if couple not in target_zone_map.keys():
                    target_zone_map[couple] = [delta]
                else:
                    target_zone_map[couple].append(delta)

    for couple, delta_list in target_zone_map.items():
        if len(delta_list) >= 4:
            for delta in delta_list:
                ultrasound_id = couple[0]
                if ultrasound_id not in time_coherency_map.keys():
                    # if ultrasound_id has not been entered in timeCoherencyMap,
                    time_coherency_map[ultrasound_id] = {delta: 1}
                    # init the vale to dict with delta count = 1
                else:
                    # if ultrasound_id already in timeCoherencyMap,
                    if delta not in time_coherency_map[ultrasound_id].keys():
                        # check if delta exists in timeCoherencyMap[ultrasound_id]
                        time_coherency_map[ultrasound_id][delta] = 1
                    else:
                        time_coherency_map[ultrasound_id][delta] += 1

    for ultrasound_id, delta_count_dict in time_coherency_map.items():
        current_max_delta_count = 0
        for delta, count in delta_count_dict.items():
            current_max_delta_count = max(current_max_delta_count, count)
        if ultrasound_id not in match_dict.keys():
            # TODO: is this needed? shld only be iterating over each ultrasound_id once
            match_dict[ultrasound_id] = current_max_delta_count
        else:
            match_dict[ultrasound_id] += current_max_delta_count

    temp_max = 0
    temp_result = None

    # print('time_coherency_map: {}'.format(time_coherency_map))
    # print('target_zone_map: {}'.format(target_zone_map))
    # print('match_dict: {}'.format(match_dict))

    for ultrasound_id, max_delta_count in match_dict.items():
        if max_delta_count > temp_max:
            temp_max = max_delta_count
            temp_result = ultrasound_id

    if temp_result:
        result = temp_result, temp_max
    else:
        result = None, None
    return result
