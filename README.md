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
  
## Prerequisites

We use Python 3 as a main tool, so you need a Python interpreter (e.g. `cPython`).
Make sure you install every needed Python package from `requirements.txt`, e.g. via  
`pip3 install -r requirements.txt`  
Aside from Python, `C++ 11` is employed in time-critical places. Make sure you have a suitable compiler (e.g. `gcc`).  
The analysis is run via `Makefile`, so you need to have `make` installed. Our `Makefile` was tested on Ubuntu 16.04.


## How to use

### Running the example
After installing all prerequisites, you may want to run our example dataset (consisting of 376 tags) to be sure everything is allright. First, clone the repository via command  
`git clone https://github.com/ItsLastDay/StackOverflow_Map.git`  

Then type (from the root of the repository)  
`make visualize_example`  
It should complete in a matter of minutes. Then go to `src/visualization` folder and start a server:  
```
cd ./src/visualization
python3 -m http.server
```  
As a final step, open [http://localhost:8000/tiling_visualizer.html](http://localhost:8000/tiling_visualizer.html) in your favourite web browser (NOTE: if port #8000 is already bound to something on your computer, you can specify another port, e.g. via `python3 -m http.server 1234`). You should see something like this:  
![screen_small_mat_wide](https://cloud.githubusercontent.com/assets/6823298/20543474/fd363f1e-b116-11e6-876c-31124c40e976.jpg)  
You can navigate on the map using mouse buttons and zoom via scroll button (NOTE: after a certain zoom level you won't see anything on a map - that is normal for an example).
![screen_small_mat](https://cloud.githubusercontent.com/assets/6823298/20543477/025cc3b4-b117-11e6-8e4d-99ad35a68843.jpg)

### Running a full visualization
Now you are ready for the main part - running a visualization on the whole 50k+ set of tags. Our script allows you to specify a date **POST_DATE**. All posts earlier than this date will be filtered prior to making a visualization. This affects measuring the similarity between two tags: since we count number of questions that have both tags, filtering old questions makes the similarity more current.

From the root of the repository, type  
`make visualize POST_DATE=2012-08-25`  
(of course, you can specify any other date, but it must follow YYYY-MM-DD format)

This command requires **several hours** to complete. It will write tags in a separate folder with a POST_DATE value in it, e.g. `tiles_2012-08-25`. Don't hesitate to try different POST_DATE's - they do not overwrite each other! Then perform the steps described above:
```
cd ./src/visualization
python3 -m http.server
```  
Open [http://localhost:8000/tiling_visualizer.html](http://localhost:8000/tiling_visualizer.html) in your web browser. 
You will see a drop-down list on the left. There you can choose which visualization to show. Choose the one according to specified POST_DATE.
Hooray, you now see a full set of tags!  

Check out a video demonstration (click to play):  
[![Click to play on youtube](https://img.youtube.com/vi/mj90I_i6HNo/0.jpg)](https://www.youtube.com/watch?v=mj90I_i6HNo)

### Authors
Mikhail Koltsov ([ItsLastDay](https://github.com/ItsLastDay))  
Arkady Kalakutsky ([testlnord](https://github.com/testlnord))
