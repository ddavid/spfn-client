import json
import pickle
from itertools import chain


def flatten_list(iterable):
    return list(chain.from_iterable(iterable))

def dump_serialized_json_obj(json_obj, save_file=''):
    # Check if string is not empty
    if save_file:
        with open(save_file + '.json', 'w') as json_file:
            json_file.write(json_obj['pred_dict'])
            print('Saved Serialized JSON predictions to %s' % save_file)

        with open(save_file + '_pcl.json', 'w') as pcl_file:
            pcl_file.write(json.dumps(json_obj['point_cloud']))
            print('Saved Serialized PC to %s' % (save_file + '_pcl.json'))

    serialized_json_obj = pickle.dumps(json_obj)

    return serialized_json_obj