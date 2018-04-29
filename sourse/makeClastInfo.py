import datetime
from collections import Counter
import gensim
import matplotlib
from scipy.cluster.hierarchy import linkage, cophenet, dendrogram, fcluster
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from MongoDataWorker import MongoDataPuller
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, AffinityPropagation
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn import metrics
import json

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

def fancy_dendrogram(*args, **kwargs):
    max_d = kwargs.pop('max_d', None)
    if max_d and 'color_threshold' not in kwargs:
        kwargs['color_threshold'] = max_d
    annotate_above = kwargs.pop('annotate_above', 0)

    ddata = dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        plt.title('Hierarchical Clustering Dendrogram (truncated)')
        plt.xlabel('sample index or (cluster size)')
        plt.ylabel('distance')
        for i, d, c in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list']):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            if y > annotate_above:
                plt.plot(x, y, 'o', c=c)
                plt.annotate("%.3g" % y, (x, y), xytext=(0, -5),
                             textcoords='offset points',
                             va='top', ha='center')
        if max_d:
            plt.axhline(y=max_d, c='k')
    return ddata

def testCalck(dockList, model):
    resultDict = {}
    modelInfDic = {}
    for it in dockList:
        serName = it['serial_name']
        parsDict = parseDocs(it)
        resultDict[serName], modelInfDic[serName] = calcVectors(parsDict, model)
    return resultDict, modelInfDic

def makeJSONDict(jsonData, keysList, clusters, algorithm, scaling,
                NClusters, SilhouetteCoefficient, CalinskiHarabazIndex, info, addInf=None):
    newData = {}
    newData['Algorithm'] = algorithm
    newData['Clusters'] = NClusters
    newData['Scaling'] = scaling
    newData['SilhouetteCoefficient'] = str(SilhouetteCoefficient)
    newData['CalinskiHarabazIndex'] = str(CalinskiHarabazIndex)
    clustersData = {}
    infoAboutData = {}
    for i in range(len(keysList)):
        clustersData[str(keysList[i])] = int(str(clusters[i]))
        infoAboutData[str(keysList[i])] = info[str(keysList[i])]
    newData['Data'] = clustersData
    newData['WordInfo'] = infoAboutData
    newData['addetedInf'] = addInf
    jsonData[str(datetime.datetime.today())] = newData
    return jsonData

def clustersJDenda(data, info):
    arr = []
    for it in data:
        arr.append(data[it])
    scaler = StandardScaler()
    reashapeArr = np.array(arr).reshape(len(data.keys()), 300)
    scaler.fit(reashapeArr)
    scaled = scaler.transform(reashapeArr)
    jsonData = {}
    Z = linkage(scaled, 'ward')
    plt.figure(figsize=(25, 10))
    plt.title('Hierarchical Clustering Dendrogram (truncated)')
    plt.xlabel('sample index or (cluster size)')
    plt.ylabel('distance')
    max_d = 20
    fancy_dendrogram(
        Z,
        truncate_mode='lastp',  # show only the last p merged clusters
        p=35,  # show only the last p merged clusters
        leaf_rotation=90.,
        leaf_font_size=12.,
        show_contracted=True,  # to get a distribution impression in truncated branches
        max_d=max_d,

    )
    plt.savefig('dendroPic/justDendroW6M3Mod100Cut20.png')
    labels = fcluster(Z, max_d, criterion='distance')
    scoreSilhouette = metrics.silhouette_score(scaled, labels, metric='euclidean')
    scoreCalinski = metrics.calinski_harabaz_score(scaled, labels)
    jsonData = makeJSONDict(jsonData, list(data.keys()), labels, 'Dendra',
                                'StandardScaler', None, scoreSilhouette, scoreCalinski, info)
    with open("results/justDendroW6M3Mod100Cut20.json", "w", encoding="utf-8") as file:
        json.dump(jsonData, file)

def clustersJSONoneN(data, info):
    arr = []
    for it in data:
        arr.append(data[it])
    scaler = StandardScaler()
    reashapeArr = np.array(arr).reshape(len(data.keys()), 300)
    scaler.fit(reashapeArr)
    scaled = scaler.transform(reashapeArr)
    jsonData = {}
    aff = AffinityPropagation()
    labels = aff.fit_predict(scaled)
    scoreSilhouette = metrics.silhouette_score(scaled, labels, metric='euclidean')
    scoreCalinski = metrics.calinski_harabaz_score(scaled, labels)
    jsonData = makeJSONDict(jsonData, list(data.keys()), labels, 'AffinityPropagation',
                                'StandardScaler', None, scoreSilhouette, scoreCalinski, info)
    print(data.keys())
    print(labels)
    with open("naffwith66serModandStandSc.json", "w", encoding="utf-8") as file:
        json.dump(jsonData, file)


def calckClastersDBSCAN(d, eps, info):
    dbascan = DBSCAN(eps)
    arr = []
    for it in d:
        arr.append(d[it])
    reashapeArr = np.array(arr).reshape(len(d.keys()), 300)
    scaled = reashapeArr
    clusters = dbascan.fit_predict(scaled)
    jsonData = {}
    scoreSilhouette = None
    scoreCalinski = None
    if len(Counter(clusters)) > 1:
        scoreSilhouette = metrics.silhouette_score(scaled, clusters, metric='euclidean')
        scoreCalinski = metrics.calinski_harabaz_score(scaled, clusters)
    jsonData = makeJSONDict(jsonData, list(d.keys()), clusters, 'DBSCAN',
                            'No', None, scoreSilhouette, scoreCalinski, info)
    print(d.keys())
    print(clusters)
    with open("results/DBSCANW6M3WithootSkale" + str(eps)  + ".json", "w", encoding="utf-8") as file:
        json.dump(jsonData, file)


model = gensim.models.Word2Vec.load('models/model100Serwind6min3')
mw = MongoDataPuller('myTesterWriter', 'USS137QQar', 'test_ser_it_2', '185.40.31.63')
con = mw.makeConnection()
res, info = testCalck(mw.findSerial(con), model)