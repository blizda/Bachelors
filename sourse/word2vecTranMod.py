import gensim as gensim

argument = 'corpora.txt'
data = gensim.models.word2vec.LineSentence(argument)
model = gensim.models.Word2Vec(data, size=300, window=7, min_count=1, sg=1)
model.save('model')