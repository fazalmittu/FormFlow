import cv2 as cv
import numpy as np
import math
import boto3
import os

ELBOW_ANGLE_ARRAY = []

BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
               "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
               "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
               "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
               ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
               ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
               ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
               ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"] ]

def process_frame(frame, thr=0.1, width=368, height=368):
    net = cv.dnn.readNetFromTensorflow("openpose_overlay/weights/graph_opt.pb")

    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    
    net.setInput(cv.dnn.blobFromImage(frame, 1.0, (width, height), (127.5, 127.5, 127.5), swapRB=True, crop=False))
    out = net.forward()
    out = out[:, :19, :, :]  # MobileNet output [1, 57, -1, -1], we only need the first 19 elements

    assert(len(BODY_PARTS) == out.shape[1])

    points = []
    for i in range(len(BODY_PARTS)):
        heatMap = out[0, i, :, :]
        _, conf, _, point = cv.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]
        points.append((int(x), int(y)) if conf > thr else None)
    
    angle_points = []

    for pair in POSE_PAIRS:
        partFrom = pair[0]
        partTo = pair[1]
        assert(partFrom in BODY_PARTS)
        assert(partTo in BODY_PARTS)

        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]

        if points[idFrom] and points[idTo]:
            if (idFrom == 2 and idTo == 3) or (idFrom == 3 and idTo == 4):  # Focus on the right elbow
                angle_points += [points[idFrom]]
                angle_points += [points[idTo]]
                cv.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
            else:
                cv.line(frame, points[idFrom], points[idTo], (255, 255, 255), 3)
            cv.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
            cv.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)

    angle = None
    if len(angle_points) == 4:
        angle = get_angle(angle_points)
    
    ELBOW_ANGLE_ARRAY.append(angle)

    t, _ = net.getPerfProfile()
    freq = cv.getTickFrequency() / 1000
    cv.putText(frame, '%.2fms' % (t / freq), (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

    return frame, angle

def dot_product(vA, vB):
    return vA[0]*vB[0]+vA[1]*vB[1]

def get_angle(angle_points):
    # Vector from shoulder to elbow
    v1 = [angle_points[0][0] - angle_points[1][0], angle_points[0][1] - angle_points[1][1]]
    # Vector from wrist to elbow
    v2 = [angle_points[3][0] - angle_points[2][0], angle_points[3][1] - angle_points[2][1]]
    
    # Calculate the dot product of v1 and v2
    dot = dot_product(v1, v2)
    
    # Calculate the magnitudes of v1 and v2
    magA = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    magB = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
    
    # Avoid division by zero and handle edge cases
    if magA == 0 or magB == 0:
        return None
    
    # Calculate the cosine of the angle
    cos_angle = dot / (magA * magB)
    
    # Clamp the cosine value to the range [-1, 1] to avoid any floating-point issues
    cos_angle = max(-1.0, min(1.0, cos_angle))
    
    # Calculate the angle in radians
    angle = math.acos(cos_angle)
    
    # Convert the angle to degrees
    ang_deg = math.degrees(angle)
    
    return ang_deg
    
def process_image_and_get_elbow_angle(image_path):
    # image = cv.imread(image_path)
    # processed_image, elbow_angle = process_frame(image)
    # path to image is static/images/user/frame_0.jpg
    # get the number from the filename
    frame_number = int(image_path.split('_')[-1].split('.')[0])
    elbow_angle = ELBOW_ANGLE_ARRAY[frame_number]
    # cv.imshow('Processed Image', processed_image)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    return elbow_angle


def generate_video(filename):
     
    # Load video
    cap = cv.VideoCapture(filename=filename)
    # Get video properties
    
    fps = cap.get(cv.CAP_PROP_FPS)
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    output_video_path = 'uploads/output_video.mp4'
    out = cv.VideoWriter(output_video_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process the frame
        processed_frame, angle = process_frame(frame)

        # Write the processed frame to the output video
        out.write(processed_frame)

    # Release everything if job is finished
    cap.release()
    out.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    # input_img = "data/jordan.jpg"
    # output_img = process_image(input_img)
    # cv.imshow("Output", output_img)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    # python3 -m openpose_overlay.overlay
    generate_video("data/freethrow.mp4")
    #print(process_image_and_get_elbow_angle("data/jordan.jpg"))

    