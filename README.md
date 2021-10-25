![Upload Python Package](https://github.com/OpenPIV/openpiv_tk_gui/workflows/Upload%20Python%20Package/badge.svg)

# A GUI for Open PIV python

This graphical user interface provides an efficient workflow for evaluating and postprocessing particle image velocimetry (PIV) images. OpenPivGui relies on the Python libraries provided by the [OpenPIV project](http://www.openpiv.net/) and H5Py.

![Screen shot of the GUI showing a vector plot.](https://raw.githubusercontent.com/OpenPIV/openpiv_tk_gui/master/fig/open_piv_gui_vector_plot.png)

[Installation](#installation)

[Launching](#launching)

[Usage](#usage)

[Video Tutorial](#video_tuturial)

[Documentation](#documentation)

[Contribution](#contribution)


## Installation <a id=installation></a>

You may use Pip to install `OpenPivGui`:

```
pip3 install openpivgui
```

## Launching <a id=launching></a>

Launch `OpenPivGui` by executing:

```
python3 -m openpivgui.OpenPivGui
```

## Usage <a id=usage></a>

1. Press »File« then »load images«. 
Select some image pairs (Ctrl + Shift for multiple).

2. Click on the links in the image list to view the imported 
images and press »Apply frequencing« to load the images
into the GUI.

3. Walk through the drop-down-menues in »Pre-processing«
and »Analysis« and edit the parameters.

4. Calibrate your images or results with the »Calibration« 
drop-down-menu.
       
5. Press the »Analyze all frame(s)« butten to 
start the processing chain. Analyzing the current frame 
saves the correlation matix for further analysis.
    
6. Validate/modify your results with the »Post processing« 
drop-down-menu.
    
7. Inspect the results by clicking on the links in the frame-list
on the right.
Use the »Data exploration« drop-down menu for changing
the plot parameters.

8. Re-evaluate images if needed (results are automatically
deleted) with new information/parameters.

9. Export results by going to »File« --> »Export« --> »Results as ASCI-II«.


## Video tutorial <a id=video_tutorial></a>

Learn how to use and extend OpenPivGui [watching a less than eight minute video tutorial](https://video.fh-muenster.de/Panopto/Pages/Viewer.aspx?id=309dccc2-af58-44e0-8cd3-ab9500c5b7f4).


## Documentation <a id=documentation></a>

Find the [detailed documentation on readthedocs.io](https://openpiv-tk-gui.readthedocs.io/en/latest/index.html).


## Contribution <a id=contribution></a>

Contributions are very welcome! Please follow the [step by step guide in the documentation](https://openpiv-tk-gui.readthedocs.io/en/latest/contribution.html).

## Related

Also check out [JPIV](https://eguvep.github.io/jpiv/index.html).
