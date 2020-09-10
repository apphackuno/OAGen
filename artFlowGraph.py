"""
@author: Aisha Ali-Gombe
@contact: aaligombe@towson.edu, apphackuno@gmail.com
"""
import subprocess, sys, hashlib
#from pygraphviz import *
import networkx as nx
from collections import OrderedDict
import procFiles as proc

# mkdir /usr/local/Frameworks
# graphviz mac installation - brew install graphviz
# pygraphiz mac installation - pip install  --install-option="--include-path=/usr/local/Cellar/graphviz/2.42.3/include/" --install-option="--library-path=/usr/local/Cellar/graphviz/2.42.3/lib/" pygraphviz
# graphviz mac installation - brew install networkx

def recurseDecode(G, node):
	try:
		rootNode = node.attr['id']	
		decoded = str(decodeObject(bitmap_size_, heapBegin_, rootNode)).encode('UTF8')[1:-1]
		if 'The data for java.lang.String' in decoded:
			slice = filter(lambda x: x != "", decoded.split("The data for java.lang.String is"))[1]
			splitted = [repr(i) for i in slice.split()]
			node.attr['data']=' '.join(splitted)
			node.attr['label']= "String - "+' '.join(splitted)
		elif('Object is either null or cannot be dereferenced') in decoded:
			node.attr['data']='Object is either null or cannot be dereferenced'
			node.attr['label']= "java.lang.Object"
		elif ('The array data for' in decoded):
			type = decoded.split('The array data for ')[1]
			if not type.startswith('[L'):
				slice = filter(lambda x: x != "", decoded.rsplit("The array data for"))[1]
				node.attr['data']=' '.join(slice.split())
				node.attr['label']= "Primitive Array " + ' '.join(slice.split())
			elif("[Ljava.lang.String" in type):
				slice = filter(lambda x: x != "", decoded.rsplit("The array data for"))[1]
				node.attr['data']=' '.join(slice.split())
				node.attr['label']= "String Array " + ' '.join(slice.split())
			else:
				arr =[]
				objArray = type[type.index(' ['):type.index(']')].replace('[', '').split(',')
				[arr.append(obj.replace('\'', '').strip()) for obj in objArray if obj.replace('\'', '').strip() != '0x0']
				arr = filter(lambda x: x != "", arr)
				for x in arr:
					G.add_node(x, id=x)
					nextNode=G.get_node(x)
					G.add_edge(node,nextNode)
				#[G.add_edge(G.nodes()[index], x) for x in arr]
				node.attr['data']=' '.join(arr)
				node.attr['label']= "Object Array"
			#print decoded
		else:
			if not 'Size ' in decoded:
				node.attr['data'] ='Error'
				node.attr['label']= "Error"
			else:
				if 'Object Size ' in decoded:
					slice = decoded.split('Object Size ')
					ref= filter(lambda x: x != "", slice[0].split('\n')).pop().split(" ")[0]
					node.attr['label']= ref
				else:
					slice = decoded.split('Class Size ')
					ref = filter(lambda x: x != "", slice[0].split('\n')).pop().split(" ").pop()
				data = slice[1].split('\n')
				data = filter(lambda x: x != "", data[1:])
				counter=0
				items=[]
				while (counter <= len(data)-2):
					key= filter(lambda x: x != "", data[counter].replace('-', '').split(' '))[2]
					val= filter(lambda x: x != "", data[counter+1].replace('---', '').split(' '))[1]
					if len(key)!=1 and val!= '0x0':
						#x= G.add_node(val)
						G.add_node(val, id=val)
						nextNode=G.get_node(val)
						G.add_edge(node,nextNode)
						#G.add_edge(G.nodes()[index], val)	
					items.append(val)
					counter=counter+2
				node.attr['data']=items
				#else:
					#root.data ='Class Object'
					#node.attr['label'] = "java.lang.Class"
					#node.attr['data']="Class Definition"
		#print node.attr['id'] +" "+node.attr['label']
	except Exception, e:
		tb = sys.exc_info()[2]
		print tb.tb_lineno, e, node.attr['id']
			
		

#Slice the graph files function
# finding shortest path from start to finish, need to read graph from a file, need start node without predassasor, need list of leaf nodes			
def slicePaths_labels(g): 
	start = g.get_node(root)
	pathLists=OrderedDict()
	counter=1
	for node in g.iternodes():
		finPath=[]
		if len(g.out_neighbors(node))==0 or (g.out_neighbors(node) == g.in_neighbors(node)):
			sPath = nx.shortest_path(g,start,node) 
			[finPath.append(s.attr['label']) for s in sPath]
			pathLists.update({counter:finPath})
			counter = counter+1
	return pathLists
	
