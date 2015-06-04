

states = ['sunny','cloudy','rainy']
featureNames = ['groundState']
numVals = {'groundState':3}

x = HMM(states,featureNames,0,numVals)

x.priors = {'sunny': 0.63, 'cloudy': 0.17, 'rainy': 0.2}
x.emissions = {'sunny':{'groundState': [0.6,0.15,0.05]}, 'cloudy':{'groundState': [0.25,0.25,0.25]}, 'rainy':{'groundState': [0.05,0.35,0.5]}}
x.transitions = {'sunny':{'sunny':0.5 ,'cloudy':0.375 ,'rainy':0.125 },'cloudy':{'sunny':0.25 ,'cloudy':0.125 ,'rainy':0.625 }, 'rainy':{'sunny':0.25 ,'cloudy':0.375 ,'rainy':0.375 }}

input = [{'groundState':0},{'groundState':1},{'groundState':2}]

a = x.label(input)
print a 