import os
import cv2
from tkinter import Tk, filedialog, messagebox, Button, Label
import easyocr

parent_folder = None
root = Tk()
root.geometry("800x200")


def blur(path_to_images, reader):
    images = []
    unrecognized = []
    invalid_files = []
    images_files = os.listdir(path_to_images)
    how_many_scanned = 0
    how_many_to_scan = 0
    for path_to_image in images_files:
        how_many_to_scan += 1
    for path_to_image in images_files:
        how_many_scanned += 1
        l_progress.config(
            text=(f"Photos scanned: {how_many_scanned}/{how_many_to_scan}" + "\n" + f"current directory: {path_to_images}"))
        root.update()
        try:
            img = cv2.imread(os.path.join(path_to_images, path_to_image))
        except cv2.error:
            invalid_files.append(os.path.join(path_to_images, path_to_image))
            continue
        # scans image for text and returns coordinates of found bounding boxes
        try:
            results = reader.readtext(img)
        except ValueError:
            invalid_files.append(os.path.join(path_to_images, path_to_image))
            continue
        if len(results) == 0:  # when easyocr doesn't find any text in photo, the results list is empty
            unrecognized.append(
                (
                    {
                        "fname": path_to_image,
                        "image": img
                    }
                )
            )
            continue
        max_surface_points = (0, 0, 0, 0)
        max_surface = 0
        for res in results:
            text = res[1]
            res = res[0]
            if len(text) > 2 or text == "W":
                x1 = max(int(res[0][0]), 0)
                x2 = min(int(res[1][0]), img.shape[1])
                y1 = max(int(res[0][1]), 0)
                y2 = min(int(res[2][1]), img.shape[0])
                # TE= # CRS
                if text.lower() == "crs" or text.lower() == "csr" or ("c" in text.lower() and "a" in text.lower() and "r" in text.lower() and "s" in text.lower()):
                    max_surface_points = (x1, x2, y1, y2)
                    break
                elif abs(x2-x1)*abs(y1-y2) > max_surface:
                    max_surface_points = (x1, x2, y1, y2)

        (x1, x2, y1, y2) = max_surface_points
        x1 = int(x1/1.05)
        x2 = int(min(x2*1.05, img.shape[1]))

        img = cv2.rectangle(img, (x1, y1), (x2, y2),
                            (255, 255, 255), -1)
        images.append(
            {
                "fname": path_to_image,
                "image": img
            })
    return images, unrecognized, invalid_files


def parent_dir():
    global parent_folder
    parent_folder = filedialog.askdirectory()
    l_parent_folder.config(text=f"Selected parent folder: {parent_folder}")
    mask_images_button["state"] = "active"


def mask_images():
    child_folders = os.listdir(parent_folder)  # folders which contain photos
    counter_recognized = 0
    counter_unrecognized = 0
    invalid_files_logs = []
    l_progress.config(text=("Loading the machine learning framework..."))
    root.update()
    reader = easyocr.Reader(['en'], gpu=True)
    for child_folder in child_folders:
        photos_folder = os.path.join(parent_folder, child_folder)
        if os.path.isdir(photos_folder):

            # blurs photos in a given folder, images where
            # text wasn't recognized are also saved
            images, unrecognized, invalid_files = blur(
                photos_folder, reader)
            for img in images:
                cv2.imwrite(
                    f'{parent_folder}/{child_folder}/{img["fname"]}',
                    img["image"])
                counter_recognized += 1
            for img in unrecognized:
                counter_unrecognized += 1
            for invalid_file in invalid_files:
                invalid_files_logs.append(invalid_file)
    if invalid_files_logs != []:
        inv_files_string = "\n".join(invalid_files_logs)
        messagebox.showinfo(
            f'Invalid files found: {len(invalid_files_logs)}',
            f'Invalid files found:\n{inv_files_string}')
    messagebox.showinfo(
        f'Images masked: {counter_recognized}',
        f'Succesfully masked {counter_recognized} images \nUnrecognized images: {counter_unrecognized}')
    l_succesfully_saved.config(
        text=f"Succesfully masked the images",
        cursor="hand2", foreground="blue")
    l_succesfully_saved.bind(
        "<Button-1>", lambda e: os.startfile(parent_folder))

# UI Buttons and labels


l_parent_folder = Label(root, text=f"Selected parent folder: {parent_folder}")
l_parent_folder.config(font=("Courier", 14))

l_succesfully_saved = Label(root, text="")
l_succesfully_saved.config(font=("Courier", 14))

l_progress = Label(root, text="")
l_progress.config(font=("Courier", 14))

images_path_button = Button(
    root, text="Choose parent folder path", command=parent_dir)

mask_images_button = Button(
    root, text="Mask", command=mask_images)

mask_images_button["state"] = "disable"
images_path_button.pack()
l_parent_folder.pack()
mask_images_button.pack()
l_progress.pack()
l_succesfully_saved.pack()

root.mainloop()
