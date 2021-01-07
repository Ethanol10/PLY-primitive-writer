import os
import time
import inspect
import time
import numpy as np
import open3d as o3d
import threading
import meshlabxml as mlx
import tooltip as tt
from tkinter import * 
from tkinter import messagebox
from tkinter import filedialog
from os import listdir
from os.path import isfile, join

precomputedMeshes = []
currentlyRunning = False
THIS_SCRIPTPATH = os.path.dirname(
    os.path.realpath(inspect.getsourcefile(lambda: 0)))

def main():
    root = Tk()
    root.iconbitmap('icon.ico')
    app = MainGUIThread(root)

class MainGUIThread():
    def __init__(self, root):
        paddx = 10
        paddy = 10
        super().__init__()
        self = root
        self.title("PLY/OBJ Mesher")
        self.resizable(width = False, height = False)
        holemaxsize = StringVar()
        radius = StringVar()
        maxnn = StringVar()
        psamples = StringVar()
        passVar = StringVar()
        radiusModVar = StringVar()

        def browseInput():
            filename = filedialog.askdirectory()
            if filename:
                inputFolder.set(filename)

        def browseOutput():
            filename = filedialog.askdirectory()
            if filename:
                outputFolder.set(filename)

        def calculateMeanRadCallback():
            if loadMeshEntry.get() == "":
                messagebox.showwarning( title = "Empty Input error", message = "You need to specify an input")
                text.insert(INSERT, "\nSpecify an input folder")
                return

            radiusMean(loadMeshEntry.get(), text)
        
        def generateBtnCallback():
            holemaxResult = DoubleVar()
            radiusResult = DoubleVar()
            maxnnResult = DoubleVar()
            psamplesResult = DoubleVar()
            passResult = IntVar()
            if loadMeshEntry.get() == "":
                messagebox.showwarning( title = "Empty Input error", message = "You need to specify an input")
                text.insert(INSERT, "\nSpecify an input folder")
                return
            if outputMeshEntry.get() == "":
                messagebox.showwarning( title = "Empty Ouput error", message = "You need to specify an output")
                text.insert(INSERT, "\nSpecify an output folder")
                return
            if option == IntVar():
                messagebox.showwarning( title = "Option Error", message = "You need to specify a format")
                text.insert(INSERT, "\nSpecify a output format")
                return
            try:
                holemaxResult = int(holemaxsize.get())
                radiusResult = float(radius.get())
                maxnnResult = int(maxnn.get())
                psamplesResult = float(psamples.get())
                psamplesResult = int(psamplesResult)
                passResult = int(passVar.get())
                radModResult = float(radiusModVar.get())
            except TypeError:
                messagebox.showwarning(title = "Value Error", message = "One of your parameters is not a number, please check and try again")        
                text.insert(INSERT, "\nRecheck mesh parameters")
                return        

            #startGenerating(loadMeshEntry.get(), outputMeshEntry.get(), option.get(), text)
            text.insert(INSERT, "\nThis process will take awhile, and as such, the program may seem to freeze but it will still be running in the background. \nPlease be patient.")
            meshGenThread = meshGen(loadMeshEntry.get(), outputMeshEntry.get(), option.get(), holemaxResult, radiusResult, maxnnResult, psamplesResult, text, passResult, radModResult)
            meshGenThread.start()

        #sets the default parameters 
        def setDefaultParam():
            holemaxsize.set("30")
            radius.set("0")
            maxnn.set("30")
            psamples.set("100000")
            passVar.set('1')
            radiusModVar.set('0.5')
        
        #Clear all mesh results computed before.
        def clearResults():
            msgBox = messagebox.askquestion(title="Delete all precomputed meshes", message = "Do you wish to delete all computed meshes? You will not be able to recover these results! (Note this will not delete all meshes from the output folder.)")
            if msgBox == 'yes':
                precomputedMeshes = []
            
        #Opens another window that handles the meshes that have been generated before.
        def openResults():
            window = Toplevel(root)
            window.title("Precomputed Meshes")
            window.iconbitmap('icon.ico')
            def viewMesh(lb):
                o3d.visualization.draw_geometries([precomputedMeshes[lb.curselection()[0]].getMesh()])            
        
            def deleteMesh(lb):
                precomputedMeshes.remove(precomputedMeshes[lb.curselection()[0]])
                lb.delete(lb.curselection()[0])

            #Listbox
            meshListBox = Listbox(window)
            #add list adding function
            i = 0
            for meshOb in precomputedMeshes:
                meshListBox.insert(i, meshOb.getName())

            meshListBox.pack(side = LEFT, padx = paddx, pady = paddy/4)

            #Button Options  
            buttonFrame = LabelFrame(window, text = "Mesh Actions")
            buttonFrame.pack(side = LEFT, padx = paddx, pady = paddy/4)
            viewButton = Button(buttonFrame, text="View selected mesh", width = 17, command= lambda : viewMesh(meshListBox))
            viewButton.pack(side = TOP, padx = paddx, pady = paddy/2)
            deleteButton = Button(buttonFrame, text="Delete Selected mesh", width = 17, command= lambda : deleteMesh(meshListBox))
            deleteButton.pack(side = TOP, padx = paddx, pady = paddy/2)

        setDefaultParam()
        
        #MenuBar
        menubar = Menu(self)
        optionMenu = Menu(menubar, tearoff = 0)
        optionMenu.add_command(label = "View precomputed meshes", command = openResults)
        optionMenu.add_command(label = "Delete all precomputed meshes", command=clearResults)
        menubar.add_cascade(label = "Options", menu=optionMenu )

        #Paths Label Frame
        paths = LabelFrame(self, text = "Path Location")

        inputFrame = Frame(paths)
        inputFrame.pack(side = TOP, padx = paddx, pady = paddy/4)
        inputFolder = StringVar()
        loadMeshLabel = Label(inputFrame, text = "Load Mesh Path:")
        loadMeshLabel.pack(side =LEFT, padx = paddx, pady = paddy/2, anchor = W)
        loadMeshEntry = Entry(inputFrame, width = 40, textvariable = inputFolder)
        loadMeshEntry.pack(side = RIGHT, padx = paddx, pady = paddy/2, anchor = E)
        
        outputFrame = Frame(paths)
        outputFrame.pack(side = TOP, padx = paddx, pady = paddy/4)
        outputFolder = StringVar()
        outputMeshLabel = Label(outputFrame, text = "Ouput Folder Path:")
        outputMeshLabel.pack(side = LEFT, padx = paddx, pady = paddy/2, anchor = W)
        outputMeshEntry = Entry(outputFrame, width = 40, textvariable = outputFolder)
        outputMeshEntry.pack(side = RIGHT, padx = paddx, pady = paddy/2, anchor = E)

        paths.pack(padx = paddx, pady = paddy/2, fill = "x")

        outputOptionsFrame = LabelFrame(self, text = "Output Parameters")
        outputOptionsFrame.pack(padx = paddx, pady = paddy/2, fill = "x")

        #Output Format label frame
        outputFormatLFrame = LabelFrame(outputOptionsFrame, text = "Output Format")

        option = IntVar()
        plyRadio = Radiobutton(outputFormatLFrame, text = "PLY", variable = option, value = 1)
        plyRadio.pack()
        objRadio = Radiobutton(outputFormatLFrame, text = "OBJ", variable = option, value = 2)
        objRadio.pack()

        outputFormatLFrame.pack(padx = paddx, pady = paddy/2, side = LEFT)

        #Parameter GUI
        parameterLFrame = LabelFrame(outputOptionsFrame, text = "Mesh Generation Parameters")

        labelFrame = Frame(parameterLFrame)
        labelFrame.pack(side = LEFT, padx = paddx/2, pady = paddy/2)
        entryFrame = Frame(parameterLFrame)
        entryFrame.pack(side = LEFT, padx = paddx/2, pady = paddy/2)
    
        holemaxLabel = Label(labelFrame, text = "Close Hole Max Size:")
        holemaxLabel.pack(padx = paddx, pady = paddy/2, anchor =W)
        tt.CreateToolTip(holemaxLabel, "Specifies how the max size of a hole that should be patched in the mesh.")
        holemaxEntry = Entry(entryFrame, width = 20, textvariable = holemaxsize)
        holemaxEntry.pack(padx = paddx, pady = paddy/2)

        radiusLabel = Label(labelFrame, text = "Radius:")
        radiusLabel.pack(padx = paddx, pady = paddy/2, anchor =W)
        tt.CreateToolTip(radiusLabel, "Specifies the search radius when estimating normals.\nA larger radius means a broader search will be conducted to estimate the normals.\nHowever, this also means it will take longer to compute. \nSet to 0 to let MeshLab Auto Guess.")
        radiusEntry = Entry(entryFrame, width = 20, textvariable = radius)
        radiusEntry.pack(padx = paddx, pady = paddy/2)

        maxnnLabel = Label(labelFrame, text = "Max Nearest Neighbours:" )
        maxnnLabel.pack(padx = paddx, pady = paddy/2, anchor =W)
        tt.CreateToolTip(maxnnLabel, "The upper limit for how many neighbours should be considered when computing normals for each point.\nThis will take up more computational power the higher the value is set.")
        maxnnEntry = Entry(entryFrame, width = 20, textvariable = maxnn)
        maxnnEntry.pack(padx = paddx, pady = paddy/2)

        poissonSampleLabel = Label(labelFrame, text = "No. of Poisson Samples: ")
        poissonSampleLabel.pack(padx = paddx, pady = paddy/2, anchor =W)
        tt.CreateToolTip(poissonSampleLabel, "The number of points to sample out of a mesh.\nEach point that is sampled using this method is made to approximately be spaced evenly from each other.\nThe higher the number, the more detailed the mesh should be, in exchange for slower computational time. ")
        poissonSampleEntry = Entry(entryFrame, width = 20, textvariable= psamples)
        poissonSampleEntry.pack(padx = paddx, pady = paddy/2, anchor =W)

        passLabel = Label(labelFrame,text = "No. of Extra Passes:")
        passLabel.pack(padx = paddx, pady = paddy, anchor =W)
        tt.CreateToolTip(passLabel, "Number of passes the point cloud should undergo when processing. \nEach extra pass increases the computation time.")
        choices = ["0", "1", "2", "3", "4", "5"]
        passMenu = OptionMenu(entryFrame, passVar, *choices)
        passMenu.pack(padx = paddx, pady = paddy/2, anchor=W)

        radiusModLabel = Label(labelFrame, text = "Radius Modifier per Pass")
        radiusModLabel.pack(padx = paddx, pady = paddy, anchor=W )
        tt.CreateToolTip(radiusModLabel, "The multiplier that the radius is modified by for every pass that is completed. \nFor Example: if the first pass has a radius of 1, and the modifier is 0.5, \nthe next pass will use a 0.5 radius, and the third pass will use a 0.25 radius.")
        radiusModEntry = Entry(entryFrame, width = 20, textvariable= radiusModVar)
        radiusModEntry.pack(padx = paddx, pady = paddy/2, anchor=W)

        parameterLFrame.pack(side = LEFT, padx = paddx, pady = paddy)

        #button output combo frame
        buttonandoutputFrame = Frame(self)
        buttonandoutputFrame.pack()
        #button Label Frame
        buttonLFrame = LabelFrame(buttonandoutputFrame, text = "Actions")

        chooseInputPathBtn = Button(buttonLFrame, text = "Choose Input Folder", width = 17, command = browseInput)
        chooseInputPathBtn.pack( padx = paddx, pady = paddy/2, anchor = W )
        chooseOutputPathBtn = Button(buttonLFrame, text = "Choose Ouput Folder", width = 17, command = browseOutput)
        chooseOutputPathBtn.pack( padx = paddx, pady = paddy/2, anchor = W )
        setDefaultParamBtn = Button(buttonLFrame, text = "Set Default Parameters", width = 17, command = setDefaultParam )
        setDefaultParamBtn.pack( padx = paddx, pady = paddy/2, anchor = W)
        calcMeanRadBtn = Button(buttonLFrame, text = "Calculate Mean Radius", width = 17, command = calculateMeanRadCallback )
        tt.CreateToolTip(calcMeanRadBtn, "This button tries to calculate an appropriate radius for the mesh, \nHOWEVER this is very inaccurate when used with multiple meshes of greatly varying size, so use with caution! ")
        calcMeanRadBtn.pack(padx = paddx, pady = paddy/2, anchor =W)
        generateBtn = Button(buttonLFrame, text = "Generate Meshes", width = 17, command = generateBtnCallback)
        generateBtn.pack( padx = paddx, pady = paddy/2, anchor = W)
        

        buttonLFrame.pack(padx = paddx, pady = paddy/2, side = LEFT, fill = "y")

        #output frame
        outputFrame = Frame(buttonandoutputFrame)
        text = Text(outputFrame, width = 35, height = 10)
        scroll_y = Scrollbar(outputFrame, orient = "vertical", command=text.yview)
        text.configure(yscrollcommand = scroll_y.set)
        text.insert(INSERT, "Ready for operation")
        text.pack(side = LEFT, pady = paddy)
        scroll_y.pack(side =LEFT, fill="y", expand =False, pady = paddy)
        outputFrame.pack(padx = paddx, pady = paddy/2, side = LEFT)

        root.config(menu = menubar)
        root.mainloop()

