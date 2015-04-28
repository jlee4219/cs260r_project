import theano
from pylearn2.models import mlp
from pylearn2.training_algorithms import sgd
from pylearn2.termination_criteria import EpochCounter
from pylearn2.datasets.dense_design_matrix import DenseDesignMatrix
from csv_data import CSVData
import numpy as np

class MLPData(DenseDesignMatrix):
  def __init__(self, X, y):
    super(MLPData, self).__init__(X=X, y=y.astype(int), y_labels=2)

threshold = 0.95
hidden_layer = mlp.Sigmoid(layer_name='h0', dim=10, sparse_init=10)
output_layer = mlp.Softmax(layer_name='y', n_classes=2, irange=0.05)
layers = [hidden_layer, output_layer]
neural_net = mlp.MLP(layers, nvis=10)
trainer = sgd.SGD(batch_size=5, learning_rate=.1, termination_criterion=EpochCounter(100))
        
first = True
learning = True
correct = 0
incorrect = 0
total = 0
data = CSVData("results2.csv")
while True:
  X, y = data.get_data()
  if(X == None):
    break

  if learning:
    ds = MLPData(X, np.array([[0]]))
    if first:
      trainer.setup(neural_net, ds)
      first = False
    prediction = np.argmax(neural_net.fprop(theano.shared(X, name='X')).eval())
    print prediction
    if prediction == 0:
      correct += 1
    total += 1
    if correct / float(total) >= threshold:
      print "Verifying"
      learning = False
      total = 0
      correct = 0
    else:
      while True:
        trainer.train(dataset=ds)
        neural_net.monitor.report_epoch()
        neural_net.monitor
        if not trainer.continue_learning(neural_net):
          break

  else:
    prediction = np.argmax(neural_net.fprop(theano.shared(X, name='X')).eval())
    print prediction
    if prediction != y:
      incorrect += 1
    total += 1

    if incorrect / float(total) >= 1 - threshold:
      print "Learning"
      learning = True
      total = 0
      incorrect = 0