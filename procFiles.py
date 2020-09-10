"""
@author: Aisha Ali-Gombe
@contact: aaligombe@towson.edu, apphackuno@gmail.com
"""
#!/usr/bin/python
import sys, collections
from pygraphviz import *
import networkx as nx
#import numpy as np
from networkx.algorithms.connectivity import k_components
from collections import OrderedDict
#import matplotlib.pyplot as plt

def findPath(g, start, finish): 
	start = g.get_node(start)
	finish = g.get_node(finish)
	finPath=[]
	sPath = nx.shortest_path(g,start,finish)
	[finPath.append(s.attr['label']) for s in sPath]
	return finPath
	
	
def getStrings(G):
	strNodes = [node.attr['id']+" "+node.attr['label'] for node in G.iternodes() if str(node.attr['label']).startswith("String - ")]
	return strNodes
	
def getThreads(G): #ALl Threads
	jThreadNodes = [node for node in G.iternodes() if "java.lang.Thread" == str(node.attr['label'])]
	return jThreadNodes
	
def getObjects(G, obj): #Searcg of Objects
	objNodes = [node for node in G.iternodes() if obj == str(node.attr['label'])]
	return  objNodes

def getRoot(G):
	return G.nodes()[0]	
	
def findPaths(G, Gnx, start, finish): 
	finPath=[]
	sPath = nx.shortest_path(Gnx,start,finish)
	[finPath.append(G.get_node(s).attr['label']+ " "+s) for s in sPath]
	print "\n".join(finPath)
	return sPath
	
def findTargetStr(G, targetStr): 
	nodeList=[]
	[nodeList.append(node) for node in G.iternodes() if str(node.attr['label']).startswith("String - ") and targetStr in node.attr['label']]
	ret = OrderedDict()
	for n in nodeList:
		ret.update({n:findTarget(G, n)})
	return ret
#recursively iterate iterpred until empty to get all nodes from target until root
def findTarget(G, node, depth): 
	nodeList=[node]
	for n in nodeList:
		for i in G.iterpred(n):
			nodeList.append(i)
		depth = depth-1
		if depth==0:
			break
	return nodeList

#recursively iterate itersucc until empty to get all nodes from target until root
def findDownTarget(G, node, depth): 
	nodeList=[node]
	for n in nodeList:
		for i in G.itersucc(n):
			nodeList.append(i)
		depth = depth-1
		if depth==0:
			break
	return nodeList

def pltSub(G, nodeList):
	import os
	pFile = "plotFile.png"
	H = G.subgraph(nodeList)
	H.layout(prog='dot')
	H.draw(pFile)
	print "Plot in "+os.getcwd()+"/"+pFile
	
def fromRoot(G, Gnx, goal):
	start = getRoot(G)
	finish = G.get_node(goal)
	findPaths(G, Gnx, start, finish)

def getData(dataList, offset):
	ret = dataList.encode("ASCII").split(",")[offset].strip(" []\'")
	return ret
	
	
def getComponents(G): 
	compNodes=[]
	objList =["android.app.ActivityThread$ActivityClientRecord", "android.app.ActivityThread$ProviderClientRecord", "android.app.LoadedApk$ReceiverDispatcher", "android.app.LoadedApk$ServiceDispatcher"]
	for obj in objList:
		objs = getObjects(G, obj)
		print obj +" "+str(len(objs))
		[compNodes.append(o) for o in objs]
	return compNodes

def printNodes(G, nodeList):
	for node in nodeList:
		print G.get_node(node).attr['label']+" "+node
			
def getContext(G, target, depth):
	nodeList = findTarget(G, target, depth)
	#nodeList = findPaths(G, Gnx, start, finish)
	edgeList=[]
	for n in nodeList:
		[edgeList.append(e) for e in G.edges(nodeList)]
	H = nx.Graph(edgeList)
	nodeList=[]
	[nodeList.append(n) for n in H.nodes()]
	return nodeList
		
#Find path to target from program components or threads	
def traversePath(nodesList, target):
	for objNode in nodesList:
		try:
			finPath=[]
			start = G.get_node(objNode)
			finish = G.get_node(target)
			sPath = nx.shortest_path(Gnx, start, finish)
			[finPath.append(G.get_node(s).attr['data']) for s in sPath]
			print objNode+"-----------"
			print "\n".join(finPath)
		except:
			print "No path between "+ objNode +" and "+ target

def lrc(G, Gnx):
	cent=[]
	for node in G.iternodes():
		c = nx.local_reaching_centrality(Gnx, node)
		if c==1.0:
			cent.append(node)
	return cent
	