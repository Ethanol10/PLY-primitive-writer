import time

#Main

def main():
    print("This program is designed to generate a primitive object in a PLY format\nType 'x!' at any text prompt to end the program.")
    time.sleep(1)
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
                depth = wxheight
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
    
    write_to_file_cube(comment, depth, width, height, typeOfObject)



def write_to_file_cube(comment, depth, width, height, typeOfObject):
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