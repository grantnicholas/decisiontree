#Grant Nicholas
#10-6-2014

import csv
import sys
import random
from math import log, fabs
from pprint import pprint


def encode(str):
	if str == '\ttrue' or str == 'true':
		return 1
	elif str == '\tfalse' or str == 'false':
		return 0
	else:
		return -1


def countthem(theset):
	truecount  =0; falsecount = 0;
	for x in theset:
		if x['Class'] ==1:
			truecount +=1
		if x['Class'] ==0:
			falsecount +=1
	return (truecount, falsecount)


def entropy(*args):
	prob = []
	for k,v in enumerate(args):
		if v !=0:
			prob.append( v*1.0/sum(args) )
		else:
			prob.append( 0)

	totentropy = 0
	for k,v in enumerate(prob):
		if v!=0:
			totentropy += -1* v*log(v,2)

	return totentropy

def infogain(theset, cat):
	t,f = countthem(theset)
	eb = entropy(t,f)

	tset = [x for x in theset if x[cat]==1]
	t,f = countthem(tset)
	eat = entropy(t,f)
	eatcount = len(tset)

	fset = [x for x in theset if x[cat]==0]
	t,f = countthem(fset)
	eaf = entropy(t,f)
	eafcount = len(fset)

	ea = (1.0)*eatcount/(eatcount + eafcount)*eat + (1.0)*eafcount/(eatcount +eafcount)*eaf

	infogain = eb - ea
	return infogain

def maketree(inputset, categories,targetcat=None):
	root = {}
	tr,fa = countthem(inputset)
	if(tr==0):
		root['label']=0
		return root
	if(fa==0):
		root['label']=1
		return root
	if categories == []:
		if tr>fa:
			root['label']=1
		else:
			root['label']=0
		return root

	catgains = {}
	for cat in categories:
		catgains[cat] = infogain(inputset, cat)
	max_key = max(catgains, key=catgains.get)
	root['decision'] = max_key

	root['true'] = {}; root['false'] = {};

	tr,fa = countthem(inputset)
	mostcommon = 0
	if tr>fa:
		mostcommon = 1

	categories = [x for x in categories if categories != max_key]

	tset =[x for x in inputset if x[max_key]==1]
	if tset == []:
		root['true']['root']={};
		root['true']['root']['label']= mostcommon

	else:
		subtree = maketree(tset,categories,max_key)
		root['true'] = subtree

	fset =[x for x in inputset if x[max_key]==0]
	if fset == []:
		root['false']['root']={};
		root['false']['root']['label']= mostcommon

	else:
		subtree = maketree(fset,categories,max_key)
		root['false']= subtree

	return root



def checkThem(trainset, testset, classi):
	totalset = trainset+testset
	truecount, falsecount = countthem(trainset)
	totalcount = truecount+falsecount
	ppoutput = []
	actuals = [x['Class'] for x in testset]
	daratio = truecount*1.0/(totalcount)

	if daratio >=.50:
		for i in testset:
			ppoutput.append(1)
	else:
		for i in testset:
			ppoutput.append(0)

	dtdiff = 0; ppdiff = 0;
	for k,v in enumerate(testset):
		dtdiff += fabs(classi[k]-testset[k]['Class'])
		ppdiff += fabs(ppoutput[k]-testset[k]['Class'])

	return (actuals, ppoutput, classi, ppdiff, dtdiff)


def classifyone(obj, tree):
	if 'label' in tree:
		return tree['label']
	cat = tree['decision']
	if obj[cat]==1:
		if 'label' in tree['true']:
			return tree['true']['label']
		else:
			return classifyone(obj, tree['true'])

	elif obj[cat]==0:
		if 'label' in tree['false']:
			return tree['false']['label']
		else:
			return classifyone(obj, tree['false'])

def classifyall(tree,theset):
	arr = [];
	for obj in theset:
		classi = classifyone(obj, tree)
		arr.append(classi)
	return arr

def printarr(arr):
	for v in arr:
		print v


if __name__ == "__main__":
	
	inputfile = sys.argv[1]
	trainingsetsize = int(sys.argv[2])
	numtrials = int(sys.argv[3])
	verbose = int(sys.argv[4])
	people = []

	with open(inputfile, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		for i,row in enumerate(reader):
			dick = {};
			if i!=0:
				dick['GoodGrades'] = encode(row[0]);
				dick['GoodLetters'] = encode(row[1]);
				dick['GoodSAT'] = encode(row[2]);
				dick['IsRich'] = encode(row[3]);
				dick['HasScholarship'] = encode(row[4]);
				dick['ParentAlum'] = encode(row[5]);
				dick['SchoolActivities'] = encode(row[6]);
				dick['Class'] = encode(row[7]);
				people.append(dick);

	testsetsize = 1.0*len(people)-trainingsetsize

	categories = ['GoodGrades', 'GoodLetters', 'GoodSAT', 'IsRich', 'HasScholarship', 'ParentAlum', 'SchoolActivities']


	master = []
	for i in range(numtrials):
		trainingset = random.sample(list(enumerate(people)), trainingsetsize)
		testset = [x for x in list(enumerate(people)) if x not in trainingset]
		trainingset = [x[1] for x in trainingset]
		testset = [x[1] for x in testset]

		tree = maketree(trainingset,categories)
		decisions = classifyall(tree,testset)
		master.append((trainingset, testset, decisions, tree))


	sumppdiff = 0; sumdtdiff = 0;
	totaltrials = testsetsize*numtrials

	for k,v in enumerate(master):
		actuals, ppout, classi, ppdiff, dtdiff = checkThem(v[0], v[1], v[2])
		sumppdiff += ppdiff
		sumdtdiff += dtdiff



	print "Making a decision tree out of the data in: ", inputfile
	print "The training set size is:", trainingsetsize
	print "The testing set size is  ", len(testset)
	print "Performing ", numtrials, "trials"
	print "Mean decision tree performance:", int(sumdtdiff), "/", int(totaltrials), "incorrect"
	print "Mean prior probability performance:", int(sumppdiff), "/", int(totaltrials), "incorrect"
	print "\n\n"

	for k,v in enumerate(master):
		tree = v[3]
		actuals, ppout, classi, ppdiff, dtdiff = checkThem(v[0], v[1], v[2])
		print "Trial:", k
		print "Decisiontree incorrect classifications:        ", int(dtdiff), "/", len(testset)
		print "Prior probability incorrect classifications:   ", int(ppdiff), "/", len(testset)
		print "\n"
		pprint(tree)
		print "\n"
		if verbose:
			print "Actual classifications       ", actuals
			print "Prior prob classifications   ", ppout
			print "Decisiontree classifications ", classi
			print "\n"
			print "Trainingset: "
			printarr(v[0])
			print "\n"
			print "Testset: "
			printarr(v[1])
			print "\n"

