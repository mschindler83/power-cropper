# Power Cropper

## Description

Power Cropper is a simple Tkinter-based tool for super fast cropping of images within a folder. It supports preset crop sizes, custom crop regions, and saving cropped images to a designated folder. The application allows users to navigate through images, define crop areas, and save the cropped portions with ease. Cropping information is stored to allow for continued work. It features auto-adjusting dimensions based on user preferences for portrait or landscape orientations, ensuring that the cropping dimensions align with the desired aspect ratio.

__This tool was mainly written to be faster when preparing images for a lora training.__

## Features

-   **Easy Navigation:** Browse through images in a folder using "Next" and "Prev" buttons or the 'A' and 'D' keys.
-   **Preset Crop Sizes:** Choose from a variety of preset crop sizes via radio buttons.
-   **Custom Crop Size:** Define a custom crop area by dragging the mouse over the image.
-   **Auto-Adjusting Dimensions:** Automatically adjusts crop dimensions based on user preference for portrait or landscape orientation.
-   **Quick Save:** Save the cropped image with a single click or by pressing the 'S' key.
-   **Delete Image:** Delete the current image using the 'X' key.
-   **Cropped Image Counter:** Keeps track of the number of images cropped at each dimension.
-   **Jump to Last Cropped:** Jump to the last cropped image with the E key.
-   **Scrollable Canvas:** Supports mousewheel scrolling for both vertical and horizontal navigation within the image.
-   **Dark Theme:** Features a dark theme for comfortable, extended use.

## Installation

Follow these steps to install and run the QuickSave Cropper:

1.  **Clone the Repository:**

    ```
    git clone https://github.com/mschindler83/power-cropper.git
    cd power-cropper
    ```

2.  **Create a Virtual Environment:**

    It is highly recommended to use a virtual environment to manage dependencies.

    ```
    python3 -m venv venv
    ```

3.  **Activate the Virtual Environment:**

    *   On Linux/macOS:

        ```
        source venv/bin/activate
        ```

    *   On Windows:

        ```
        .\venv\Scripts\activate.bat
        ```

4.  **Install Dependencies:**

    ```
    pip install -r requirements.txt
    ```

5.  **Run the Script:**

    ```
    python power-cropper.py
    ```

## Usage

1.  **Open Folder:** Click the "Open Folder" button to select a directory containing images.
2.  **Navigate Images:** Use the "Next" and "Prev" buttons to navigate through the images. Alternatively, use the 'A' (previous) and 'D' (next) keys.
3.  **Select Crop Size:** Choose a preset crop size from the radio buttons, or select "Custom" to draw a custom crop area.
4.  **Orientation Preference:** Select either "Portrait" or "Landscape" to auto-adjust dimensions based on the selected preference.
5.  **Define Crop Area:**
    *   For preset sizes, click on the image to place the crop rectangle. The dimensions will automatically adjust to fit the selected orientation preference.
    *   For custom sizes, click and drag on the image to define the crop area.
6.  **Quick Save:** Press the "Quick Save" button or the 'S' key to save the cropped image to a "cropped" subfolder within the selected directory.
7.  **Delete Image:** If you want to delete the current image, press the "X" key.
8.  **Dimension Counts:** The right panel displays the count of cropped images for each dimension.
9.  **Jump to Last Cropped:** To continue working where you left off, press the "Jump to Last Cropped" button or the 'E' key to return to the last image you cropped in the current folder.

## Notes

*   The cropped images are saved in a subfolder named "cropped" within the selected directory.
*   The tool supports `.png`, `.jpg`, `.jpeg`, and `.bmp` image formats.
*   Cropping information is saved in `cropped_info.json` and `last_cropped.json` to persist the data between sessions.

