# cell_tracking
### Setup Python:
Follow steps 1-5 to install python and PIP:
https://phoenixnap.com/kb/how-to-install-python-3-windows

### Download Code + Requirements:
Download + unzip the source code zip file anywhere (Importantly need _py_version.py_ and _requirements.txt_)  
#### Open Command Prompt (Win + R -> "cmd")  
![cmd window](https://i.gyazo.com/c261b9088febf0cb524f747acbd06ea0.png)  


#### _cd "Path/to/Folder"_
![cd](https://i.gyazo.com/0be3b794ebc53641c2b9d12ce7c7f7e4.png)  


#### Install all the necessary libraries  
_pip install -r requirements.txt_
![pip](https://i.gyazo.com/2fef0549001c19ced284d6ba6b71831f.png)  


Most should be okay, but might get an error that no matching opencv version can be found.  
If so, try _pip install opencv-python_ (May take a few minutes to finish)

## Running the Program:
If everything is set up, the program can be run with  
#### _python py_version.py_  
if in the folder, or  
#### _python "path/to/py_version.py"_  
from anywhere

Note: the program requires you pass the video at command line (-v flag), which can be a full path or relative path.
If video is in the same folder:
#### _python py_version.py -v V4.avi_
Or to access any video
#### _python py_version.py -v "C:\Users\Jefferson\OneDrive - University of Pittsburgh\Pitt\2021 Fall\Research\m_code\cell_tracking\V4.avi"_

### Example / Results:
First, the program will display basic information about the video properties, such as FPS, length, etc.  
Then, the program will begin processing chunks of video. It will display the calculated threshold and frame number reached in this chunk  
Finally, it will display information about execution, including processing duration and speed (FPS), total number of cells counted, and the location of the output files.  
The outputs are saved in an "output" folder and labeled "video_name_type" in data (.csv) and graph (.png) forms
![demo](https://i.gyazo.com/83b9c7ab1b215f4a7b37ef9f00e965ce.png)


### Debug Flag:
Lastly, in addition to supplying a video, you can use "-d 1" to enable debug mode, which will stop after each chunk and display the image results and labeled cells.
This will freeze until you press any key ("Q" is standard) before proceeding to process then display the next chunk.
This can be helpful when altering parameters inside the program to accomodate a specific video.
#### _python py_version.py -v V4.avi -d 1_
