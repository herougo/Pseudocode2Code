NEW_TAG = '########### NEW TEST CASE SET ###########'
INPUT_TAG =  '########### INPUT ###########'
OUTPUT_TAG =  '########### OUTPUT ###########'
TAGS = [NEW_TAG, INPUT_TAG, OUTPUT_TAG]
BLOCK = '\n'.join([NEW_TAG, '', INPUT_TAG, '', OUTPUT_TAG, ''])

if __name__ == "__main__":
    # generate empty test file
    print('\n'.join([BLOCK] * 100))