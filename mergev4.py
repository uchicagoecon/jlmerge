#v4 of the python matching algorithm
#we process fsc first in this version

#packages used
import csv
from Levenshtein import *
import time

#this function checks whether NAV values are similar
#we use a band variable to determine the range we are ok with
#THIS FUNCTION HAS BEEN DEBUGGED

def NAVCheck(N1, N2):
  if N1 != "" and N2 != "":
    N1 = float(N1)
    N2 = float(N2)
  else:
    return -1
  band = N1*0.02
  if N2 < N1 + band and N2 > N1 - band:
    return abs(N1-N2)
  else:
    return -1

#nMatch looks for a match for list a in the dataset dset (the entirety of dataset 2)
#it returns the best match
#note that it matches off string similarities
#THIS FUNCTION HAS BEEN DEBUGGED

def nMatch(a,dset):
  levthresh = 0.6
  levscore = 1
  navscore = 1
  temp = []
  count = 0
  decide = 0
  for b in dset:
    cur_nav = NAVCheck(a[8],b[11])
    if a[7] == b[10] and cur_nav>=0 and marked[count] < 0:
      lratio = ratio(a[1],b[9])
      if len(temp) == 0:
        if lratio > levthresh:
          temp = b
          levscore = 1-lratio
          navscore = cur_nav
          decide = count
      else:
        if lratio > ratio(a[1],temp[9]):
          temp = b
          levscore = 1-lratio
          navscore = cur_nav
          decide = count
    count = count + 1
  if temp != []:
    nresult = a + temp
    marked[decide] = 1
    #we include their NAV score and lev score
    #the closer to 0, the more ideal the match
    nresult.append(navscore)
    nresult.append(levscore)
    return nresult
  else:
    return []

#this function just finds the fsc code/date match, and returns it if NAV is similar
#THIS FUNCTION IS DEBUGGED
def fscMatch(a,dset):
  count = 0
  decide = 0
  for b in dset:
    navscore = NAVCheck(a[8],b[11])
    if marked[count] < 0 and a[2] == b[6] and a[7] == b[10] and (a[11] == 1 or navscore >=0):
      #we add a NAV score, and the lev score is automatically 0
      nresult = a + b
      nresult.append(navscore)
      nresult.append(0)
      marked[count] = 1
      return nresult
    count = count + 1
  return []

#mark beginning of runtime
start_time = time.time()

#this step imports the datasets into lists comp1 (fundata) and comp2 (univeris)
fundataCSV = csv.reader(open('fundata.csv','rb'),delimiter=',',quotechar='"')
univerisCSV = csv.reader(open('ivd_univeris.csv','rb'),delimiter=',',quotechar='"')
'''
#test data ver
fundataCSV = csv.reader(open('test1.csv','rb'),delimiter=',',quotechar='"')
univerisCSV = csv.reader(open('test2.csv','rb'),delimiter=',',quotechar='"')
'''

univerisCSV.next()
fundataCSV.next()

#comp1 is fundata
#comp2 is univeris
#fscs is fundservcodes of univeris data
comp1 = []
comp2 = []
fscs = []

for row in fundataCSV:
  comp1.append(row)

for row in univerisCSV:
  comp2.append(row)
  fscs.append(row[6])

#then we clean up structural problems in the strings
#we have a key that corresponds to the following problems
#problem 1: there are random stars in the strings of ivd_univeris
#problem 2: class/series must be exact match (end of string)
#problem 3: random abbreviations need exact match
#THIS CHUNK OF CODE IS DEBUGGED
swapoutCSV = csv.reader(open('swapout.csv','rb'),delimiter=',',quotechar='"')
swapout = []
for row in swapoutCSV:
  swapout.append(row)

for row in comp1:
  for swap in swapout:
    row[1] = row[1].replace(swap[0],swap[1])

for row in comp2:
  for swap in swapout:
    row[9] = row[9].replace(swap[0],swap[1])

#now we need to make sure we get exact NAV matches for funds without a lot of entries
#for all the entries in column 11 (comp1) column 12 (comp2)
#1 means we have 10+ samples
#0 means we don't
cnt = 0
len1 = len(comp1)
while cnt < len1:
  if cnt > 10 and cnt < len1-11:
    start = cnt - 10
    end = cnt + 10
    holder = []
    while start < end:
      holder.append(comp1[start][1])
      start = start + 1
    num = holder.count(comp1[cnt][1])
    if num >= 10:
      comp1[cnt].append(1)
    else:
      comp1[cnt].append(0)
  else:
    comp1[cnt].append(1)
  cnt = cnt + 1


#we also want to mark which slots are already taken in comp2
#-1 means not matched 1 means matched
global marked
marked = [-1]*len(comp2)
global c1taken
c1taken = [-1]*len(comp1)

#now we insert our results into our array called "final"
final = []
count1 = 0

for s in comp1:
  print count1
  #check if fundservcode exists in comp1 and comp2
  #if so, send it into fscMatch
  if s[2] != "" and s[2] in fscs:
    fMed = fscMatch(s, comp2)
    if fMed != []:
      final.append(fMed)
      c1taken[count1] = 1
  count1 = count1 + 1

count2 = 0
for s in comp1:
  print count2
  if c1taken[count2] < 0:
    nMed = nMatch(s,comp2)
    if nMed != []:
      final.append(nMed)
  count2 = count2 + 1

with open('mergeddata.csv','wb') as csvfile:
  merge = csv.writer(csvfile)
  for x in final:
    merge.writerow(x)

#mark endtime
end_time = time.time()

print("Elapsed time was %g seconds" % (end_time - start_time))
