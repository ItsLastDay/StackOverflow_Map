# Managing data of the SOMap problem

## Data sources

### data.stackexchange
[Data Explorer](http://data.stackexchange.com/help) is a website where you can make SQL-queries to DMBS with current 
data of Stack Exchange sites. One of the sites is our beloved StackOverflow.  
Although quite convenient, this method has several disadvantages:
 - result set for a query is limited to 50k rows 
 ([link](https://github.com/StackExchange/StackExchange.DataExplorer/blob/069bf5e441cf6717258479b862cc1f190ef1f7b4/App/StackExchange.DataExplorer/AppSettings.cs));
 - there is no intended way to query and parse results automatically.  
 
Data Explorer is good for catching the drift of current situtation, ad-hoc queries, etc.  
Some of my queries: [here](http://data.stackexchange.com/users/24326/mike-koltsov?order_by=favorite).

### Full dump at archive.org
There is a .torrent [dump](https://archive.org/details/stackexchange) of Stack Exchange data, which is updated 
approximately bi-yearly. It is a snapshot of some particular DB state.    
While more directly accessible, this dump is too comprehensive. 

### StackLite
There is a githup repo called [StackLite](https://github.com/dgrtwo/StackLite), that provides minified version of the 
dump. That version contains mostly question metadata, which is sufficient for our needs (because it includes tags).

## Data storage

### Matrix format
The adjacency matrix, which must be obtained from the graph, has the following format:  
`vertex_from: vertex_to1,w1 vertex_to2,w2 ... vertex_tok,wk`  
Each row starts with a vertex number, that this row is describing. Then zero or more space-separated strings come,
each has a destination vertex, followed by a comma, followed by `w(source, dest)`. Each destination vertex number
must be greater than the source number: we store only higher-than-main-diagonal part of the matrix.  
Example:
```
1: 3517,1
2:
3: 41,1 44,1 54836,1
4: 37043,1 44404,1
6:
7: 33,6 95,1 106,2 228,1 1098,1 1547,4 1906,1 3196,5
```
