from io import BytesIO
import requests
from PIL import Image
import numpy as np
import easyocr
from pprint import pprint

# Initialize the OCR reader
reader = easyocr.Reader(['en'], gpu=False)


def read_license_plate(license_plate_crop):
    print("\nread license plate started\n")
    detections = reader.readtext(license_plate_crop)
    for detection in detections:
        bbox, text, score = detection

        text = text.upper().replace(' ', '')

        if len(text)>=6 and len(text)<=10:
            # Convert the numpy array to a PIL Image
            license_plate_crop_temp = Image.fromarray((license_plate_crop * 255).astype(np.uint8))

            # Convert the crop into a file-like object
            img_io = BytesIO()
            license_plate_crop_temp.save(img_io, format='JPEG')
            img_io.seek(0)

            response = requests.post(
                'https://api.platerecognizer.com/v1/plate-reader/',
                files=dict(upload= img_io),
                headers={'Authorization': 'Token 19a2b2e25d6ee62a5323a7ffd5bd8da20f3b643c'}
            )
            response_json = response.json()
            # print()
            # pprint(response_json)
            # print()
            results = response_json.get('results', [])
            for result in results:
                plate = result.get('plate')
                if plate:
                    plate=plate.upper()
                    # print()
                    # print(plate)
                    # print()
                    return plate
    return None

def get_car(license_plate, vehicle_track_ids):
    """
    Retrieve the vehicle coordinates and ID based on the license plate coordinates.

    Args:
        license_plate (tuple): Tuple containing the coordinates of the license plate (x1, y1, x2, y2, score, class_id).
        vehicle_track_ids (list): List of vehicle track IDs and their corresponding coordinates.

    Returns:
        tuple: Tuple containing the vehicle coordinates (x1, y1, x2, y2) and ID.
    """
    x1, y1, x2, y2, score, class_id = license_plate

    foundIt = False
    for j in range(len(vehicle_track_ids)):
        xcar1, ycar1, xcar2, ycar2, car_id = vehicle_track_ids[j]

        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            car_indx = j
            foundIt = True
            break

    if foundIt:
        return vehicle_track_ids[car_indx]

    return -1, -1, -1, -1, -1
