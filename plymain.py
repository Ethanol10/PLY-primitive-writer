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
        voxelsize = StringVar()
        radius = StringVar()
        maxnn = StringVar()
        psamples = StringVar()

        def browseInput():
            filename = filedialog.askdirectory()
            if filename:
                inputFolder.set(filename)

        def browseOutput():
            filename = filedialog.askdirectory()
            if filename:
                outputFolder.set(filename)
        
        def generateBtnCallback():
            voxelResult = DoubleVar()
            radiusResult = DoubleVar()
            maxnnResult = DoubleVar()
            psamplesResult = DoubleVar()
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
                voxelResult = float(voxelsize.get())
                radiusResult = float(radius.get())
                maxnnResult = float(maxnn.get())
                psamplesResult = float(psamples.get())
                psamplesResult = int(psamplesResult)
            except TypeError:
                messagebox.showwarning(title = "Value Error", message = "One of your parameters is not a number, please check and try again")        
                text.insert(INSERT, "\nRecheck mesh parameters")
                return        

            #startGenerating(loadMeshEntry.get(), outputMeshEntry.get(), option.get(), text)
            text.insert(INSERT, "\nThis process will take awhile, and as such, the program may seem to freeze but it will still be running in the background. \nPlease be patient.")
            meshGenThread = meshGen(loadMeshEntry.get(), outputMeshEntry.get(), option.get(), voxelResult, radiusResult, maxnnResult, psamplesResult, text)
            meshGenThread.start()

        #sets the default parameters 
        def setDefaultParam():
            voxelsize.set("0.0001")
            radius.set("0.1")
            maxnn.set("30")
            psamples.set("100000")
        
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
    
        voxelSizeLabel = Label(labelFrame, text = "Voxel Size:")
        voxelSizeLabel.pack(padx = paddx, pady = paddy/2, anchor =W )
        tt.CreateToolTip(voxelSizeLabel, "This buckes all points into voxels, \nand gets a singular point for each voxel representing the bucket of points.\nChanging the voxel size controls how simplified the model should be.")
        voxelSizeEntry = Entry(entryFrame, width = 20, textvariable = voxelsize)
        voxelSizeEntry.pack(padx = paddx, pady = paddy/2)

        radiusLabel = Label(labelFrame, text = "Radius:")
        radiusLabel.pack(padx = paddx, pady = paddy/2, anchor =W)
        tt.CreateToolTip(radiusLabel, "Specifies the search radius when estimating normals.\nA larger radius means a broader search will be conducted to estimate the normals.\nHowever, this also means it will take longer to compute.")
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
    def __init__(self, sourceStr, outputfolderStr, option, voxel, radius, maxnn, psamples, text):
        threading.Thread.__init__(self)
        self.sourceStr = sourceStr
        self.outputFolderStr = outputfolderStr
        self.option = option
        self.voxel = voxel
        self.radius = radius
        self.maxnn = maxnn
        self.text = text
        self.psamples = psamples
    def run(self):
        startGenerating(self.sourceStr, self.outputFolderStr, self.option, self.voxel, self.radius, self.maxnn, self.psamples, self.text)
        self.text.insert(INSERT, "\nAll Meshes completely converted." + "\n")
        messagebox.showinfo(title = "Mesh Generation", message = "All meshes generated successfully.")
        self.text.see("end")

def startGenerating(sourceStr, outputfolderStr, option, voxel, radius, maxnn, psamples, text):
    threads = []
    onlyfiles = [f for f in listdir(sourceStr) if isfile(join(sourceStr, f))]
    for i in onlyfiles:
        thread = threading.Thread(target=genMeshFromPointCloud, args=[sourceStr, outputfolderStr, option, voxel, radius, maxnn, psamples, text, i])
        threads.append(thread)
        thread.start()
        # genMeshFromPointCloud(sourceStr, outputfolderStr, option, voxel, radius, maxnn, psamples, text, i)
    for thread in threads:
        thread.join()

