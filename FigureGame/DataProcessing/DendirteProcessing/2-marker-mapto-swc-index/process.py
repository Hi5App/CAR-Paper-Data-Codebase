# delete trash image -v
# eswc -> swc -v
# replace new swc into swc folder -v
# map marker to swc index and change type
# later in game: change swc bp points with type
import glob
import math
import os
import sys

class swcnode:
    def __init__(self,id,type,x,y,z,r,pid):
        self.id = id
        self.type = type
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.pid = pid

    def changeType(self,t):
        self.type = t

class marker:
    def __init__(self,x,y,z,r,g,b):
        self.x = x
        self.y = y
        self.z = z
        self.color = self.getColor(r,g,b)

    def getColor(self,a, b, c):
        color = (a, b, c)
        if color == (255, 38, 0) or color == (255, 0, 0):
            return 1  # red
        elif color == (0, 253, 255) or color == (0, 255, 255):
            return 2  # cyan
        elif color == (255, 147, 0) or color == (255, 85, 0):
            return 3  # orange
        else:
            print(f"ERROR unrecognized color scheme:{color}")
            raise ValueError("color not found")
            return 4

    def distance_to(self,x,y,z):
        return math.sqrt((self.x-x)**2 + (self.y-y)**2 + (self.z-z)**2)

def checkForConsistency(imageFolder,swcFolder) -> bool:
    images = list(map(lambda x:os.path.basename(x),glob.glob(imageFolder+"/*.v3draw")))
    swcs = list(map(lambda x:os.path.basename(x),glob.glob(swcFolder+"/*.swc")))
    if len(images) != len(swcs):
        return False
    image_names = set([os.path.splitext(image)[0] for image in images])
    swc_names = set([os.path.splitext(swc)[0][:-11] for swc in swcs])
    if image_names == swc_names:
        return True
    else:
        return False

def buildNameDic(path):
    # take third as key
    files = glob.glob(path)
    files.sort()
    d = dict()
    for file in files:
        swc_name = os.path.basename(file)
        swc_words = swc_name.split("_")
        x_coord = float(swc_words[2])
        d[x_coord] = file
    return d

def renameSWC():
    src = "./newDendriteData/newswc"
    dst = "./newDendriteData/dendriteSWC"
    dst_dic = buildNameDic(path=dst)
    dst_array = list(dst_dic.items())
    files = glob.glob(src+"/*.eswc")
    files.sort()
    for file in files:
        filename = os.path.basename(file)[:-5]
        if len(filename) > 10:
            continue
        if "." in filename:
            key = float(filename)
            new_path = dst_dic[key]
            new_name = os.path.basename(new_path)[:-4]+".eswc"
            os.rename(file,src+"/"+new_name)
        else:
            for name in dst_array:
                index = str(name[0])
                if index.split(".")[0] == filename:
                    os.rename(file,src+"/"+os.path.basename(name[1][:-4]+".eswc"))

def getMarkerFromFile(path):
    markers = []
    with open(path) as f:
        lines = f.readlines()
        for line in lines:
            if line[0] == "#":
                continue
            words = line.split(",")
            x = float(words[0])
            y = float(words[1])
            z = float(words[2])
            b = int(words[-1])
            g = int(words[-2])
            r = int(words[-3])
            m = marker(x,y,z,r,g,b)
            markers.append(m)
    return markers

def getNodeFromFile(path):
    nodes = []
    with open(path) as f:
        lines = f.readlines()
        for line in lines:
            if line[0] == "#":
                continue
            words = line.split(" ")
            id = int(words[0])
            type = int(words[1])
            x = float(words[2])
            y = float(words[3])
            z = float(words[4])
            r = float(words[5])
            pid = int(words[6])
            n = swcnode(id,type,x,y,z,r,pid)
            nodes.append(n)
    return nodes

