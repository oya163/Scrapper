'''
    JSON extractor
    
    Collects texts from all JSON files
    
    Date: 04/20/2020
    
    How to run:
        python extractor.py ./content
'''

import os
import sys
import json
from pathlib import Path

def main():
    # Go through all folders
    paths = [str(x) for x in Path(sys.argv[1]).glob("**/*.json")]
    ext = '.txt'
    
    # Create similar filename
    # Save into same directory
    for each in paths:
        base_dir = os.path.dirname(each)
        fname = os.path.basename(each).split('.')[0]
        output_file = os.path.join(base_dir, fname+ext)
        f = open(output_file, 'w')
        data = json.load(open(each))
        print("Length of data : {}".format(len(data['category'])))
        for items, value in data['category'].items():
            f.write(value['text']+"\n\n")
        print("File written : {}".format(f.name))
        f.close()
        

if __name__ == '__main__':
    main()
