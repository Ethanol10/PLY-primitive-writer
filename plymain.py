import time
import numpy as np
import open3d as o3d
import trimesh as triM
from os import listdir
from os.path import isfile, join


def main():
    print("This program is designed to generate a mesh from a set of points known as a point cloud")
    print("This program can also generate primitive objects in a PLY format.")
    print("Type x! at any prompt to end the program")
    print("Press 1 to generate a primitive PLY object.")
    
    option = ""
    loopBreak = False
    while not loopBreak:
        try:
            option = input("Press 2 to attempt to perform three operations on a point cloud (Poisson Disk Sampling, Computing normals for point sets, Ball Pivoting Algorithm):")
            if option == "x!":
                exit()
            elif int(option) > 2 or int(option) < 1:
                print("Invalid Number")
                loopBreak = False
            else:
                option = int(option)
                loopBreak = True
        except ValueError:
            print("Invalid Number") 
            loopBreak = False
    
    if option == 1:
        createPrimitive()
    elif option == 2:
        genMeshFromPointCloud()    

def genMeshFromPointCloud():
    print("Attempting to create a mesh from a point cloud.")
    print("Place your point clouds in the folder named 'input' in the directory where this program is located.")
    print("Your successfully generated mesh will be in a 'output' folder after all processes are complete.")
    userInput = input("type 'ready' when your files are ready to be converted. Type anything else to exit the program: ")
    
    if userInput != "ready":
        exit()  

    onlyfiles = [f for f in listdir("./input/") if isfile(join("./input/", f))]

    for i in onlyfiles:
        pcd = o3d.io.read_point_cloud("./input/" + i, format = 'ply')
        print("working on: " + i)
        downpcd = pcd.voxel_down_sample(voxel_size=0.001)
        downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        downpcd.compute_convex_hull()
        print(downpcd.has_normals())

        distances = downpcd.compute_nearest_neighbor_distance()
        avg_dist = np.mean(distances)
        radius = 3 * avg_dist
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(downpcd, o3d.utility.DoubleVector([radius, radius * 2]))

        #Retry with poisson disk
        pcd = mesh.sample_points_poisson_disk(100000)
        downpcd = pcd.voxel_down_sample(voxel_size=0.001)
        downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        downpcd.compute_convex_hull()
        distances = downpcd.compute_nearest_neighbor_distance()
        avg_dist = np.mean(distances)
        radius = 3 * avg_dist
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(downpcd, o3d.utility.DoubleVector([radius, radius * 2]))

        #tri_mesh = triM.Trimesh(np.asarray(mesh.vertices), np.asarray(mesh.triangles), vertex_normals=np.asarray(mesh.vertex_normals))
        #triM.convex.is_convex(tri_mesh)
        o3d.io.write_triangle_mesh("./output/" + i, mesh)

    print("Done, Terminating program.")
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