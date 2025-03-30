import os
import threading
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

def open_directory():
    folder_selected = filedialog.askdirectory(title="Chọn thư mục chứa ảnh")
    if folder_selected:
        listbox.delete(0, tk.END)
        for filename in os.listdir(folder_selected):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                listbox.insert(tk.END, filename)
        if listbox.size() == 0:
            messagebox.showinfo("Thông báo", "Thư mục không chứa ảnh hợp lệ!")
        else:
            process_images(folder_selected)

def process_images(folder):
    # Tạo thư mục lưu ảnh nếu chưa có
    os.makedirs("cropped_faces", exist_ok=True)

    def process():
        total = listbox.size()
        for i, filename in enumerate(listbox.get(0, tk.END)):
            filepath = os.path.join(folder, filename)
            print(f"Đang xử lý ảnh: {filepath}")
            image = cv2.imread(filepath)
            if image is None:
                print(f"Không đọc được ảnh: {filepath}")
                continue
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            except Exception as e:
                print(f"Lỗi chuyển đổi sang gray cho ảnh {filename}: {e}")
                continue
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            print(f"Số khuôn mặt tìm được trong {filename}: {len(faces)}")
            for (x, y, w, h) in faces:
                face = image[y:y+h, x:x+w]
                save_path = os.path.join("cropped_faces", f"cropped_{filename}")
                cv2.imwrite(save_path, face)
            progress_var.set((i + 1) / total * 100)
            progress_bar.update_idletasks()
        messagebox.showinfo("Hoàn thành", "Xử lý ảnh đã hoàn thành. Kiểm tra thư mục 'cropped_faces'.")
    threading.Thread(target=process, daemon=True).start()

# Initialize GUI
root = tk.Tk()
root.title("Image Processor")
root.geometry("500x400")

# Listbox hiển thị tên ảnh
listbox = tk.Listbox(root, width=50)
listbox.pack(pady=10)

# Button mở thư mục
open_button = tk.Button(root, text="Open Directory", command=open_directory)
open_button.pack(pady=5)

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=10, fill=tk.X)

# Load model nhận diện khuôn mặt
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

root.mainloop()
