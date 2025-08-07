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