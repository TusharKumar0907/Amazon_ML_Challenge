import os
import random
import pandas as pd
from pk2 import MLmodel
def predictor(image_link, category_id, entity_name):
    '''
    Call your model/approach here
    '''
    # image_link ="https://m.media-amazon.com/images/I/812FE4kIZ8L.jpg"
    return MLmodel(image_link, entity_name)
    # return "1800 gram"
    

if __name__ == "__main__":
    DATASET_FOLDER = 'dataset/'
    
    test = pd.read_csv(os.path.join(DATASET_FOLDER, 'test.csv'))
    
    test['prediction'] = test.apply(
        lambda row: predictor(row['image_link'], row['group_id'], row['entity_name']), axis=1)
    
    output_filename = os.path.join(DATASET_FOLDER, 'test_out.csv')
    test[['index', 'prediction']].to_csv(output_filename, index=False)