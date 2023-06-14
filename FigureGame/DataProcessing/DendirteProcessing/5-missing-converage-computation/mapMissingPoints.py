import glob
import math
import sys

import numpy
import pandas as pd
from process import swcnode,getNodeFromFile
from clusteringMissingPoints import index_str_to_ints

def mapMissingPoints(path,threshold=20):
    df = pd.read_csv(path)
    # df = df[df['MissedBP'].notnull()]
    # df = df[df['SWCId'].str.len() > 20]
    log = []
    for i,row in df.iterrows():
        swcId = row["SWCId"]

        if len(swcId) < 20:
            continue
        if pd.isna(row["MissedBP"]):
            continue
        swcName = swcId + ".swc"
        swc_nodes = getNodeFromFile(f"./newDendriteData/dendriteSWC/{swcName}")
        ids = index_str_to_ints(row["MissedBP"])
        id_position_dict = dict()
        missing_points_dict = dict()
        for node in swc_nodes:
            if node.id in ids:
                id_position_dict[node.id] = (node.x,node.y,node.z)
        for node in swc_nodes:
            if node.type == 100003:
                missing_points_dict[node.id] = (node.x,node.y,node.z)
        mapped_id_set = []
        if swcId == "Img_X_5064.29_Y_9801.94_Z_3097.92.swc_sorted":
            print("1")
        for id in id_position_dict:
            min_index = -2
            min_distance = sys.maxsize
            for missP in missing_points_dict: # find nearest missing point
                d = distance_3d(id_position_dict[id],missing_points_dict[missP])
                if d < min_distance:
                    min_index = missP
                    min_distance = d
            if min_distance < threshold: # if in threshold, add mapped missing point
                mapped_id_set.append(min_index)
            else:
                mapped_id_set.append(id) # if not, add original point as false point
        newMissingData = ",".join([str(i) for i in mapped_id_set])
        log.append(row["SWCId"] + " " + row["MissedBP"] + "changed to " + newMissingData + "\n")
        df.at[i,'MissedBP'] = newMissingData
    df.to_csv('./newGameData/fakedata_missingMapped.csv',index=False)
    with open("log.txt","w") as f:
        f.writelines(log)


def distance_3d(start,end):
    dis_x = start[0] - end[0]
    dis_y = start[1] - end[1]
    dis_z = start[2] - end[2]
    return math.sqrt(dis_x**2 + dis_y**2 + dis_z**2)


def id2Position(swcName,id):

    for node in swc_nodes:
        if node.id == id:
            return (node.x,node.y,node.z)
    else:
        raise ValueError("no matching id found in swc name")

if __name__ == "__main__":
    mapMissingPoints("./newGameData/fakedata.csv")