class meshGen(threading.Thread):
    def __init__(self, sourceStr, outputfolderStr, option, holemax, radius, maxnn, psamples, text, passNo, radMod):
        threading.Thread.__init__(self)
        self.sourceStr = sourceStr
        self.outputFolderStr = outputfolderStr
        self.option = option
        self.holemax = holemax
        self.radius = radius
        self.maxnn = maxnn
        self.text = text
        self.psamples = psamples
        self.passNo = passNo
        self.radMod = radMod
    def run(self):
        startGenerating(self.sourceStr, self.outputFolderStr, self.option, self.holemax, self.radius, self.maxnn, self.psamples, self.text, self.passNo, self.radMod)
        self.text.insert(INSERT, "\nAll Meshes completely converted." + "\n")
        messagebox.showinfo(title = "Mesh Generation", message = "All meshes generated successfully.")
        self.text.see("end")

def startGenerating(sourceStr, outputfolderStr, option, holemax, radius, maxnn, psamples, text, passNo, radMod):
    threads = []
    onlyfiles = [f for f in listdir(sourceStr) if isfile(join(sourceStr, f))]
    for i in onlyfiles:
        # thread = threading.Thread(target=genMeshFromPointCloud, args=[sourceStr, outputfolderStr, option, voxel, radius, maxnn, psamples, text, i])
        # threads.append(thread)
        # thread.start()
        genMeshFromPointCloud(sourceStr, outputfolderStr, option, holemax, radius, maxnn, psamples, text, i, passNo, radMod)
    # for thread in threads:
    #     thread.join()

