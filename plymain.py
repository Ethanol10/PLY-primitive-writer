import time
import numpy as np
import open3d as o3d
import tkinter
from tkinter import * 
from tkinter import messagebox
from os import listdir
from os.path import isfile, join


def main():

    #main frame
    top = tkinter.Tk()
    top.title("PLY/OBJ Mesher")
    top.resizable(width=False, height=False)
    top.geometry("640x500")

    #Entry for first text box
    loadMeshLabel = Label(top, text = "Load Mesh Path:")
    loadMeshLabel.place(x = 10, y = 10)
    loadMeshEntry = Entry(top, width = 84)
    loadMeshEntry.place(x = 120, y = 10)

    #Entry for Second text box
    outputMeshLabel = Label(top, text = "Ouput Folder Path:")
    outputMeshLabel.place(x = 10, y = 40)
    outputMeshEntry = Entry(top, width = 84)
    outputMeshEntry.place(x = 120, y = 40)

    #Frame for radio buttons for obj/ply options
    objRadioFrame = LabelFrame(top, text = "PLY/OBJ format")
    objRadioFrame.place(x = 10, y = 70, width = 620)

    option = IntVar()
    plyRadio = Radiobutton(objRadioFrame, text = "PLY", variable = option, value = 1)
    plyRadio.pack(anchor = W)
    objRadio = Radiobutton(objRadioFrame, text = "OBJ", variable = option, value = 2)
    objRadio.pack(anchor = W)

    #Button Frames
    buttonFrame = LabelFrame(top, text = "Actions")
    buttonFrame.place(x = 10, y = 150, width = 620)

    def generateBtnCallback():
        if loadMeshEntry.get() == "":
            messagebox.showwarning( title = "Empty Input error", message = "You need to specify an input")
            text.insert(INSERT, "\nSpecify an input folder", foreground = "red")
            return
        if outputMeshEntry.get() == "":
            messagebox.showwarning( title = "Empty Ouput error", message = "You need to specify an output")
            text.insert(INSERT, "\nSpecify an output folder", foreground = "red")
            return
        if option == IntVar():
            messagebox.showwarning( title = "Option Error", message = "You need to specify a format")
            text.insert(INSERT, "\nSpecify a output format", foreground = "red")
            return

        genMeshFromPointCloud(loadMeshEntry.get(), outputMeshEntry.get(), option, text)

    chooseInputPathBtn = Button(buttonFrame, text = "Choose Input Folder", width = 17)
    chooseInputPathBtn.pack( padx = 10, pady = 10, anchor = W )
    chooseOutputPathBtn = Button(buttonFrame, text = "Choose Ouput Folder", width = 17)
    chooseOutputPathBtn.pack( padx = 10, pady = 5, anchor = W )
    generateBtn = Button(buttonFrame, text = "Generate Meshes", width = 17, command = generateBtnCallback)
    generateBtn.pack( padx = 10, pady = 10, anchor = W)

    #Progress Text
    textLabel = Label(top, text = "Progress")
    textLabel.place(x = 10, y = 310)
    text = Text(top, state = DISABLED)
    scroll_y = Scrollbar(top, orient = "vertical", command=text.yview)
    scroll_y.place(x = 613, y = 330, height = 150)
    text.configure(yscrollcommand = scroll_y.set)
    text.insert(INSERT, "Ready for operation")
    text.place(x = 10, y = 330, width = 603, height = 150)

    top.mainloop()

def genMeshFromPointCloud(sourceStr, outputfolderStr, option, text):
    onlyfiles = [f for f in listdir(sourceStr) if isfile(join(sourceStr, f))]

    for i in onlyfiles:
        pcd = o3d.io.read_point_cloud("./input/" + i, format = 'ply')
        text.insert(INSERT, "\nworking on: " + i)
        text.insert(INSERT, "\n0% - Starting voxel downsampling of " + i)
        downpcd = pcd.voxel_down_sample(voxel_size=0.001)
        text.insert(INSERT, "\nEstimating normals of " + i )
        downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        text.insert(INSERT, "\nComputing convex hull" + i)
        downpcd.compute_convex_hull()
        text.insert(INSERT, "\n20% - Computed convex hull for" + i)

        text.insert(INSERT, "\nComputing nearest neighbour distance for " + i)
        distances = downpcd.compute_nearest_neighbor_distance()
        text.insert(INSERT, "\n30% - Calculating average distance for" + i)
        avg_dist = np.mean(distances)
        text.insert(INSERT, "\nCalculating average distance for" + i)
        radius = 3 * avg_dist
        text.insert(INSERT, "\n50% Performing Ball Pivoting Algorithm for" + i)
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(downpcd, o3d.utility.DoubleVector([radius, radius * 2]))

        #Retry with poisson disk
        text.insert(INSERT, "\n70% - Performing Poisson disk sampling on mesh for " + i)
        pcd = mesh.sample_points_poisson_disk(100000)
        downpcd = pcd.voxel_down_sample(voxel_size=0.001)
        downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        downpcd.compute_convex_hull()
        distances = downpcd.compute_nearest_neighbor_distance()
        avg_dist = np.mean(distances)
        radius = 3 * avg_dist 
        text.insert(INSERT, "\n90% - Performing 2nd pass for BPA on" + i)
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(downpcd, o3d.utility.DoubleVector([radius, radius * 2]))
        #o3d.visualization.draw_geometries([mesh])
        if option == 1:
            outputFileName = i.split(".")
            o3d.io.write_triangle_mesh(outputfolderStr + outputFileName[0] + ".ply", mesh)
            text.insert(INSERT, "\n100% - Mesh generated for " + i)
        elif option == 2:
            outputFileName = i.split(".")
            o3d.io.write_triangle_mesh(outputfolderStr + outputFileName[0] + ".obj", mesh)
            text.insert(INSERT, "\n100% - Mesh generated for " + i)
    
    time.sleep(1)


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