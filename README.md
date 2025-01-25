# A URBAN TRAFFIC MANAGEMENT SYSTEM

This repository contains the source code and implementation details for the research project titled "A Urban Traffic Management System," which was published in the International Journal of Innovation, Information, and Engineering. The project focuses on optimizing traffic flow and reducing congestion using innovative algorithms and technologies.

---

## Publication
You can access the published research paper [here](http://www.journal-iiie-india.com/1_apr_24/77_online_apr.pdf).

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [How to Run](#how-to-run)
- [License](#license)
- [JSON Data Structure](#json-data-structure)

---

## Overview
Urban traffic congestion is a significant issue in metropolitan areas. This project aims to tackle this problem by proposing an intelligent traffic management system. The system detects license plates, emergency vehicles, provides time for pedestrians, adjusts traffic signal lights based on real-time vehicle flow, and stores license plate data in a structured JSON format.

---

## Features
- Detects license plates and emergency vehicles.
- Adjusts traffic signal timings dynamically based on real-time vehicle flow.
- Provides time for pedestrian crossings.
- Stores license plate information in a JSON file with timestamps, locations, red-line crossing violations, and corresponding images.
- Captures and saves images of vehicles violating traffic rules.

---

## Technologies Used
- **Python**: For implementing the core logic and algorithms.
- **OpenCV**: For image processing and license plate detection.
- **YOLOv8**: For object detection and emergency vehicle identification.
- **Google Colab**: For training the YOLOv8 model.
- **Shell Script**: To automate project execution.

---

## How to Run
1. Clone this repository:
   ```bash
   git clone https://github.com/dinesh776/A-URBAN-TRAFFIC-MANAGEMENT-SYSTEM.git
   ```
2. Navigate to the project directory:
   ```bash
   cd A-URBAN-TRAFFIC-MANAGEMENT-SYSTEM
   ```
3. Execute the project by running the shell script:
   ```bash
   bash run.sh
   ```

---

## JSON Data Structure
The project stores vehicle data in a JSON file with the following structure:
```json
{
    "MW51VSU": {
        "Date&Time": {
            "2024-05-04": [
                "10:13:22",
                "10:14:29",
                "10:30:19",
                "10:31:25"
            ]
        },
        "image_path": "/Users/MAC/colab/Final_Project_with_display/Results/Road1/images/car_6faae277170c4eeba9f22544eb60a22f.png",
        "location": "Anandapuram",
        "Red_line_crossed": {
            "true": [
                "2024-05-04",
                "10:13:22"
            ]
        }
    },
    "NA13NRU": {
        "Date&Time": {
            "2024-05-04": [
                "10:13:23",
                "10:14:28",
                "10:30:20",
                "10:31:24"
            ]
        },
        "image_path": "/Users/MAC/colab/Final_Project_with_display/Results/Road1/images/car_428085a2a23a4394995a67fadd93e9a7.png",
        "location": "Kurmanapalem",
        "Red_line_crossed": {
            "true": [
                "2024-05-04",
                "10:13:23"
            ]
        }
    },
    "GX150GJ": {
        "Date&Time": {
            "2024-05-04": [
                "10:15:14"
            ]
        },
        "image_path": "/Users/MAC/colab/Final_Project_with_display/Results/Road1/images/car_df4ea6b57a2843a0a34bedb9836db6c3.png",
        "location": "Anandapuram",
        "Red_line_crossed": {
            "true": [
                "2024-05-04",
                "10:15:14"
            ]
        }
    }
}
```

---

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## Acknowledgments
Special thanks to the contributors and reviewers who made this project and its publication possible.

