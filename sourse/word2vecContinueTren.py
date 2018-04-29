import gensim as gensim

model = gensim.models.Word2Vec.load('model')
argument = 'corpora.txt'
data = gensim.models.word2vec.LineSentence(argument)
model.build_vocab(data, update=True)
model.train(data, total_examples=model.corpus_count, epochs=model.epochs)
model.save('model2')
