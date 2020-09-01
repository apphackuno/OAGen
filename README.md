# OAGen is a post-execution and app-agnostic semantic analysis for Android
designed to help investigators establish concrete evidence by identifying the provenance 
and relationships between in-memory objects in a process memory image.

OAGen utilizes Points-to analysis to reconstruct a runtime’s object allocation network. 
The resulting graph is then fed as an input into our semantic analysis algorithms to 
determine objects’ origin, context, and scope in the network. 

Dependencies
=========================
PyPy - https://www.pypy.org

pygraphviz - https://pygraphviz.github.io

networkx - https://networkx.github.io

Requirements:
=========================
ProcMem - Extract per process memory from Android device or emulator using Memfetch (Only evaluated on Android 8.0.0)

Heapdump - Dump the heap allocation using DroidScraper ()

Note:
  Request for test images and heapdump by emailing apphackuno@gmail.com


OAG Generation
==================
Generate graph for each memory image –

  pypy artFlowGraph.py Graph path-to-ProcMem path-to-Heapdump graph-out-file.dot
  
Example:

  pypy artFlowGraph.py Graph /ProcMem/org.thoughtcrime.securesms/  /HeapDumps/signal.out signal.dot
 
Strings Utility
====================
General string search -

  pypy artFlowGraph.py Strings whatApp2AllObj.dot
  
Specific string search, e.g. "Tree of Life, City of Bridges"

  pypy artFlowGraph.py Strings whatApp2AllObj.dot "Tree of Life, City of Bridges"


Context Determination 
======================================
To examine the context for 0x136b4078
Run context with 0x136b4078 as target 

1) To output only the nodelist in the subgraph generated by the context determination algorithm-

  pypy artFlowGraph.py Context whatApp2AllObj.dot 0x136b4078 50

2)Plot the graph and visualize the subgraph – 

  pypy artFlowGraph.py Context whatApp2AllObj.dot 0x136b4078 50 Plot
  
Due to our code review and optimization as well as differences CPU and memory capacity, result may differ in the size of OAG (number of nodes and edges) as well as processing time.
