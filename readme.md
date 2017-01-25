This is a repository for the source code for posts on unburythelead.com. The figures appearing in each post can be found in the folders in the top directory. The CommonData folder contains many subdirectories which hold various data which are used for multiple posts. This will contain voting data, shape files for geovisualization, election finance data, and so on. This folder also contains routines fetching and storing data for later use. The utilities folder contains some useful functions.

There are several dependencies for the various scripts here including

numpy
scipy
pandas
geopandas
pysal
pyproj
matplotlib
bs4
us

The census shapefiles used here can be found on the census website https://www.census.gov/geo/maps-data/data/tiger-cart-boundary.html. Download the state and county files and unzip them in the /CommonData/ShapeFiles directory
