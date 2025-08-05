import pandas as pd
import plotly.express as px
from itertools import combinations, permutations

def visualizeEverything(df,iColumns:list[str] | None=None,maxPermutations:int | None=None,maxGraph:int|None=None,permute:bool|None=False):
    try:
        savedGraphMemory=maxGraph
        plottedPer=1
        plottedGraph=1
        dfNew=df.copy()
        dfNew.columns=dfNew.columns.str.strip()
        if iColumns is not None:
            dfNew=dfNew[list(map(str.strip,iColumns))]
        columns=dfNew.select_dtypes(include="object").columns
        for i in columns:
            if dfNew[i].nunique()<=20:
                dfNew[i]=pd.factorize(dfNew[i])[0]
            else: 
                dfNew.drop(i,axis=1,inplace=True)
        finColumns=list(dfNew.select_dtypes(include='number').columns)
        if len(finColumns)<1:
            return
        else:
            finColumns=list(permutations(finColumns,2) if permute==True else combinations(finColumns,2))
            print(f"List of Permutation:\n{finColumns}" if permute else f"List of Combinations:\n{finColumns}")
            second=finColumns[0][1]
            forPermute=-1
            for i, j in finColumns:
                forPermute+=1
                if (maxGraph is not None and maxPermutations is not None and permute==True) or (maxPermutations is not None and permute):
                    print("\n\033[93mPermute can be only be set to True, if \033[1mEITHER\033[0m\033[93m maxGraph or maxPermuations is set to None\033[0m \n Or \n \n\033[93mPermute can't be True, if MaxPermutations is not None\033[0m")
                    break

                elif (maxGraph is not None and maxPermutations is None and plottedGraph<=maxGraph) or (maxGraph is None and maxPermutations is not None and plottedPer<=maxPermutations):
                    if i==second:
                        if maxPermutations is not None and plottedPer<maxPermutations:
                            fig=px.scatter(dfNew,x=i,y=j,title=f"Scatter Plot: {i.upper()} with {j.upper()}")
                            fig.show()
                        elif (maxPermutations is None and maxGraph is not None):
                            fig=px.scatter(dfNew,x=i,y=j,title=f"Scatter Plot: {i.upper()} with {j.upper()}")
                            fig.show()
                        plottedPer+=1
                        second=j
                        continue
                    fig=px.scatter(dfNew,x=i,y=j,title=f"Scatter Plot: {i.upper()} with {j.upper()}")
                    fig.show()
                    plottedGraph+=1 if maxGraph is not None else plottedGraph

                elif (maxGraph is not None and maxPermutations is not None and permute==False):
                    if i == second:
                        if plottedPer==maxPermutations:
                            break
                        else: 
                            fig=px.scatter(dfNew,x=i,y=j,title=f"Scatter Plot: {i.upper()} with {j.upper()}")
                            fig.show()
                            plottedPer+=1
                            second=j
                            plottedGraph=2
                    else:
                        if plottedGraph>maxGraph:
                            continue
                        else:
                            fig=px.scatter(dfNew,x=i,y=j,title=f"Scatter Plot: {i.upper()} with {j.upper()}")
                            fig.show()
                            plottedGraph+=1

                elif (maxGraph is None and maxPermutations is None):
                    fig=px.scatter(dfNew,x=i,y=j,title=f"Scatter Plot: {i.upper()} with {j.upper()}")
                    fig.show()
    except Exception as e:
        print(f"Error: {e}")