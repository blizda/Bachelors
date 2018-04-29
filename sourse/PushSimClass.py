import gensim
from MongoDataWorker import MongoDataPuller, MongoSimClassPush
import numpy as np
from sklearn.cluster import AffinityPropagation
from sklearn.preprocessing import StandardScaler

def parseDocs(document):
    cleanDict = {}
    for it in document['tf_idf']:
        if ' ' in it:
            splitWords = it.split()
            for w in splitWords:
                cleanDict[w] = 1
        else:
           cleanDict[it] = 1
    return cleanDict

def calcVectors(wordDict, model):
    finalVector = np.zeros(300, dtype=np.float32)
    sucses = 0
    loseArray = []
    for it in wordDict.keys():
        if it in model.wv.vocab:
            finalVector = finalVector + (model[it] * wordDict[it])
            sucses += 1
        else:
            loseArray.append(it)
    return np.divide(finalVector, sucses), {'TokensInModel' : sucses, 'TokensOutOfModel': len(loseArray)}

def testCalck(dockList, model):
    resultDict = {}
    modelInfDic = {}
    idDict = {}
    for it in dockList:
        serName = it['serial_name']
        idDict[it['serial_name']] = it['_id']
        parsDict = parseDocs(it)
        resultDict[serName], modelInfDic[serName] = calcVectors(parsDict, model)
    return resultDict, modelInfDic, idDict


def clustersJSONoneN(data, info, idInf, conn, mw2):
    arr = []
    arrList = []
    for it in data:
        arr.append(data[it])
        arrList.append(it)
    scaler = StandardScaler()
    reashapeArr = np.array(arr).reshape(len(data.keys()), 300)
    scaler.fit(reashapeArr)
    scaled = scaler.transform(reashapeArr)
    aff = AffinityPropagation(max_iter=1200, convergence_iter=50)
    labels = aff.fit_predict(scaled)
    print(data.keys())
    print(labels)
    for i in range(len(arrList)):
        print(arrList[i] + ' ' + str(idInf[arrList[i]]) + ' ' + labels[i])
        mw2.updateSerial(conn, arrList[i], idInf[arrList[i]], labels[i])

model = gensim.models.Word2Vec.load('')
mw = MongoDataPuller('')
mw2 = MongoSimClassPush('')
con = mw.makeConnection()
con2 = mw2.makeConnection()
res, info, idInf = testCalck(mw.findSerial(con), model)
clustersJSONoneN(res, info, idInf, con2, mw2)