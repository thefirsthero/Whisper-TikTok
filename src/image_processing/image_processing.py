import cv2
import pytesseract

def extract_text_from_image(image_path):
    # Load the image using OpenCV
    image = cv2.imread(image_path)

    '''
    PREPROCESSING
    '''
    img = cv2.resize(image, (0, 0), fx=2, fy=2)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    '''
    TEXT EXTRACTION
    '''

    # Use pytesseract to extract text from the image
    config = "--psm 3"
    extracted_text = pytesseract.image_to_string(image, config=config)

    return extracted_text