def teslapython_1():
    LRV = input("Enter the Lower Range Value (LRV): ")
    URV = input("Enter the Upper Range Value (URV): ")
    X = input("Enter the measured value (X): ")
    LRV = float(LRV)
    URV = float(URV)
    X = float(X)
    if LRV >= URV:
        raise ValueError("Lower Range Value must be less than Upper Range Value")
    if X < LRV or X > URV:
        raise ValueError("Measured value must be within the range defined by LRV and URV")
    if URV - LRV == 0:
        raise ValueError("Upper Range Value must be greater than Lower Range Value to avoid division by zero")
    if X == LRV:
        return 0.0
    if X == URV:
        return 100.0
    if X < LRV or X > URV:
        raise ValueError("Measured value must be within the range defined by LRV and URV")
    if LRV == URV:
        raise ValueError("Lower Range Value must be less than Upper Range Value to avoid division by zero")
   
    percentage = (X - LRV) / (URV - LRV) * 100

    Y = (percentage + 25) / 6.25

    print(Y, "mA")

#teslapython_1()

def teslapython_2():
    LRV = input("Enter the Lower Range Value (LRV): ")
    URV = input("Enter the Upper Range Value (URV): ")
    Y = input("Enter the 4-20mA signal (Y): ")
    LRV = float(LRV)
    URV = float(URV)
    Y = float(Y)
    if LRV >= URV:
        raise ValueError("Lower Range Value must be less than Upper Range Value")
    if Y < 4 or Y > 20:
        raise ValueError("Measured value must be within the range defined by 4 and 20")
    if URV - LRV == 0:
        raise ValueError("Upper Range Value must be greater than Lower Range Value to avoid division by zero")
    if Y == 4:
        return 0.0
    if Y == 20:
        return 100.0
    if LRV == URV:
        raise ValueError("Lower Range Value must be less than Upper Range Value to avoid division by zero")

    percentage = (Y*6.25)-25

    PV = (percentage * (URV - LRV) / 100) + LRV

    print(PV)

#teslapython_2()

def teslapython_3():
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import sys
    print(sys.path)

    img = mpimg.imread('/Users/khanh/Downloads/1.Source_codes/teslapython_pypi/teslapython/teslapython/pic1.png')
    imgplot = plt.imshow(img)
    plt.show()

def teslapython_4():
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import sys
    print(sys.path)

    img = mpimg.imread('/Users/khanh/Downloads/1.Source_codes/teslapython_pypi/teslapython/teslapython/SIL.png')
    imgplot = plt.imshow(img)
    plt.show()

def teslapython_5():
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import sys
    print(sys.path)

    img = mpimg.imread('/Users/khanh/Downloads/1.Source_codes/teslapython_pypi/teslapython/teslapython/pic2.png')
    imgplot = plt.imshow(img)
    
    plt.show()

def teslapython_6():
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import sys
    print(sys.path)

    img = mpimg.imread('/Users/khanh/Downloads/1.Source_codes/teslapython_pypi/teslapython/teslapython/pic3.png')
    imgplot = plt.imshow(img)
    
    plt.show()

def teslapython_7():
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import sys
    print(sys.path)

    img = mpimg.imread('/Users/khanh/Downloads/1.Source_codes/teslapython_pypi/teslapython/teslapython/pic4.png')
    imgplot = plt.imshow(img)
    
    plt.show()

def teslapython_8():
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import sys
    print(sys.path)

    img = mpimg.imread('/Users/khanh/Downloads/1.Source_codes/teslapython_pypi/teslapython/teslapython/pic5.png')
    imgplot = plt.imshow(img)
    img = mpimg.imread('/Users/khanh/Downloads/1.Source_codes/teslapython_pypi/teslapython/teslapython/pic4.png')
    imgplot = plt.imshow(img)
    plt.show()

def teslapython_9():
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import sys
    print(sys.path)

    plt.figure(1)
    img = mpimg.imread('/Users/khanh/Downloads/1.Source_codes/teslapython_pypi/teslapython/teslapython/pic6.png')
    imgplot = plt.imshow(img)
    plt.figure(2)
    img = mpimg.imread('/Users/khanh/Downloads/1.Source_codes/teslapython_pypi/teslapython/teslapython/pic7.png')
    imgplot = plt.imshow(img)
    plt.figure(3)
    img = mpimg.imread('/Users/khanh/Downloads/1.Source_codes/teslapython_pypi/teslapython/teslapython/pic8.png')
    imgplot = plt.imshow(img)
    plt.show()

def teslapython_10():

    import cv2
    cap=cv2.VideoCapture('/Users/khanh/Downloads/1.Source_codes/teslapython_pypi/teslapython/teslapython/test_video.mp4')
    while(cap.isOpened()):
        result, frame = cap.read()
        if result== True:
            frame= cv2.resize(frame, (640, 480))  # Resize the
            cv2.imshow('VIDEO', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()

def teslapython():
    while True:
        print("Welcome to the TeslaPython Software Foundation!")
        print("1. Process variable to 4-20mA conversion")
        print("2. 4-20mA to process variable conversion")
        print("3. Difference between PNP and NPN sensors")
        print("4. Safety Integrity Level (SIL) calculations")
        print("5. What is an Active Barrier?")
        print("6. Zener Diode Barrier Principle")
        print("7. RTD, Thermocouple and Thermistor")
        print("8. Labelling of explosion proof equipment")
        print("9. ANSI codes")
        print("10. Directional Overcurrent Relay (67) Explaination")
        print("11. Exit")

        choice = input("Enter your choice (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, or 11): ")

        if choice == '1':
            teslapython_1()
        elif choice == '2':
            teslapython_2()
        elif choice == '3':
            teslapython_3()
        elif choice == '4':
            teslapython_4()
        elif choice == '5':
            teslapython_5()
        elif choice == '6':
            teslapython_6()
        elif choice == '7':
            teslapython_7()
        elif choice == '8':
            teslapython_8()
        elif choice == '9':
            teslapython_9()
        elif choice == '10':
            teslapython_10()
        elif choice == '11':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    teslapython()