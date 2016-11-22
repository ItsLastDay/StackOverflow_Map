# StackOverflow Map

This is a project for creating 2D visualization of [StackOverflow](http://stackoverflow.com/)
tags using [t-SNE](https://lvdmaaten.github.io/tsne/) 
algorithm. See a bit more thorough [problem description](https://github.com/ItsLastDay/StackOverflow_Map/wiki/Problem-description).

Everything is written in Python 3.5 and C++.

## Project structure

Our repository follows [cookiecutter](http://drivendata.github.io/cookiecutter-data-science/) Data Science template.  
  - `data` folder contains data on all stages of processing: `raw` for unprocessed data, `interim` for intermediate results, `processed` for results of heavy computations (these do not require further processing).  
  `example` folder contains information about small subset of tags (~400 of them).   
  You can read more about our data on a wiki [page](https://github.com/ItsLastDay/StackOverflow_Map/wiki/Data);
  - `src` folder contains scripts that transform data or infer information from it.  
  `data` folder holds scripts for initial data transformation (from `raw` to `interim`).  
  `models/use_bhtsne` contains scripts that prepare data for using it in t-SNE, as well as a slightly rewritten version of [bhtsne](https://github.com/lvdmaaten/bhtsne).  
  `visualization` folder holds the last part of the equation - the frontend. 
  


### Authors
Mikhail Koltsov ([ItsLastDay](https://github.com/ItsLastDay))  
Arkady Kalakutsky ([testlnord](https://github.com/testlnord))
