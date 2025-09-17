import os
import cv2
import numpy as np
from pathlib import Path
from utils import save_labels, ensure_dir
import argparse

CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

def gather_images(dataset_dir):
    """
    Walks dataset_dir, expects subdirectories per person.
    Returns face_images list (grayscale arrays) and label_ids list.
    Also returns labels_map: id -> name
    """
    detector = cv2.CascadeClassifier(CASCADE_PATH)
    faces = []
    ids = []
    labels_map = {}
    current_id = 0

    # sort directories for deterministic ids
    persons = sorted([d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))])
    if len(persons) == 0:
        raise RuntimeError(f"No person subfolders found in {dataset_dir}. Each person should be a folder containing images.")

    for person in persons:
        current_id += 1
        person_id = current_id
        labels_map[person_id] = person
        person_dir = os.path.join(dataset_dir, person)
        image_files = sorted([f for f in os.listdir(person_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))])
        if len(image_files) == 0:
            print(f"[!] Warning: no images for {person} in {person_dir}, skipping.")
            continue
        for img_name in image_files:
            path = os.path.join(person_dir, img_name)
            img = cv2.imread(path)
            if img is None:
                print(f"[!] Could not read {path}, skipping.")
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            detected = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))
            if len(detected) == 0:
                # fallback: use whole image (useful if images are already cropped)
                faces.append(gray)
                ids.append(person_id)
            else:
                for (x,y,w,h) in detected:
                    faces.append(gray[y:y+h, x:x+w])
                    ids.append(person_id)
    return faces, ids, labels_map

def train(dataset_dir="dataset", model_dir="model"):
    ensure_dir(model_dir)
    print("[*] Gathering images...")
    faces, ids, labels_map = gather_images(dataset_dir)
    if len(faces) == 0:
        print("[!] No faces gathered. Check dataset folder structure and images.")
        return
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
    except AttributeError:
        raise RuntimeError("cv2.face not found. Install opencv-contrib-python (not plain opencv-python).")
    print(f"[*] Training on {len(faces)} face samples from {len(labels_map)} people...")
    recognizer.train(faces, np.array(ids))
    trainer_path = os.path.join(model_dir, "trainer.yml")
    recognizer.save(trainer_path)
    labels_path = os.path.join(model_dir, "labels.pickle")
    save_labels(labels_map, labels_path)
    print(f"[+] Training complete. Model saved to: {trainer_path}")
    print(f"[+] Labels saved to: {labels_path}")
    print("[*] Labels mapping (id -> name):")
    for k,v in labels_map.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="dataset", help="Path to dataset folder (subfolders per person)")
    parser.add_argument("--model-dir", default="model", help="Directory to save trained model and labels")
    args = parser.parse_args()
    train(args.dataset, args.model_dir)
