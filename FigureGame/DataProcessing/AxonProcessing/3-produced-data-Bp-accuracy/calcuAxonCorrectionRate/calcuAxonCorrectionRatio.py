import pandas as pd

from process import getNodeFromFile,getBpIndexFromFile
from mapMissingPoints import distance_3d

def str2ints(s):
    if s == 'set()':
        return []
    if s == '{}':
        return []
    s1 = s[1:-1]
    return [int(i[1:-1]) for i in s.strip('{}').split(', ')]

def getBpPositions(path):
    nodes = getNodeFromFile(path)
    bpIndexes = getBpIndexFromFile(path)
    result = []
    for node in nodes:
        if node.id in bpIndexes:
            result.append((node.x,node.y,node.z))
    return result

def isBpValid(gsBpPosition,testPosition,threshold=5):
    for posi in gsBpPosition:
        if distance_3d(posi,testPosition) < threshold:
            return True
    return False

def getPosiUsingIndexes(indexes,swcPath):
    nodes = getNodeFromFile(swcPath)
    result = []
    for node in nodes:
        if node.id in indexes:
            result.append((node.x,node.y,node.z))
    if len(result) != len(indexes):
        raise ValueError('indexes and results not match')
    return result

'''
gsSWC: a list of 3d positions of gs bp points
testSWC:
original: a list of 3d position of bp points
predicted: two list of right and wrong bp points

calculate method:
true correct + true wrong / original sum
'''
def calculateCorrectionRatio():
    df = pd.read_csv('axonPredictResult.csv')
    accuracy = []
    for i,row in df.iterrows():
        swcName = row['SwcId']
        gsPath = 'sortedAxonSwc/' + swcName + '.swc'
        autoPath = 'ServerSWCFiles/' + swcName + '.swc'
        gsBp = getBpPositions(gsPath)
        autoBp = getBpPositions(autoPath)
        # calculate auto accuracy first
        # true correct / sum
        count = 0
        for bp in autoBp:
            if isBpValid(gsBp,bp):
                count += 1
        autoAccuracy = count/len(autoBp)
        # calculate predict accuracy
        trueCorrect = 0
        trueWrong = 0
        CorrectBp = str2ints(row['CorrectBP'])
        CorrectBpPositions = getPosiUsingIndexes(CorrectBp,autoPath)
        WrongBp = str2ints(row['WrongBP'])
        WrongBpPositions = getPosiUsingIndexes(WrongBp,autoPath)
        for p in CorrectBpPositions:
            if isBpValid(gsBp,p):
                trueCorrect += 1
        for p in WrongBpPositions:
            if not isBpValid(gsBp,p):
                trueWrong += 1
        predictAccuracy = (trueCorrect+trueWrong)/(len(CorrectBp)+len(WrongBp))
        accuracy.append({'swcName':swcName,'auto':round(autoAccuracy,4),'auto+CAR':round(predictAccuracy,4)})
    accuracyDF = pd.DataFrame(accuracy)
    accuracyDF.to_csv('axonAccuracy.csv')


if __name__ == '__main__':
    calculateCorrectionRatio()
