import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os
from PIL import Image, ImageTk

filelist = []
filtered_files = []
img_index = 0
folder_path = ""

def openDialog():
    global filelist, folder_path
    folder_path = filedialog.askdirectory(title="Select a Folder")
    if folder_path:
        files = os.listdir(folder_path)
        filelist = [file for file in files if os.path.isfile(os.path.join(folder_path,file))]
        for file in filelist:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')):
                filtered_files.append(file)
            # print(filtered_files)
    else:
        print("No folder selected.")

# def eval_blur(img_path):
#     img = cv2.imread(img_path)
#     gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#     laplacian = cv2.Laplacian(gray,cv2.CV_64F)
#     variance = laplacian.var()
#     return variance

def eval_blur(img_path):
    # Convert path to raw string or use double backslashes for Windows paths
    normalized_path = img_path.replace('\\', '/')
    
    # Try reading with OpenCV
    img = cv2.imread(normalized_path)
    
    # If OpenCV fails, use PIL to load and convert to OpenCV format
    if img is None:
        try:
            pil_img = Image.open(normalized_path)
            img = np.array(pil_img)
            
            # Convert RGB to BGR (if image is in RGB format)
            if len(img.shape) == 3 and img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Error loading image with PIL: {e}")
            return 0  # Return 0 if image can't be loaded
    
    # Continue with blur evaluation
    if img is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        return variance
    else:
        print(f"Failed to load image: {normalized_path}")
        return 0  # Return 0 if image can't be processed

def filterFiles():
    for file in filelist:
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')):
            filtered_files.append(file)
    print(filtered_files)

# def showImg():
#     global img_index,label,filename_label

#     if filtered_files:
#         image_path = os.path.join(folder_path,filtered_files[img_index])
#         image = Image.open(image_path)
#         image_resized = scaleImg(image, max_width=400, max_height=400)
#         img_tk = ImageTk.PhotoImage(image_resized)
#         label.config(image=img_tk)
#         label.image = img_tk

#     filename_label.config(text=filtered_files[img_index])

def previous_image():
    global img_index
    if img_index > 0:
        img_index -= 1
    showImg()

def next_image():
    global img_index
    if img_index < len(filtered_files)-1:
        img_index += 1
    showImg()

def scaleImg(img, max_width=400, max_height=400):
    img_width, img_height = img.size
    width_ratio = max_width / img_width
    height_ratio = max_height / img_height
    scale_factor = min(width_ratio, height_ratio)

    new_width = int(img_width * scale_factor)
    new_height = int(img_height * scale_factor)

    resized_image = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return resized_image

def window():
    global label, filename_label,score_label
    root = tk.Tk()
    root.geometry("600x600")  
    root.title("Gallery CleanUp")

    top_frame = tk.Frame(root)
    top_frame.pack(fill=tk.X, pady=10)
    
    button = tk.Button(top_frame, text="Wybierz folder", command=openDialog)
    button.pack(side=tk.LEFT, padx=10)
    
    # button2 = tk.Button(top_frame, text="Filtruj tylko zdjęcia", command=filterFiles)
    # button2.pack(side=tk.LEFT, padx=10)
    
    image_frame = tk.Frame(root, width=400, height=400, bg="light gray")
    image_frame.pack(pady=10)
    image_frame.pack_propagate(False) 
    
    label = tk.Label(image_frame)
    label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  
    
    filename_label = tk.Label(root, text="", font=("Arial", 12))
    filename_label.pack(pady=10)

    score_label = tk.Label(root, text="", font=("Arial", 12))
    score_label.pack(pady=10, anchor=tk.CENTER)
    
    nav_frame = tk.Frame(root)
    nav_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
    
    button_left = tk.Button(nav_frame, text="<-", command=previous_image, width=10)
    button_left.pack(side=tk.LEFT, padx=20)
    
    button_right = tk.Button(nav_frame, text="->", command=next_image, width=10)
    button_right.pack(side=tk.RIGHT, padx=20)
    
    root.mainloop()

def showImg():
    global img_index, label, filename_label, score_label

    if filtered_files:
        image_path = os.path.join(folder_path, filtered_files[img_index])
        image = Image.open(image_path)
        image_resized = scaleImg(image, max_width=400, max_height=400)
        img_tk = ImageTk.PhotoImage(image_resized)
        label.config(image=img_tk)
        label.image = img_tk  # Keep a reference    
        
        label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        filename_label.config(text=filtered_files[img_index])
        # Here's the fix - pass the full path to eval_blur
        score = f"Współczynnik rozmazania zdjęcia: {eval_blur(image_path)}"
        score_label.config(text=score)
    else:
        label.config(image="")
        filename_label.config(text="No images to display")

window()
