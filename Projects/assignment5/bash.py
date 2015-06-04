execfile("StrokeHmm.py")
x = StrokeLabeler()
x.trainHMM(["trainingFiles/0128_1.6.1.labeled.xml", "trainingFiles/0128_1.7.1.labeled.xml", "trainingFiles/0128_1.8.1.labeled.xml", "trainingFiles/0128_3.5.1.labeled.xml", "trainingFiles/0128_3.6.1.labeled.xml"])
x.returnConfusionMatrix("trainingFiles/0128_1.6.1.labeled.xml")


execfile("StrokeHmm.py")
x = StrokeLabeler()
x.evaluate("../trainingFiles/")