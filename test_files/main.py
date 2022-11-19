from flask import Flask,render_template,Response
import cv2
import pickle
import cvzone
import numpy as np

app=Flask(__name__)
cap=cv2.VideoCapture("carPark.mp4")


            
            
            
def generate_frames():
    while True:
            
        ## read the camera frame
        success,img=cap.read()

        
        if not success:
            break
        else:
            with open('CarParkPos', 'rb') as f:
                posList = pickle.load(f)     
            width, height = 107, 48

            def checkParkingSpace(imgPro):
                        spaceCounter = 0

                        for pos in posList:
                            x, y = pos

                            imgCrop = imgPro[y:y + height, x:x + width]
                            # cv2.imshow(str(x * y), imgCrop)
                            count = cv2.countNonZero(imgCrop)

                            if count < 900:
                                color = (0, 255, 0)
                                thickness = 5
                                spaceCounter += 1
                            else:
                                color = (0, 0, 255)
                                thickness = 2

                            cv2.rectangle(img, pos, (pos[0] + width,
                                        pos[1] + height), color, thickness)
                            # cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
                            #                 thickness=2, offset=0, colorR=color)

                        cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                                        thickness=5, offset=20, colorR=(0, 200, 0))
            while True:

                if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, img = cap.read()
                imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
                imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                    cv2.THRESH_BINARY_INV, 25, 16)
                imgMedian = cv2.medianBlur(imgThreshold, 5)
                kernel = np.ones((3, 3), np.uint8)
                imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

                checkParkingSpace(imgDilate)
                ret,buffer=cv2.imencode('.jpg',img)
                frame=buffer.tobytes()
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/helpDesk')
def helpDesk():
    return render_template('helpDesk.html')

@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')

@app.route('/parking')
def parking():
    return render_template('parking.html')

@app.route('/parking/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(debug=True)