def genMeshFromPointCloud(sourceStr, outputfolderStr, option, voxel, inpRad, maxnn, psamples, text, filename):
    start_time = time.time()
    text.insert(INSERT, "\n")
    pcd = o3d.io.read_point_cloud(sourceStr + "/" + filename, format = 'ply')
    text.insert(INSERT, "\nworking on: " + filename)
    text.insert(INSERT, "\n0% - Starting voxel downsampling of " + filename + " " + time.ctime() + "\n")
    downpcd = pcd.voxel_down_sample(voxel_size=voxel)
    text.insert(INSERT, "\nEstimating normals of " + filename + " " + time.ctime()+ "\n")
    downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius= inpRad, max_nn=int(maxnn)))
    text.insert(INSERT, "\nComputing convex hull" + filename + " "  + time.ctime()+ "\n")
    downpcd.compute_convex_hull()
    text.insert(INSERT, "\n20% - Computed convex hull for " + filename + " "  + time.ctime()+ "\n")
    text.see("end")
    
    text.insert(INSERT, "\nComputing nearest neighbour distance for " + filename + " " + time.ctime()+ "\n")
    text.see("end")
    distances = downpcd.compute_nearest_neighbor_distance()
    text.insert(INSERT, "\n30% - Calculating average distance for " + filename + " "  + time.ctime()+ "\n")
    text.see("end")
    avg_dist = np.mean(distances)
    text.insert(INSERT, "\nCalculating average distance for " + filename + " "  + time.ctime()+ "\n")
    text.see("end")
    radius = 3 * avg_dist
    text.insert(INSERT, "\n50% Performing Ball Pivoting Algorithm for " + filename + " "  + time.ctime()+ "\n")
    text.see("end")
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(downpcd, o3d.utility.DoubleVector([radius, radius * 2]))

    #Retry with poisson disk
    text.insert(INSERT, "\n70% - Performing Poisson disk sampling on mesh for " + filename + " "  + time.ctime()+ "\n")
    text.see("end")
    pcd = mesh.sample_points_poisson_disk(int(psamples))
    downpcd = pcd.voxel_down_sample(voxel_size=voxel)
    downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=inpRad, max_nn=int(maxnn)))
    downpcd.compute_convex_hull()
    distances = downpcd.compute_nearest_neighbor_distance()
    avg_dist = np.mean(distances)
    radius = 3 * avg_dist 
    text.insert(INSERT, "\n90% - Performing 2nd pass for BPA on " + filename + " "  + time.ctime()+ "\n")
    text.see("end")
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(downpcd, o3d.utility.DoubleVector([radius, radius * 2]))
    # def showMesh(inpMesh):
    #     o3d.visualization.draw_geometries([inpMesh])
    # o3dwindow = threading.Thread(target = showMesh, args= [mesh])
    # o3dwindow.start()

    if option == 1:
        outputFileName = filename.split(".")
        o3d.io.write_triangle_mesh(outputfolderStr + "/" + outputFileName[0] + ".ply", mesh)
        text.insert(INSERT, "\n100% - Mesh generated for " + filename + " "  + time.ctime())
        meshOb = meshObj(mesh, outputFileName )
        precomputedMeshes.append(meshOb)
    elif option == 2:
        outputFileName = filename.split(".")
        o3d.io.write_triangle_mesh(outputfolderStr + "/" + outputFileName[0] + ".obj", mesh)
        objTexGen(outputFileName[0], outputfolderStr, text, filename)
        text.insert(INSERT, "\n100% - Mesh generated for " + filename + " "  + time.ctime()+ "\n")
        text.see("end")
        meshOb = meshObj(mesh, outputFileName)
        precomputedMeshes.append(meshOb)

def objTexGen(fileOutputName, outputPath, text, filename):
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
    text.insert(INSERT, "\n95% - Generating Texture file for requested OBJ output on " + filename + " "  + time.ctime()+ "\n")
    text.see("end")
    texGenScript = mlx.FilterScript(file_in=outputPath + "/" + fileOutputName + ".obj", file_out= outputPath + "/" + fileOutputName + ".obj", ml_version=ml_version)
    mlx.texture.per_triangle(texGenScript, sidedim = 0, textdim = 4096, border = 0.01, method = 1)
    mlx.transfer.vc2tex(texGenScript, tex_name=fileOutputName + ".png", tex_width=4096, tex_height=4096, assign_tex=True, fill_tex=True)
    texGenScript.run_script()

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