import os
import time
import inspect
import time
import numpy as np
import open3d as o3d
import threading
import meshlabxml as mlx
from tkinter import * 
from tkinter import messagebox
from tkinter import filedialog
from os import listdir
from os.path import isfile, join


THIS_SCRIPTPATH = os.path.dirname(
    os.path.realpath(inspect.getsourcefile(lambda: 0)))

def main():
    root = Tk()
    root.iconbitmap('icon.ico')
    app = GUIThread(root)

class GUIThread:
    def __init__(self, root):
        super().__init__()
        #main frame
        self = root
        self.title("PLY/OBJ Mesher")
        self.resizable(width=False, height=False)
        self.geometry("640x500")

        #Entry for first text box
        inputFolder = StringVar()
        loadMeshLabel = Label(self, text = "Load Mesh Path:")
        loadMeshLabel.place(x = 10, y = 10)
        loadMeshEntry = Entry(self, width = 84, textvariable = inputFolder)
        loadMeshEntry.place(x = 120, y = 10)

        #Entry for Second text box'
        outputFolder = StringVar()
        outputMeshLabel = Label(self, text = "Ouput Folder Path:")
        outputMeshLabel.place(x = 10, y = 40)
        outputMeshEntry = Entry(self, width = 84, textvariable = outputFolder)
        outputMeshEntry.place(x = 120, y = 40)

        def browseInput():
            filename = filedialog.askdirectory()
            if filename:
                inputFolder.set(filename)

        def browseOutput():
            filename = filedialog.askdirectory()
            if filename:
                outputFolder.set(filename)

        #Frame for radio buttons for obj/ply options
        objRadioFrame = LabelFrame(self, text = "PLY/OBJ format")
        objRadioFrame.place(x = 10, y = 70, width = 620)

        option = IntVar()
        plyRadio = Radiobutton(objRadioFrame, text = "PLY", variable = option, value = 1)
        plyRadio.pack(anchor = W)
        objRadio = Radiobutton(objRadioFrame, text = "OBJ", variable = option, value = 2)
        objRadio.pack(anchor = W)

        def generateBtnCallback():
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

            #startGenerating(loadMeshEntry.get(), outputMeshEntry.get(), option.get(), text)
            text.insert(INSERT, "\nThis process will take awhile, and as such, the program may seem to freeze but it will still be running in the background. \nPlease be patient.")
            meshGenThread = meshGen(loadMeshEntry.get(), outputMeshEntry.get(), option.get(), text)
            meshGenThread.start()

        #Button Frames
        buttonFrame = LabelFrame(self, text = "Actions")
        buttonFrame.place(x = 10, y = 150, width = 620)

        chooseInputPathBtn = Button(buttonFrame, text = "Choose Input Folder", width = 17, command = browseInput)
        chooseInputPathBtn.pack( padx = 10, pady = 10, anchor = W )
        chooseOutputPathBtn = Button(buttonFrame, text = "Choose Ouput Folder", width = 17, command = browseOutput)
        chooseOutputPathBtn.pack( padx = 10, pady = 5, anchor = W )
        generateBtn = Button(buttonFrame, text = "Generate Meshes", width = 17, command = generateBtnCallback)
        generateBtn.pack( padx = 10, pady = 10, anchor = W)

        #Progress Text
        textLabel = Label(self, text = "Progress")
        textLabel.place(x = 10, y = 310)
        text = Text(self)
        scroll_y = Scrollbar(self, orient = "vertical", command=text.yview)
        scroll_y.place(x = 613, y = 330, height = 150)
        text.configure(yscrollcommand = scroll_y.set)
        text.insert(INSERT, "Ready for operation")
        text.place(x = 10, y = 330, width = 603, height = 150)
        root.mainloop()

class meshGen(threading.Thread):
    def __init__(self, sourceStr, outputfolderStr, option, text):
        threading.Thread.__init__(self)
        self.sourceStr = sourceStr
        self.outputFolderStr = outputfolderStr
        self.option = option
        self.text = text
    def run(self):
        startGenerating(self.sourceStr, self.outputFolderStr, self.option, self.text)
        self.text.insert(INSERT, "\nAll Meshes completely converted.")
        messagebox.showinfo(title = "Mesh Generation", message = "All meshes generated successfully.")

# def main():

#     #main frame
#     top = tkinter.Tk()
#     top.title("PLY/OBJ Mesher")
#     top.resizable(width=False, height=False)
#     top.geometry("640x500")

#     #Entry for first text box
#     loadMeshLabel = Label(top, text = "Load Mesh Path:")
#     loadMeshLabel.place(x = 10, y = 10)
#     loadMeshEntry = Entry(top, width = 84)
#     loadMeshEntry.place(x = 120, y = 10)