def getBpIndexFromFile(path):
    nodes = getNodeFromFile(path)
    child_count_dict = dict()
    BpIndexes = []
    for node in nodes:
        if node.pid not in child_count_dict:
            child_count_dict[node.pid] = 1
        else:
            child_count_dict[node.pid] += 1
    for key in child_count_dict:
        if child_count_dict[key] == 2:
            BpIndexes.append(key)
    return BpIndexes


def changeSWCNodeType(path,id,type):
    with open(path,"r+") as f:
        lines = f.readlines()
        for i in range(len(lines)):
            words = lines[i].split(" ")
            if words[0] == str(id):
                words[1] = str(type)
                lines[i] = " ".join(words)
                break

        f.seek(0)
        f.writelines(lines)
        f.truncate()

def filterBP(nodes):
    children_dict = dict()
    for node in nodes:
        if node.pid not in children_dict:
            children_dict[node.pid] = 1
        else:
            children_dict[node.pid] += 1

    bp_id_set = set()
    for key in children_dict:
        if children_dict[key] == 2:
            bp_id_set.add(key)
    # exclude soma
    if 1 in bp_id_set:
        bp_id_set.remove(1)
    return list(filter(lambda x:x.id in bp_id_set,nodes))

def mapMarker(swcD,markerD):
    for key in swcD:
        swcFile = swcD[key]
        markerFile = markerD[key]
        nodes = getNodeFromFile(swcFile)
        BPnodes = filterBP(nodes)
        # nodes_dict =
        markers = getMarkerFromFile(markerFile)
        # min_distance = sys.maxsize
        # min_index = -1
        with open("mapLog.txt", "a") as f:
            log = f"swc:{swcFile},marker:{markerFile}\n"
            f.write(log)
        for marker in markers:
            min_distance = sys.maxsize
            min_index = -1
            min_posi = (0,0,0)
            use_nodes = nodes if marker.color == 3 else BPnodes # cyan and red find in bp, orange find in all nodes
            for node in use_nodes:
                distance = marker.distance_to(node.x,node.y,node.z)
                if distance < min_distance:
                    min_distance = distance
                    min_index = node.id
                    min_posi = (node.x,node.y,node.z)
            type = -1
            if marker.color == 1: # red 正确分叉点
                type = 100001
            elif marker.color == 2: # cyan 忽略的分叉点
                type = 100002
            elif marker.color == 3: # orange missing点
                type = 100003
            changeSWCNodeType(swcFile,min_index,type)
            with open("mapLog.txt","a") as f:
                log = f"marker:{(marker.x,marker.y,marker.z)} map to swcnode:{(min_index,min_posi[0],min_posi[1],min_posi[2])} Distance:{min_distance:.2f}\n"
                f.write(log)
            for node in nodes: #remove node to avoid one marker map to more than one node
                if node.id == min_index:
                    nodes.remove(node)
                    # print("delete node: "+str(min_index))
                    break
            for node in BPnodes:
                if node.id == min_index:
                    BPnodes.remove(node)
                    # print("delete bp node: " + str(min_index))
                    break


if __name__ == "__main__":
    image_path ="./newDendriteData/dendriteImageRaw"
    swc_path ="./newDendriteData/dendriteSWC"
    if checkForConsistency(image_path,swc_path):
        print("image and swc is consistent")
    swcDict = buildNameDic("./newDendriteData/dendriteSWC/*.swc")
    # swcDict = buildNameDic("./newDendriteData/testSWC/*.swc")
    markerDict= buildNameDic("./newDendriteData/gsmarker/*.marker")
    # markerDict= buildNameDic("./newDendriteData/testMarker/*.marker")
    k1 = set(swcDict.keys())
    k2 = set(markerDict.keys())
    if len(swcDict) != len(markerDict) or k1 != k2:
        overlap = k1.intersection(k2)
        swc_remain = k1.difference(k2)
        marker_remain = k2.difference(k1)
        print("swc number does not match marker number")
        exit()
    if os.path.exists("mapLog.txt"):
        os.remove("mapLog.txt")
    mapMarker(swcDict,markerDict)
    print("Finished Map")
    # print(swcDict)
    # renameSWC()