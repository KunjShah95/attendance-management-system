import cv2
import os
import pickle
from pathlib import Path
from utils import mark_attendance_db, load_labels, ensure_dir
import argparse
import datetime


CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
UNKNOWN_DIR = "unknowns"
MODEL_DIR = "model"




def save_unknown(face_img):
	ensure_dir(UNKNOWN_DIR)
	ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
	path = os.path.join(UNKNOWN_DIR, f"unknown_{ts}.jpg")
	cv2.imwrite(path, face_img)




def run(cam_index=0, model_dir=MODEL_DIR, threshold=70):
	labels_path = os.path.join(model_dir, "labels.pickle")
	trainer_path = os.path.join(model_dir, "trainer.yml")
	if not os.path.exists(trainer_path):
		raise RuntimeError("No trained model found. Run train.py first.")
	with open(labels_path, "rb") as f:
		labels_map = pickle.load(f)
	recognizer = cv2.face.LBPHFaceRecognizer_create()
	recognizer.read(trainer_path)
	detector = cv2.CascadeClassifier(CASCADE_PATH)
	cap = cv2.VideoCapture(cam_index)
	print("[*] Starting camera. Press 'q' to quit.")
	while True:
		ret, frame = cap.read()
		if not ret:
			break
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60,60))
		for (x,y,w,h) in faces:
			face_gray = gray[y:y+h, x:x+w]
			face_color = frame[y:y+h, x:x+w]
			try:
				label_id, conf = recognizer.predict(face_gray)
			except Exception:
				label_id, conf = None, 999
			if label_id is not None and conf < threshold:
				name = labels_map.get(label_id, f"ID_{label_id}")
				mark_attendance_db(label_id, name)
				color = (0,255,0)
				text = f"{name} ({round(conf,1)})"
			else:
				color = (0,0,255)
				text = "Unknown"
				save_unknown(face_color)
			cv2.rectangle(frame, (x,y), (x+w,y+h), color, 2)
			cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
		cv2.imshow('Attendance', frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	cap.release()
	cv2.destroyAllWindows()




if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--cam', type=int, default=0)
	parser.add_argument('--threshold', type=float, default=70.0)
	args = parser.parse_args()
	run(args.cam, threshold=args.threshold)