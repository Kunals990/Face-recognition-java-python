import os
import random
import shutil
from itertools import islice

outputFolderpath = 'DataSets/SplitData'
inputFolderPath = 'DataSets/all'
splitRatio = {"train":0.7,"val":0.2,"test":0.1}
classes = ["fake","real"]

try:
    shutil.rmtree(outputFolderpath)
    # print("Directory removed")

except OSError as e:
    os.mkdir(outputFolderpath)

# ----------Directories to Create -------
os.makedirs(f"{outputFolderpath}/train/images",exist_ok=True)
os.makedirs(f"{outputFolderpath}/train/labels",exist_ok=True)
os.makedirs(f"{outputFolderpath}/val/images",exist_ok=True)
os.makedirs(f"{outputFolderpath}/val/labels",exist_ok=True)
os.makedirs(f"{outputFolderpath}/test/images",exist_ok=True)
os.makedirs(f"{outputFolderpath}/test/labels",exist_ok=True)

# ----------Get Name -------
listNames = os.listdir(inputFolderPath)
# print(listNames)
# print(len(listNames))
uniqueNames=[]
for name in listNames:
    uniqueNames.append(name.split('.')[0])
uniqueNames = list(set(uniqueNames))

# print(len(uniqueNames))

# ----------Shuffle -------
random.shuffle(uniqueNames)
# print(uniqueNames)

# ----------Find number of Images in each folder-------
lenData = len(uniqueNames)
print(f"Total Images :{uniqueNames}")
print(f"Total Images :{lenData}")
lenTrain = int(lenData*splitRatio['train'])
lenVal = int(lenData*splitRatio['val'])
lenTest = int(lenData*splitRatio['test'])
print(f"Total Images:{lenData} \nSplit:{lenTrain} {lenVal} {lenTest} ")

# ----------Put remaining data into Train-------
if lenData != lenTrain+lenTest+lenVal:
    remaining = lenData - (lenTrain+lenTest+lenVal)
    lenTrain +=remaining

print(f"Total Images:{lenData} \nSplit:{lenTrain} {lenVal} {lenTest} ")

# --- Split the list ----
lenToSplit = [lenTrain,lenVal,lenTest]

Input = iter(uniqueNames)
Output = [list(islice(Input,elem)) for elem in lenToSplit]
print(f"Total Images :{lenData} \nSplit: {len(Output[0])} {len(Output[1])} {len(Output[2])}")

# ---- Copy the files ---

sequence = ['train','val','test']
for i,out in enumerate(Output):
    for filename in out:
        shutil.copy(f"{inputFolderPath}/{filename}.jpg",f'{outputFolderpath}/{sequence[i]}/images/{filename}.jpg')
        shutil.copy(f"{inputFolderPath}/{filename}.txt",f'{outputFolderpath}/{sequence[i]}/labels/{filename}.txt')

print("Split process completed...")

# -- Creating Data.yaml file ---

dataYaml = (f'path:../Data\n\
train:../train/images\n\
val:../val/images\n\
test:../test/images\n\
\n\
nc:{len(classes)}\n\
names = {classes}'
)

f = open(f"{outputFolderpath}/data.yaml",'a')
f.write(dataYaml)
f.close()