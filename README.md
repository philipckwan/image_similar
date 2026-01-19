# image_similar
Python based program using DeepImageSearch module to search similar images within a directory

This is a python program that uses the DeepImageSearch library:<br/>
https://github.com/TechyNilesh/DeepImageSearch<br/>
An AI-based image search engine, to search within a directory of image files that are similar.

The background of me developing this tool is that I have a habit of backing up all the photos from my mobile phone around once a year.<br/>
Every time, after such backup of photos from my phone to my laptop, I can see that there are a lot of photos that I don't want to keep.<br/>
For example, I received a lot of Whatsapp photos of someone's phone capture, or photos of newspaper clips.<br/>
So, I developed this tool that leverages the DeepImageSearch, along with some customization that I built on top of it, in order to suit my use.


Features
-

This tool:
* takes a source folder which should contain a lot of images/photos
* takes a match folder or file, which should contain at least a single image, up to several images<br/>
These files will be used to match, or find similar images, from the source folder<br/>
* runs image processing to first load and index the images, then find similar images according to the match file(s)<br/>
These files can then be copied or moved to the destination directory

Usage
-

First, assuming *python* and *pip* are already installed, need to install the DeepImageSearch module:<br/>
```shell
pip install DeepImageSearch
```

Then, this tool has other dependencies such as shutil, configparser, logging, etc...<br/>
If they are not installed already, use the same *pip* command to install them just like the above example.

Next, make a copy of the *config.txt.example* to *config.txt* in order to specify configurations to run the tool properly.
Update the parameters inside config.txt to suit your need.
* imgSourceDirectory - specify the source folder which should contain a lot of images/photos<br/>
```imgSourceDirectory=/Users/philip/Pictures/whatsapp_photos```<br/>
* imgMatchFileOrDirectory - specify a match folder or file, which should contain at least a single image, up to just several images (recommended)<br/>
```imgMatchFileOrDirectory=/Users/philip/desktop/whatsapp_photos/01-phone_white_screen.jpg```<br/>
* imgProcessedDirectory - specify the output, or processed, folder. Resulting image files that are matched will be moved or copied here<br/>
```imgProcessedDirectory=/Users/philip/Pictures/photo_albums/2022/whatsapp_photos_filtered```<br/>
* imgControlDirectory - can just leave this blank for now, as usage is still being decided<br/>
* matchPattern - specify how the matching output are to be grouped together<br/>
```matchPattern=5,15```<br/>
For the above setting, the first 5 closest matched images will be grouped into the first folder "5".<br/>
Then, the next 15 closest matched images will be grouped into the next folder, in which the folder name will be "20"<br/>
* processMode - specify the treatment of a matched file. It accepts only 2 settings: (1) copy, and (2) move<br/>
```processMode=move```<br/>
Specifying "copy" will simply make a copy of the matched file to the processed directory, while "move" will move the file to the processed directory (i.e. it will be removed from the source directory)<br/>
* shouldIncludeNonExistedFiles - this is to specify whether to count a file that is no longer existed in the source folder, just take the default "true" for now<br/>
```shouldIncludeNonExistedFiles=true```<br/>

Next, run the program on the command line.<br/>
```python
python3 pck_image_similar.py
```

Optional Command Line Arguments for Advanced Usage
-

There are some optional command line arguments.
* -s - specify among the two key DeepImageSearch steps (load and index, search and process), which one to skip for this run<br/>
This is for more advanced usage.<br/>
As for myself, I want to split the loading and searching of photos, in order to fine tune the matching part.<br/>
I will run the load and index step once, then I will run multiple times of searching in separate program runs<br/>
```-sS```<br/>
Will skip the searching step, only do the loading the indexing steps, this should be done first<br/>
```-sL```<br/>
Will skip the loading and indexing steps, only do the searching step, this should be done after loading and indexing are done<br/>
* -m - override the imgMatchFileOrDirectory field in the config.txt<br/>
Specifying -m followed by the filepath to a match file will override the setting in config.txt.<br/>
```-m <filepath>```<br/>
This should be done when the searching step is not skipped<br/>

This is how I use the tool with the -s and -m options<br/>
First, do loading and indexing, thus will skip searching:
```python
python3 pck_image_similar.py -sS
```

Then, do the searching, thus will skip loading and indexing<br/>
Also, specify the -m if preferred:
```python
python3 pck_image_similar.py -sL -m /Users/philip/Pictures/match/01-phone_screen_white.jpg
```
Using -m option allow me to quickly match another file later:
```python
python3 pck_image_similar.py -sL -m /Users/philip/Pictures/match/04-renovations_room_of_cement.jpg
```
