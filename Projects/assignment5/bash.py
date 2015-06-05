execfile("StrokeHMM.py")
x = StrokeLabeler()
x.trainHMM(["../trainingFiles/0128_1.6.1.labeled.xml", "../trainingFiles/0128_1.7.1.labeled.xml", "../trainingFiles/0128_1.8.1.labeled.xml", "../trainingFiles/0128_3.5.1.labeled.xml", "../trainingFiles/0128_3.6.1.labeled.xml"])


execfile("StrokeHMM.py")
x = StrokeLabeler()
x.evaluate("../trainingFiles/")

# Results – length
# {'text': {'text': 129, 'drawing': 245}, 'drawing': {'text': 283, 'drawing': 435}}

# Results – length, curvature
# {'text': {'text': 143, 'drawing': 211}, 'drawing': {'text': 239, 'drawing': 476}}


# Results – length, curvature, area, ratio, duration
# {'text': {'text': 88, 'drawing': 243}, 'drawing': {'text': 101, 'drawing': 546}}
# {'text': {'text': 73, 'drawing': 299}, 'drawing': {'text': 139, 'drawing': 473}}
# {'text': {'text': 136, 'drawing': 298}, 'drawing': {'text': 133, 'drawing': 573}} #69%  #81%


execfile("StrokeHMM.py")
ViterbiTestingExample()





n, bins, patches = plt.hist(duration_t, 50, normed=1, facecolor='green', alpha=0.75)
plt.show()