def slicePaths(g): 
	start = g.get_node(root)
	pathLists=[]
	for node in g.iternodes():
		finPath=[]
		if len(g.out_neighbors(node))==0 or (g.out_neighbors(node) == g.in_neighbors(node)):
			sPath = nx.shortest_path(g,start,node) 
			lData=[]
			for s in sPath:
				x = s.attr['data'].encode('ASCII')
				if ('0x') in x:
					[lData.append(filter(str.isalnum, entry)) for entry in x.split(',')]
				else:
					lData.append(x)
			buf=[]
			for d in lData:
				if d.startswith('0x') and not d ==('0x0'):
					buf.append(g.get_node(d).attr['label'])
				else:
					buf.append(d)
			dHash = hashlib.md5(pickle.dumps(buf)).hexdigest()
			pathLists.append(dHash)
	return pathLists
	
def simlarity(set1, set2): #list of slices in app all the threads in A- set1, list of slices in all the threads in B - set2
	import py_stringmatching as sim
	oc = sim.Jaccard() #http://anhaidgroup.github.io/py_stringmatching/v0.4.x/Jaro.html
	score = oc.get_raw_score(set1, set2)
	return score
	
def findPaths(g, start, finish): 
	start = g.get_node(start)
	finish = g.get_node(finish)
	finPath=[]
	sPath = nx.shortest_path(g,start,finish)
	[finPath.append(s.attr['label']) for s in sPath]
	return finPath
	
	
def displayGraph(gFile, pFile):
	subprocess.check_output('neato -x -Goverlap=false -o'+pFile +' -Tpng '+gFile, shell = True)	
	

#provide root, dir and depth are globals	
def getGraph(G, fName, roots):
	G.edge_attr['color']='red'
	G.edge_attr['style']='dashed'
	G.edge_attr['arrowType']='normal'
	for r in roots:
		G.add_node(r, id=r, label='', data='')
	counter=0
	for node in G.iternodes():
		recurseDecode(G, node)
		if depth>0:
			counter=counter+1
			if counter>depth:
				break
	G.write(fName)#
	
def decodeObject(bitmap_size_, heapBegin_, node):
	ret = hp.getObject(node, jvm2, lstList, mapList, bitmap_size_, heapBegin_)
	return "@ Address "+node+"\n"+ '\n'.join(ret)
	

def help():
	print "Usage: pypy artFlowGraph Command [File/Path] [Options]\n" 
	print "Available Commands:\n"
	print "Graph:   A utility for creating an object allocation graph from a memory image and a heapdump"
	print "\t\tpypy artFlowGraph Graph Path-to-ImageFiles Path-to-HeapDump Graph-OutFile.dot"
	print "Plot:    Plot the generated OAG"
	print "\t\tpypy artFlowGraph Plot Graph-InFile Plot-File.png"
	print "Strings: A utility for simple string object search"
	print "\t\tpypy artFlowGraph Strings Graph-InFile "
	print "\t\tpypy artFlowGraph Strings Graph-InFile seachString"
	print "Context: A utility that recursively find the broader context for a target object with depth and width"
	print "\t\tpypy artFlowGraph Context Graph-InFile TargetAddress -d depth"
	print "\t\tpypy artFlowGraph Context Graph-InFile TargetAddress -d depth Plot"
	print "\t\tpypy artFlowGraph Context Graph-InFile TargetAddress -w width"
	print "\t\tpypy artFlowGraph Context Graph-InFile TargetAddress -w width Plot"
	
			

def getRoot(G):
	return G.nodes()[0]
	
def getGCRoot(heapDump):
	g = open(heapDump, 'r')
	gcroot =[]
	for line in g.readlines():
		if line.startswith('Address'):
			gcroot.append(str(line.split(' ')[1]).rstrip("L"))
	g.close()
	return gcroot
	
def getGlobs(dir):
	import artThread as tSelf
	import artHeap as heap
	[nPath, rAddr, memList, mapList, listing,lstList,runtime]=art.main(dir)
	th = tSelf.android_threads() # Global Thread Object
	hp = heap.android_heap()
	[TLAB, NonTLAB, threads, bitmap_size_, heapBegin_] = art.helper(hp, th, nPath, rAddr, dir, memList)
	return [nPath, rAddr, memList, mapList, listing,lstList,runtime, th, hp, bitmap_size_, heapBegin_]