#     #Entry for Second text box
#     outputMeshLabel = Label(top, text = "Ouput Folder Path:")
#     outputMeshLabel.place(x = 10, y = 40)
#     outputMeshEntry = Entry(top, width = 84)
#     outputMeshEntry.place(x = 120, y = 40)

#     #Frame for radio buttons for obj/ply options
#     objRadioFrame = LabelFrame(top, text = "PLY/OBJ format")
#     objRadioFrame.place(x = 10, y = 70, width = 620)

#     option = IntVar()
#     plyRadio = Radiobutton(objRadioFrame, text = "PLY", variable = option, value = 1)
#     plyRadio.pack(anchor = W)
#     objRadio = Radiobutton(objRadioFrame, text = "OBJ", variable = option, value = 2)
#     objRadio.pack(anchor = W)

#     #Button Frames
#     buttonFrame = LabelFrame(top, text = "Actions")
#     buttonFrame.place(x = 10, y = 150, width = 620)

#     def generateBtnCallback():
#         if loadMeshEntry.get() == "":
#             messagebox.showwarning( title = "Empty Input error", message = "You need to specify an input")
#             text.insert(INSERT, "\nSpecify an input folder")
#             return
#         if outputMeshEntry.get() == "":
#             messagebox.showwarning( title = "Empty Ouput error", message = "You need to specify an output")
#             text.insert(INSERT, "\nSpecify an output folder")
#             return
#         if option == IntVar():
#             messagebox.showwarning( title = "Option Error", message = "You need to specify a format")
#             text.insert(INSERT, "\nSpecify a output format")
#             return

#         startGenerating(loadMeshEntry.get(), outputMeshEntry.get(), option.get(), text)

#     chooseInputPathBtn = Button(buttonFrame, text = "Choose Input Folder", width = 17)
#     chooseInputPathBtn.pack( padx = 10, pady = 10, anchor = W )
#     chooseOutputPathBtn = Button(buttonFrame, text = "Choose Ouput Folder", width = 17)
#     chooseOutputPathBtn.pack( padx = 10, pady = 5, anchor = W )
#     generateBtn = Button(buttonFrame, text = "Generate Meshes", width = 17, command = generateBtnCallback)
#     generateBtn.pack( padx = 10, pady = 10, anchor = W)

#     #Progress Text
#     textLabel = Label(top, text = "Progress")
#     textLabel.place(x = 10, y = 310)
#     text = Text(top)
#     scroll_y = Scrollbar(top, orient = "vertical", command=text.yview)
#     scroll_y.place(x = 613, y = 330, height = 150)
#     text.configure(yscrollcommand = scroll_y.set)
#     text.insert(INSERT, "Ready for operation")
#     text.place(x = 10, y = 330, width = 603, height = 150)

#     top.mainloop()

def startGenerating(sourceStr, outputfolderStr, option, text):
    onlyfiles = [f for f in listdir(sourceStr) if isfile(join(sourceStr, f))]
    for i in onlyfiles:
        genMeshFromPointCloud(sourceStr, outputfolderStr, option, text, i)

def genMeshFromPointCloud(sourceStr, outputfolderStr, option, text, filename):
    start_time = time.time()
    text.insert(INSERT, "\n")
    pcd = o3d.io.read_point_cloud(sourceStr + "/" + filename, format = 'ply')
    text.insert(INSERT, "\nworking on: " + filename)
    text.insert(INSERT, "\n0% - Starting voxel downsampling of " + filename)
    downpcd = pcd.voxel_down_sample(voxel_size=0.001)
    text.insert(INSERT, "\nEstimating normals of " + filename )
    downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    text.insert(INSERT, "\nComputing convex hull" + filename)
    downpcd.compute_convex_hull()
    text.insert(INSERT, "\n20% - Computed convex hull for " + filename)

    text.insert(INSERT, "\nComputing nearest neighbour distance for " + filename)
    distances = downpcd.compute_nearest_neighbor_distance()
    text.insert(INSERT, "\n30% - Calculating average distance for " + filename)
    avg_dist = np.mean(distances)
    text.insert(INSERT, "\nCalculating average distance for " + filename)
    radius = 3 * avg_dist
    text.insert(INSERT, "\n50% Performing Ball Pivoting Algorithm for " + filename)
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(downpcd, o3d.utility.DoubleVector([radius, radius * 2]))

    #Retry with poisson disk
    text.insert(INSERT, "\n70% - Performing Poisson disk sampling on mesh for " + filename)
    pcd = mesh.sample_points_poisson_disk(100000)
    downpcd = pcd.voxel_down_sample(voxel_size=0.001)
    downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    downpcd.compute_convex_hull()
    distances = downpcd.compute_nearest_neighbor_distance()
    avg_dist = np.mean(distances)
    radius = 3 * avg_dist 
    text.insert(INSERT, "\n90% - Performing 2nd pass for BPA on " + filename)
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(downpcd, o3d.utility.DoubleVector([radius, radius * 2]))
    #o3d.visualization.draw_geometries([mesh])
    if option == 1:
        outputFileName = filename.split(".")
        o3d.io.write_triangle_mesh(outputfolderStr + "/" + outputFileName[0] + ".ply", mesh)
        text.insert(INSERT, "\n100% - Mesh generated for " + filename)
    elif option == 2:
        outputFileName = filename.split(".")
        o3d.io.write_triangle_mesh(outputfolderStr + "/" + outputFileName[0] + ".obj", mesh)
        objTexGen(outputFileName[0], outputfolderStr)
        text.insert(INSERT, "\n100% - Mesh generated for " + filename)

