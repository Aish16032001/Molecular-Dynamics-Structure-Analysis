# Molecular-Dynamics-Structure-Analysis

# Introduction: 
Molecular dynamics (MD) simulations in computational materials research can produce large data sets with hundreds of frames. Converging difficult structures and researching material attributes require the analysis of these frames in order to extract useful information, such as particular bond lengths or atomic locations. However, manually sorting through MD datasets can be a laborious and error-prone procedure. In order to overcome these obstacles, I have created a Python script that improves and automates MD frame analysis by utilizing the pymatgen module.

# Overview of the Script:
1.	Splitting MD Frames into Separate Files:
       * Molecular dynamics trajectory files can be processed by the script, which will then divide them into distinct frames, each of which will be saved as a different file. 
2.	Searching for Frames to get specific bond length : 
       * Users can define a target bond length, and the script will scan all frames to identify those that meet the specified criteria.The identified frames are extracted and saved for 
         further use in downstream applications.
         
