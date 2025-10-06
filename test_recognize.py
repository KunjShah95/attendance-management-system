from streamlit_utils import recognize_and_mark

# pick a sample image from dataset
img_path = "dataset/kunj/20250811_065936.jpg"
with open(img_path, "rb") as f:
    img_bytes = f.read()

res = recognize_and_mark(img_bytes, threshold=70)
print("Recognition result:", res)