def objTexGen(fileOutputName, outputPath):
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

    texGenScript = mlx.FilterScript(file_in=outputPath + "/" + fileOutputName + ".obj", file_out= outputPath + "/" + fileOutputName + ".obj", ml_version=ml_version)
    mlx.texture.per_triangle(texGenScript, sidedim = 0, textdim = 4096, border = 0.01, method = 1)
    mlx.transfer.vc2tex(texGenScript, tex_name=fileOutputName + ".png", tex_width=4096, tex_height=4096, assign_tex=True, fill_tex=True)
    texGenScript.run_script()

#createPrimitive creates either a primitive of either a cube or a rectangular prism.
def createPrimitive():
    loopBreak = False
    width = 0
    height = 0
    depth = 0
    typeOfObject = ""
    #type of object
    while not loopBreak:
        try:
            typeOfObject = input("What object type? 1 for Cube, 2 for Rectanglular Prism: ")
            if typeOfObject == "x!":
                exit()
            elif int(typeOfObject) > 2 or int(typeOfObject) < 1:
                print("Invalid Number")
                loopBreak = False
            else:
                typeOfObject = int(typeOfObject)
                loopBreak = True
        except ValueError: 
            print("Invalid Number")
            loopBreak = False

    loopBreak = False
    #Get Length of cube
    while not loopBreak: 
        try:
            width = input("Width of the sides of the " + ("cube", "rectanglular prism")[typeOfObject == 2] + "?(please enter a number): ")
            if width == "x!":
                exit()
            width = float(width)

            if typeOfObject == 2:
                depth = input("Depth of the rectangle?: ")
                if depth == "x!":
                    exit()
                depth = float(depth)
                height = input("Height of the rectangle?: ")
                if height == "x!":
                    exit()
                height = float(height)
            else:
                depth = width
            loopBreak = True

        except ValueError:
            print("Invalid Number")
            time.sleep(2)
            loopBreak = False

    loopBreak = False
    comment = ""
    while not loopBreak:
        comment = input("File Name: ")
        if comment == "x!":
            exit()
        loopBreak = True
    
    writeToFileCube(comment, depth, width, height, typeOfObject)



def writeToFileCube(comment, depth, width, height, typeOfObject):
    print("Generating Cube PLY file")
    try:
        f = open( comment + ".ply", "x")
    except IOError:
        print("File already exists! Terminating program.")
        time.sleep(2)
        exit()
    
    f.write("ply\nformat ascii 1.0\ncomment ")
    f.write(("Rectangular Prism","Cube")[typeOfObject == 1] + "\n")
    f.write("element vertex 8\nproperty float x\nproperty float y\nproperty float z\n")
    f.write("element face 6\nproperty list uint8 int32 vertex_index\n")
    f.write("end_header\n")
    print("Writing vertex points")
    time.sleep(1)
    #write vertex points
    x = 0
    y = 0
    z = 0
    while z == 0 or y == 0 or x == 0:
        f.write((str(width), str(0))[x == 0] + " " + ((str(height), str(width))[typeOfObject == 1], str(0))[y == 0] + " " + ((str(depth), str(width))[typeOfObject == 1], str(0))[z == 0] + "\n")
        z += 1
        if z > 1:
            z = 0
            y += 1
            if y > 1:
                y = 0
                x += 1
    
    f.write( str(width) + " " + (str(height), str(width))[typeOfObject == 1] + " " + (str(depth), str(width))[typeOfObject == 1] + "\n")
    f.write("4 1 0 2 3\n4 5 4 6 7\n4 1 0 4 5\n4 3 2 6 7\n4 2 0 4 6\n4 3 1 5 7\n")
    f.close()

    print("Done. Program will now terminate.")
    time.sleep(1)

if __name__ == "__main__":
    main()