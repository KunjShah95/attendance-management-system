import os
from streamlit_utils import recognize_and_mark
from utils import load_students, load_labels


def test_recognition():
    """Test if face recognition correctly identifies faces after the fix"""
    print("=== Testing Face Recognition Fix ===")

    # Load the current labels and students
    labels = load_labels("model/labels.pickle")
    students = load_students()

    print(f"\nModel labels mapping: {labels}")
    print(f"Students CSV: {[(s['id'], s['name']) for s in students]}")

    # Test with a sample image from kunj's dataset
    kunj_image_path = "dataset/kunj/20240122_173320.jpg"
    if os.path.exists(kunj_image_path):
        print(f"\nTesting with kunj's image: {kunj_image_path}")

        # Read image as bytes (similar to how streamlit processes it)
        with open(kunj_image_path, "rb") as f:
            img_bytes = f.read()

        # Run recognition
        results = recognize_and_mark(
            img_bytes, threshold=100
        )  # Higher threshold for testing

        if results:
            for result in results:
                print("Recognition result:")
                print(f"  - ID: {result['id']}")
                print(f"  - Name: {result['name']}")
                print(f"  - Confidence: {result['confidence']}")
                print(f"  - Debug: {result.get('debug', 'No debug info')}")
        else:
            print("No faces recognized or detected")
    else:
        print(f"Test image not found: {kunj_image_path}")


if __name__ == "__main__":
    test_recognition()