def usage():
	global dir, root, depth, gFile, nPath, rAddr, memList, mapList, listing,lstList,runtime, th, hp, bitmap_size_, heapBegin_, art, jvm, jvm2
	if len(sys.argv) == 2 and sys.argv[1]=="-h":
		help()
	elif len(sys.argv) < 3:
		print "Insufficient arguments. Try -h for usage and command options"
	else:#dir = sys.argv[1] 
		import os.path
		if (sys.argv[1]=="Graph"):#Generate Object Allocation graph from process memory dump given the starting point
			import artParse as art
			import artJVM as jvm
			import artJVM2 as jvm2
			dir = sys.argv[2]
			[nPath, rAddr, memList, mapList, listing,lstList,runtime, th, hp, bitmap_size_, heapBegin_] = getGlobs(dir)
			heapDump = sys.argv[3]
			roots =  getGCRoot(heapDump)
			gFile = sys.argv[4]
			depth=0
			G=AGraph(strict=False,directed=True)
			getGraph(G, gFile, roots)
			print G.order()
			print len(G.edges())
		elif (sys.argv[1]=="Strings" and os.path.isfile(sys.argv[2])):
			gFile = sys.argv[2]
			G=AGraph(gFile, strict=False,directed=False)
			strings = proc.getStrings(G)
			if len(sys.argv) >3:
				strSearch = sys.argv[3]
				strings = [i for i in strings if strSearch in i]
			print "\n".join(strings) # Start from a string  then plot the subgraph of the top predessaor to target
		elif(sys.argv[1]=="Object" and os.path.isfile(sys.argv[2])):
			gFile = sys.argv[2]
			G=AGraph(gFile, strict=False,directed=False)
			obj=sys.argv[3]
			objNodes = proc.getObjects(G, obj) #e.g obj "org.apache.http.impl.client.DefaultHttpClient"
			proc.printNodes(G, objNodes)
		elif (sys.argv[1]=="Plot"):#Plot the graph
			gFile = sys.argv[2]
			pFile = sys.argv[3]
			G=AGraph(gFile, strict=False,directed=False)
			Gnx = nx.nx_agraph.from_agraph(G)
			#pos = Gnx.sfdp_layout(g)
			#G.graph_draw(G, pos=pos, output="graph-draw-sfdp.pdf")
			#graphviz_draw(g,
			displayGraph(gFile, pFile)
		elif(sys.argv[1]=="Path" and os.path.isfile(sys.argv[2])):
			gFile = sys.argv[2]
			G=AGraph(gFile, strict=False,directed=False)
			start=sys.argv[3]
			finish =sys.argv[4]
			finPath = proc.findPath(G, start, finish)
			proc.printNodes(G, finPath)
		elif(sys.argv[1]=="Scope" and os.path.isfile(sys.argv[2])):
			gFile = sys.argv[2]
			G=AGraph(gFile, strict=False,directed=False)
			target=sys.argv[3]
			#jThreadNodes = proc.getThreads(G)
			#proc.printNodes(G, jThreadNodes)
			#print len(jThreadNodes)
			#proc.traversePath(jThreadNodes, target)
			depth = int(sys.argv[4])
			nodeList = proc.findDownTarget(G, target, depth)
			#proc.printNodes(G, nodeList)
			if len(sys.argv) >5 and sys.argv[5] == "Plot":
				proc.pltSub(G, sorted(nodeList))
			else:
				proc.printNodes(G, nodeList)
		elif(sys.argv[1]=="Context" and os.path.isfile(sys.argv[2])):
			gFile = sys.argv[2]
			G=AGraph(gFile, strict=False,directed=False)
			target=sys.argv[3]
			if sys.argv[4]=="-d":
				depth = int(sys.argv[5])
				nodeList = proc.getContext(G, target, depth)
			elif sys.argv[4]=="-w":
				print "here"
				width = int(sys.argv[5])
				allNodes = G.nodes()
				if target in allNodes:
					idx = allNodes.index(target)
					start = idx-width
					stop = idx+width
					nodeList=[]
					for i in range(start, stop):
						nodeList.append(allNodes[i])
					#proc.printNodes(G, nodeList)
				else:
					print "Target not Graph"
			else:
				print "Deafult to depth of 10"
				nodeList = proc.getContext(G, target, 10)
			if len(sys.argv) >6 and sys.argv[6] == "Plot":
				proc.pltSub(G, sorted(nodeList))
			else:
				proc.printNodes(G, nodeList)
		else:
			print "Invalid Option, Try -h for usage and command options"
			
if __name__ == "__main__":
	print "Android Object Allocation Graph"
	try:
		usage()
	except Exception, ex:
		print ex

