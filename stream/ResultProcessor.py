import os
import json

def list_dir(dirPath):
    g = os.walk(dirPath)
    for path,dir_list,file_list in g:  
        for file_name in file_list:  
            yield os.path.join(path, file_name)

def get_order_file_list(dirPath):
    fl = [f for f in list_dir(dirPath)]
    fl.sort(key=lambda x:int(x.split('_')[-1].split('.')[0]))
    return fl

def merge_result(path, desName = 'merge.txt'):
    index = 0
    frame_ret_list = []
    for f in get_order_file_list(path):
        index+=1
        lines = open(f,'r').readlines()
        cls_map = {}
        for l in lines:
            cls = l[0]
            if cls not in cls_map:
                cls_map[cls] = 1
            else:
                cls_map[cls] += 1
        frame_ret_list.append(cls_map)
    des = os.path.join(os.path.dirname(path),desName)
    with open(des,'w') as f:
        j = json.dumps(frame_ret_list)
        f.write(j)
        f.flush()
    return des



if __name__ == '__main__':
    merge_result('D:\\MyProjects\\yolov5\\runs\\detect\\debug\\labels')