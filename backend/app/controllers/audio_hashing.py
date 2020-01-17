'''
Contains function for hashing peak arrays
'''
from bson.objectid import ObjectId

ANCHOR_DISTANCE = 3
TARGET_ZONE_SIZE = 5

def hasher(peak, ultrasound_id):
    '''
    expects array
    '''
    # list to hold fingerprints
    fingerprints = []
    # list to hold candidate anchors
    candidateAnchors = []

    if len(peak) == 0:
        return fingerprints
    currentAbsoluteTime = peak[0][0]
    tempCandidateIndex = 0
    tempMaxAmp = 0
    for i in range(0, len(peak) - (ANCHOR_DISTANCE + TARGET_ZONE_SIZE)):
        anchor = peak[i] # a list
        if anchor[0] > currentAbsoluteTime:
            candidateAnchors.append(tempCandidateIndex)
            currentAbsoluteTime = anchor[0]
            tempMaxAmp = 0
        if anchor[2] > tempMaxAmp:
            tempCandidateIndex = i
            tempMaxAmp = anchor[2]
    for i in candidateAnchors:
        for j in range(i + ANCHOR_DISTANCE, i + ANCHOR_DISTANCE + TARGET_ZONE_SIZE):
            anchor = peak[i]
            point = peak[j]
            anchorFrequency = anchor[1]
            pointFrequency = point[1]
            delta = point[0] - anchor[0]
            absoluteTime = anchor[0]
            address = 'a{}p{}d{}'.format(anchorFrequency, pointFrequency, delta)
            couple = {
                'absoluteTime': absoluteTime,
                'ultrasound_id': ObjectId(ultrasound_id),
            }
            fingerprint = {
                'address': address,
                'couple': couple
            }
            fingerprints.append(fingerprint)
            # append fingerprint to fingerprints
    return fingerprints

# fingerprints = hasher(peaks)
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(fingerprints)