"""
Contains function for hashing peak arrays
"""
from bson.objectid import ObjectId

ANCHOR_DISTANCE = 3
TARGET_ZONE_SIZE = 5


def hasher(peak, ultrasound_id=None):
    """
    expects array

    if ultrasound_id is specified:
        the fingeprint is being generated from a link.
        couples will be added to the fingeprint
    if ultrasound_id is not specified (None):
        the fingepeirnt is being generated from listening audio.
        only absolute_time will be added to the fingerprint.
    """
    # list to hold fingerprints
    fingerprints = []
    # list to hold candidate anchors
    candidate_anchors = []

    if len(peak) == 0:
        return fingerprints
    current_absolute_time = peak[0][0]
    temp_candidate_index = 0
    temp_max_amp = 0
    for i in range(0, len(peak) - (ANCHOR_DISTANCE + TARGET_ZONE_SIZE)):
        anchor = peak[i]  # a list
        if anchor[0] > current_absolute_time:
            candidate_anchors.append(temp_candidate_index)
            current_absolute_time = anchor[0]
            temp_max_amp = 0
        if anchor[2] > temp_max_amp:
            temp_candidate_index = i
            temp_max_amp = anchor[2]
    for i in candidate_anchors:
        point_zone_start = i + ANCHOR_DISTANCE
        point_zone_end = point_zone_start + TARGET_ZONE_SIZE
        for j in range(point_zone_start, point_zone_end):
            anchor = peak[i]
            point = peak[j] # anchor, but a set distance awa y
            anchor_frequency = anchor[1]
            pointfrequency = point[1]
            delta = point[0] - anchor[0]
            absolute_time = anchor[0]
            address = "a{}p{}d{}".format(anchor_frequency, pointfrequency, delta)
            couple = {
                "absolute_time": absolute_time,
                "ultrasound_id": ObjectId(ultrasound_id),
            }
            if ultrasound_id:
                fingerprint = {"address": address, "couple": couple}
            else:
                fingerprint = {"address": address, "absolute_time": absolute_time}
            fingerprints.append(fingerprint)
            # append fingerprint to fingerprints
    return fingerprints


# fingerprints = hasher(peaks)
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(fingerprints)
