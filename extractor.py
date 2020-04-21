'''
    JSON extractor
    
    Collects texts from all JSON files
    
    Date: 04/20/2020
    
    How to run:
        python extractor.py ./content ./corpus
'''

import os
import sys
import json
from pathlib import Path

def main():
    # Go through all folders
    paths = [str(x) for x in Path(sys.argv[1]).glob("**/*.json")]
    output_dir = sys.argv[2]
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    ext = '.txt'
    
    # One huge file
    final_file = open(os.path.join(output_dir, "final_file.txt"), 'w')
    
    # Create similar filename
    # Save into same directory
    for each in paths:
        base_dir = os.path.dirname(each)
        base_dir = os.path.join(output_dir, base_dir)
        
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        fname = os.path.basename(each).split('.')[0]
        
        output_file = os.path.join(base_dir, fname+ext)
        f = open(output_file, 'w')
        data = json.load(open(each))
        
        print("Length of data : {}".format(len(data['category'])))
        for items, value in data['category'].items():
            f.write(value['text']+"\n\n")
            final_file.write(value['text']+"\n\n")
        print("File written : {}".format(f.name))
        
        f.close()
        
    final_file.close()
        

if __name__ == '__main__':
    main()
