import os
import json
from tqdm import tqdm
from src.image_processing.image_processing import extract_text_from_image
from src.text_processing.text_processing import reformat_text

def process_images(input_folder):
    video_data = []

    # Process a folder of images only if it contains more than just the 'completed' folder
    if len(os.listdir(input_folder)) > 1:

        # Create a tqdm progress bar for processing images
        with tqdm(total=len(os.listdir(input_folder))-1) as pbar:
            # Process each image in the input folder
            for filename in os.listdir(input_folder):
                if filename.endswith(".jpg") or filename.endswith(".png"):
                    image_path = os.path.join(input_folder, filename)
                    extracted_text = extract_text_from_image(image_path)
                    formatted_data = reformat_text(extracted_text)
                    video_data.append(formatted_data)

                    pbar.update(1)  # Update the progress bar

        # Sort video_data by the 'part' field in ascending order
        video_data = sorted(video_data, key=lambda x: int(x["part"]))

        # Append the video data to video.json
        with open('video.json', 'w') as json_file:
            json.dump(video_data, json_file, indent=4)

        print("Data appended to video.json.")
    else:
        print("No images to process in the 'images' folder.")