def genMeshFromPointCloud(sourceStr, outputfolderStr, option, holemax, inpRad, maxnn, psamples, text, filename, passNo, radMod):
    #Initial setup for generating meshes
    os.chdir(THIS_SCRIPTPATH)
    #ml_version = '1.3.4BETA'
    ml_version = '2016.12'
    # Add meshlabserver directory to OS PATH; omit this if it is already in
    # your PATH
    #meshlabserver_path = 'C:\\Program Files\\VCG\\MeshLab'
    #"""
    if ml_version == '1.3.4BETA':
        meshlabserver_path = 'C:\Program Files\VCG\MeshLab'
    elif ml_version == '2016.12':
        meshlabserver_path = 'C:/Program Files/VCG/MeshLab'
    #"""
    os.environ['PATH'] = meshlabserver_path + os.pathsep 
    outputFileName = filename.split(".")
    texGenScript = None
    #start of script
    if option == 1:
        texGenScript = mlx.FilterScript(file_in=sourceStr + "/" + outputFileName[0] + ".ply", file_out= outputfolderStr + "/" + outputFileName[0] + ".ply", ml_version=ml_version)
    elif option == 2:
        texGenScript = mlx.FilterScript(file_in=sourceStr + "/" + outputFileName[0] + ".ply", file_out= outputfolderStr + "/" + outputFileName[0] + ".obj", ml_version = ml_version)
    #generate normals, get sampling and ball pivot as much as user desires.
    mlx.normals.point_sets(texGenScript, neighbors=maxnn)
    mlx.sampling.poisson_disk(texGenScript, sample_num=psamples, subsample=True)
    # mlx.layers.delete(texGenScript, layer_num=None)
    if passNo == 0:
        mlx.remesh.ball_pivoting(texGenScript, ball_radius=inpRad, delete_faces=False)
    else: 
        mlx.remesh.ball_pivoting(texGenScript, ball_radius=inpRad, delete_faces=False)

    #The subsequent commands are optional if 0 is the input radius.
    modiRad = inpRad
    if passNo != 0 and inpRad != 0:
        #Subsequent passes must reduce inpRad by a user factor.
        modiRad = modiRad / radMod
        for i in range(0, passNo):
            mlx.remesh.ball_pivoting(texGenScript, ball_radius=modiRad, delete_faces=False)
            modiRad = modiRad / radMod
    mlx.clean.close_holes(texGenScript, hole_max_edge=holemax)
    mlx.delete.duplicate_faces(texGenScript)

    if option == 1:
        outputMask = mlx.default_output_mask(outputFileName[0] + ".ply", vert_colors= True, face_colors= True)
        texGenScript.run_script(output_mask=outputMask)
        mesh = o3d.io.read_triangle_mesh(outputfolderStr + "/" + outputFileName[0] + ".ply")
        meshOb = meshObj(mesh, outputFileName)
        precomputedMeshes.append(meshOb)
    elif option == 2:
        outputMask = mlx.default_output_mask(outputFileName[0] + ".obj", vert_colors= True, face_colors= True)
        texGenScript.run_script(output_mask=outputMask)

        textureScript = mlx.FilterScript(file_in=outputfolderStr + "/" + outputFileName[0] + ".obj", file_out= outputfolderStr + "/" + outputFileName[0] + ".obj", ml_version = ml_version)
        mlx.texture.per_triangle(textureScript, sidedim = 0, textdim = 4096, border = 0.01, method = 1)
        mlx.transfer.vc2tex(textureScript, tex_name=outputFileName[0] + ".png", tex_width=4096, tex_height=4096, assign_tex=True, fill_tex=True)
        textureScript.run_script()
        mesh = o3d.io.read_triangle_mesh(outputfolderStr + "/" + outputFileName[0] + ".obj")
        meshOb = meshObj(mesh, outputFileName)
        precomputedMeshes.append(meshOb)

def radiusMean(sourceStr, text):
    onlyfiles = [f for f in listdir(sourceStr) if isfile(join(sourceStr, f))]
    totalmesh = 0
    totalRad = 0.0
    for i in onlyfiles:
        totalmesh += 1
        totalRad += checkDistance(sourceStr, i)
    
    messagebox.showinfo(title = "Mesh Average Radius", message = "Average Radius between all inputted meshes is " + str(totalRad))
    text.insert(INSERT, "\nAverage Radius between all inputted meshes is " + str(totalRad))
    text.see("end")

def checkDistance(sourceStr, filename):
    pcd = o3d.io.read_point_cloud(sourceStr + "/" + filename, format = 'ply')
    measurementpcd = pcd.compute_nearest_neighbor_distance()
    return np.mean(measurementpcd)

class meshObj():
    def __init__(self, mesh, name):
        self.mesh = mesh
        self.name = name
    
    def getMesh(self):
        return self.mesh

    def getName(self):
        return self.name

if __name__ == "__main__":
    main()