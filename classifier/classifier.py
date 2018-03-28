import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from matplotlib import pyplot as plt
import cv2 as cv
import pickle as pkl
import gzip

f = gzip.open("fetr1.txt.gz")

a = np.ndarray([55*62, 50*50])
b = np.ndarray([55*62], dtype=int)
for i, lin in enumerate(f):
    lin = lin.strip().split()
    b[i] = lin[0]
    for j in range(2500):
        a[i][j] = lin[1+j]
# Split the dataset into test and training set
xtr, xte, ytr, yte = train_test_split(a, b, test_size=.05)
# Scaling the dataset to managable size
s = StandardScaler()
s.fit(xtr)
xtrn = s.transform(xtr)
xten = s.transform(xte)
# Encoding the probabilites to the corresponding character
lab = LabelEncoder()
l = map(chr, list(range(ord('0'), ord('9')+1))+list(range(ord('A'), ord('Z')+1))+list(range(ord('a'), ord('z')+1)))
lab.fit(l)
len(lab.classes_)
# Defining the classifier and training
mlp = MLPClassifier(solver='lbfgs', max_iter=1000, hidden_layer_sizes=(100))
mlp.fit(xtrn, ytr)
pkl.dump((mlp, s, lab), open('classifier.bin', 'wb'))
# Testing for presicting accuracy ~ 73%
sorted(mlp.predict_proba(xten)[0])
np.sum(mlp.predict(xten)==yte)/float(len(yte))
np.sum(mlp.predict(xtrn)==ytr), len(ytr)

for i, j in zip(mlp.predict(xten), yte):
    print lab.inverse_transform(int(i)), lab.inverse_transform(j)

lab.inverse_transform(mlp.predict(s.transform(cv.resize(255-cv.imread('p.png', 0), (50, 50)).reshape(1,2500))))

for i,j in enumerate(mlp.predict_proba(s.transform(cv.resize(255-cv.imread('p.png', 0), (50, 50)).reshape(1,2500)))[0]):
    print lab.inverse_transform(i), j

for i,j in enumerate(mlp.predict_proba(xten)[0]):
    print lab.inverse_transform(i), j

data = np.zeros([50, 50])
n = 3
xte[0][1000]
for i in range(50):
    for j in range(50):
        data[i][j] = (cv.resize(255-cv.imread('p.png', 0), (50, 50)).reshape(1, 2500))[0][i*50+j]
plt.imshow(data, interpolation='nearest')

if True:
    for i in range(50):
        for j in range(50):
            data[i][j] = a[lab.transform(['p'])[0]*55+5][i*50+j]
    plt.imshow(data, interpolation='nearest')

cv.imshow('N', cv.resize(255-cv.imread('N.png', 0), (50, 50)))

if True:
    import gzip
    import shutil
    with open('classifier/fetr1.txt', 'rb') as f_in, gzip.open('classifier/fetr1.txt.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
