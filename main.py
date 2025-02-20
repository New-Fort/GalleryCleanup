import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os
from PIL import Image, ImageTk
from skimage.transform import radon

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

def advanced_blur_detection(img_path):
    try:
        # Use PIL to load the image (better with Unicode paths)
        from PIL import Image
        pil_img = Image.open(img_path)
        
        # Convert PIL Image to numpy array for OpenCV
        img = np.array(pil_img)
        
        # Handle grayscale images
        if len(img.shape) == 2:
            gray = img
        # Handle RGB images
        elif len(img.shape) == 3:
            # Convert to grayscale
            if img.shape[2] == 3:  # RGB
                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            elif img.shape[2] == 4:  # RGBA
                gray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
            else:
                gray = img[:, :, 0]  # Use first channel
        else:
            print(f"Unexpected image shape: {img.shape}")
            return {"blur_score": 0, "likely_blurred": False}
        
        # 1. Laplacian variance (basic method)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        lap_var = laplacian.var()
        
        # 2. Edge strength analysis
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edges = np.sqrt(sobelx**2 + sobely**2)
        edge_strength = np.mean(edges)
        
        # 3. Simple FFT analysis
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude = np.abs(fshift)
        spectrum_energy = np.sum(magnitude) / (gray.shape[0] * gray.shape[1])
        
        # Combine metrics with appropriate weights
        # Handle cases where metrics might be zero or extreme
        lap_var = max(0.1, min(lap_var, 10000))
        edge_strength = max(0.1, min(edge_strength, 10000))
        spectrum_energy = max(0.1, min(spectrum_energy, 10000))
        
        # Calculate individual blur scores (higher = more blur)
        lap_score = 100 / lap_var if lap_var > 0 else 100
        edge_score = 100 / edge_strength if edge_strength > 0 else 100
        spectrum_score = 100 / spectrum_energy if spectrum_energy > 0 else 100
        
        # Scale the scores to more reasonable ranges
        lap_score = min(100, lap_score * 0.5)
        edge_score = min(100, edge_score * 0.05)
        spectrum_score = min(100, spectrum_score * 0.001)
        
        # Combine scores with weights
        blur_score = (
            0.3 * lap_score +
            0.3 * edge_score +
            0.4 * spectrum_score
        )
        
        # Normalize to 0-100 scale
        normalized_score = min(100, max(0, blur_score))
        is_blurred = normalized_score > 60  # Adjust threshold as needed
        
        return {
            "blur_score": normalized_score,
            "likely_blurred": is_blurred,
            "detail": {
                "laplacian_var": lap_var,
                "edge_strength": edge_strength,
                "spectrum_energy": spectrum_energy
            }
        }
        
    except Exception as e:
        print(f"Error processing image {img_path}: {e}")
        import traceback
        traceback.print_exc()
        return {"blur_score": 0, "likely_blurred": False, "error": str(e)}
    
# def fast_blur_detection(img_path, resize_width=512, blur_threshold=30):
#     try:
#         pil_img = Image.open(img_path)
#         img = np.array(pil_img)

#         # Resize to speed up processing
#         h, w = img.shape[:2]
#         scale = resize_width / w
#         new_size = (resize_width, int(h * scale))
#         img_resized = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)

#         # Convert to grayscale
#         if len(img_resized.shape) == 3:
#             gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
#         else:
#             gray = img_resized

#         # **Laplacian Variance (Fast Blur Detection)**
#         laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

#         # **Simple Edge Strength Check**
#         edges = cv2.Canny(gray, 50, 150)
#         edge_density = np.sum(edges) / edges.size

#         # **Motion Blur Detection via FFT (Directional Analysis)**
#         fft = np.fft.fft2(gray)
#         fft_shift = np.fft.fftshift(fft)
#         magnitude_spectrum = np.log1p(np.abs(fft_shift))
#         motion_blur_score = np.std(magnitude_spectrum)

#         # Combine into a blur score
#         blur_score = (100 / max(laplacian_var, 1)) + (50 / max(edge_density, 1)) + (50 / max(motion_blur_score, 1))
#         normalized_score = min(100, max(0, blur_score))

#         # Thresholding based on good/bad photo examples
#         likely_blurred = normalized_score > blur_threshold

#         return {
#             "blur_score": normalized_score,
#             "likely_blurred": likely_blurred,
#             "details": {
#                 "laplacian_var": laplacian_var,
#                 "edge_density": edge_density,
#                 "motion_blur_score": motion_blur_score
#             }
#         }

#     except Exception as e:
#         return {"blur_score": 0, "likely_blurred": False, "error": str(e)}

def tuned_blur_detection(img_path, resize_width=512):
    try:
        pil_img = Image.open(img_path)
        img = np.array(pil_img)

        # Resize to optimize speed
        h, w = img.shape[:2]
        scale = resize_width / w
        new_size = (resize_width, int(h * scale))
        img_resized = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)

        # Convert to grayscale
        if len(img_resized.shape) == 3:
            gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_resized

        # **Laplacian Variance - Key Blur Detector**
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # **Edge Density - Helps Differentiate Blur**
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges) / edges.size

        # **Motion Blur Detection via FFT**
        fft = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude_spectrum = np.log1p(np.abs(fft_shift))
        motion_blur_score = np.std(magnitude_spectrum)

        # **Score Recalibration**
        blur_score = (1000 / max(laplacian_var, 10)) + (100 / max(edge_density, 0.1)) + (30 / max(motion_blur_score, 1))
        normalized_score = min(100, max(0, blur_score))  # Keep within 0-100 range

        # **New Thresholds**
        if normalized_score < 15:
            blur_category = "Sharp"
        elif normalized_score < 30:
            blur_category = "Acceptable"
        else:
            blur_category = "Blurry"

        return {
            "blur_score": normalized_score,
            "category": blur_category,
            "details": {
                "laplacian_var": laplacian_var,
                "edge_density": edge_density,
                "motion_blur_score": motion_blur_score
            }
        }

    except Exception as e:
        return {"blur_score": 0, "category": "Error", "error": str(e)}

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

# def showImg():
#     global img_index, label, filename_label, score_label

#     if filtered_files:
#         image_path = os.path.join(folder_path, filtered_files[img_index])
#         image = Image.open(image_path)
#         image_resized = scaleImg(image, max_width=400, max_height=400)
#         img_tk = ImageTk.PhotoImage(image_resized)
#         label.config(image=img_tk)
#         label.image = img_tk  # Keep a reference    
        
#         label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

#         filename_label.config(text=filtered_files[img_index])
#         # Here's the fix - pass the full path to eval_blur
#         score = f"Współczynnik rozmazania zdjęcia: {eval_blur(image_path)}"
#         score_label.config(text=score)
#     else:
#         label.config(image="")
#         filename_label.config(text="No images to display")

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
        
        blur_result = tuned_blur_detection(image_path)
        score_text = f"Współczynnik rozmazania: {blur_result['blur_score']:.1f}/100"
        print(blur_result)
        # if blur_result['likely_blurred']:
        #     score_text += " - Prawdopodobnie rozmazane"
        
        score_label.config(text=score_text)
    else:
        label.config(image="")
        filename_label.config(text="No images to display")

window()
