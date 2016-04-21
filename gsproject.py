import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import gsq.ci_tests as gsq
from itertools import chain, combinations
import logging
logging.basicConfig()

#The function for conditional indepenence test.
# The value 1 means conditional indepenence
def citest(data,x,y,z,threshold):
    p=gsq.ci_test_dis(data,x,y,z)
    if p>threshold:
        value=1
    else:
        value=0
    return value

#The function for finding the markov blanket of node X
#Return a list S
def markovblanket(Xnodeindex,data,threshold):
    S=[]
    for Ynodeindex in range(0,data.shape[1]):
       if Ynodeindex!=Xnodeindex:
          Value=citest(data,Xnodeindex,Ynodeindex,S,threshold)
          if Value == 0:
              S.append(Ynodeindex)

    for Index in S:
        if len(S)>1:
            Sy=S
            Sy.remove(Index)
        elif len(S) == 1:
            Sy=[]
        Value=citest(data,Xnodeindex,Index,Sy,threshold)
        if Value == 1:
            S.remove(Index)

    return S


#The function for finding a smaller between two sets X and Y
def Findsmallset(X,Y):
    if (X==None) or (Y==None):
        T=[]
    elif len(X)<len(Y):
        T=X
    else:
        T=Y
    return T

#The function for finding all the subsets for a set S
def Subset(S):
  xs = list(S)
  return chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1))


#The function for finding all the neighbour
#return N as a dictionary N={node: its neighbour}
def Neighbor(data,threshold):
    MB={}
    N={}
    for index in range(0,data.shape[1]):
        MB[index]=markovblanket(index,data,threshold)

    for Xindex in range(0,data.shape[1]):
        MBX=MB[Xindex]
        for Yindex in MBX:
            MBY=MB[Yindex]
            if (Yindex in MBX) and (Xindex in MBY):
                T=Findsmallset(MBX.remove(Yindex), MBY.remove(Xindex))
            else:
                T=Findsmallset(MBX, MBY)
            Tsubset=list(Subset(set(T)))
            v=0
            for S in Tsubset:
                value=citest(data,Xindex,Yindex,S,threshold)
                if value == 1:
                    v=value
            if v==0:
                N[Xindex]=Yindex

    for Xindex in range(0,data.shape[1]):
        if Xindex not in N.keys():
            N[Xindex]=[]

    return N


def main():
    #load dataset
    testdata=np.loadtxt("testdata.csv",delimiter=',')
    threshold=0.05
    #Find all the markov blankets of all nodes
    MB={}
    for index in range(0,testdata.shape[1]):
        MB[index]=markovblanket(index,testdata,threshold)
    N=Neighbor(testdata,threshold)
    Nud=N
    #This part do the orient edge part.Save the direction result in ND
    ND={}
    for Xindex in N.keys():
        for Yindex in MB[Xindex]:
            if N[Yindex]==[] and N[Xindex]==[]:
                Z=set(N[Xindex])-set(N[Yindex])-set([Yindex])
            elif N[Yindex]==[]:
                Z=set([N[Xindex]])-set(N[Yindex])-set([Yindex])
            elif N[Xindex]==[]:
                Z=set(N[Xindex])-set([N[Yindex]])-set([Yindex])
            else:
                Z=set([N[Xindex]])-set([N[Yindex]])-set([Yindex])
            for Zindex in Z:
                TY=list(set(MB[Yindex])-set([Xindex,Zindex]))
                TZ=list(set(MB[Zindex])-set([Xindex,Yindex]))
                T=Findsmallset(TY,TZ)
                Tsubsets=Subset(T)
                for S in Tsubsets:
                    S=list(set(S)+set([Xindex]))
                    value=citest(testdata,Yindex,Zindex,S)
                    if value==0:
                        ND[Xindex]=Yindex

    #If ND is empty,we can draw undirection graph
    if ND == {}:
        G=nx.Graph()
        G.add_nodes_from(range(0,testdata.shape[1]))
        for Xnode,Ynode in Nud.items():
            if Xnode and Ynode !=[]:
                G.add_edge(Xnode,Ynode)

    #If ND is not empty, we can draw direction graph
    else:
        G=nx.DiGraph()
        G.add_nodes_from(range(0,testdata.shape[1]))
        for Xnode,Ynode in ND.items():
            if Xnode and Ynode !=[]:
                G.add_edge(Ynode,Xnode)

    nx.draw(G,with_labels=True)
    plt.show()

if __name__ == "__main__":
    main()
