from transformers import AutoModelForImageClassification, AutoImageProcessor
model_name = "WT-MM/vit-base-blur"

from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog
import os
from PIL import Image, ImageTk
import torch
import torch
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

def filterFiles():
    for file in filelist:
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')):
            filtered_files.append(file)
    print(filtered_files)

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
    load_dotenv()
    load_dotenv()
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

processor = AutoImageProcessor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name) 

def load_and_preprocess_image(image_path):
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    return inputs

def predict_blurriness(image_path):
    inputs = load_and_preprocess_image(image_path)

    # Perform inference
    with torch.no_grad():  # No need to compute gradients
        outputs = model(**inputs)
    
    logits = outputs.logits
    predicted_class_idx = logits.argmax(-1).item()

    # Labels corresponding to the model's output classes
    labels = ["clean", "blurry"]

    # Get the predicted class (blurry or clean)
    predicted_class = labels[predicted_class_idx]

    return predicted_class 

def showImg():
    global img_index, label, filename_label, score_label

    if filtered_files:
        image_path = os.path.join(folder_path, filtered_files[img_index])
        image = Image.open(image_path)
        image_resized = scaleImg(image, max_width=400, max_height=400)
        img_tk = ImageTk.PhotoImage(image_resized)
        label.config(image=img_tk)
        label.image = img_tk
        
        label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        filename_label.config(text=filtered_files[img_index])
        
        blur_result = predict_blurriness(image_path)
        # score_text = f"Współczynnik rozmazania: {blur_result['blur_score']:.1f}/100"
        blur_result = predict_blurriness(image_path)
        # score_text = f"Współczynnik rozmazania: {blur_result['blur_score']:.1f}/100"
        print(blur_result)
        # if blur_result['likely_blurred']:
        #     score_text += " - Prawdopodobnie rozmazane"
        
        # score_label.config(text=score_text)
        # score_label.config(text=score_text)
    else:
        label.config(image="")
        filename_label.config(text="No images to display")

window()
