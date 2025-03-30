import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Button, Label, Entry, Style
import face_recognition
from PIL import Image, ImageTk
import numpy as np

def convert_image_to_rgb(image_path):
    try:
        pil_image = Image.open(image_path).convert("RGB")
        image_array = np.array(pil_image, dtype=np.uint8)
        # Ép mảng thành contiguous array
        image_array = np.ascontiguousarray(image_array)
        print(f"Ảnh {os.path.basename(image_path)} sau chuyển đổi có mode: RGB, shape: {image_array.shape}, dtype: {image_array.dtype}")
        return image_array
    except Exception as e:
        print(f"Lỗi chuyển đổi ảnh {image_path}: {e}")
        return None


# Hàm để chọn thư mục chứa ảnh
def open_folder():
    folder = filedialog.askdirectory(title="Chọn thư mục chứa ảnh")
    if not folder:
        return
    folder_path.set(folder)
    list_files(folder)

# Hàm liệt kê các file ảnh trong thư mục vào listbox
def list_files(folder):
    listbox.delete(0, tk.END)
    for file in os.listdir(folder):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            listbox.insert(tk.END, file)

# Hàm khởi động xử lý cắt khuôn mặt trong một thread
def process_faces():
    folder = folder_path.get()
    if not folder:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn thư mục chứa ảnh!")
        return

    thread = threading.Thread(target=run_face_detection, args=(folder,))
    thread.daemon = True
    thread.start()

# Hàm thực hiện nhận diện và crop khuôn mặt
def run_face_detection(folder):
    files = listbox.get(0, tk.END)
    if not files:
        messagebox.showwarning("Cảnh báo", "Thư mục không có ảnh hợp lệ!")
        return

    # Tạo thư mục lưu ảnh khuôn mặt (nằm cùng thư mục chương trình)
    output_folder = os.path.join(os.getcwd(), "cropped_faces")
    os.makedirs(output_folder, exist_ok=True)

    progress['maximum'] = len(files)

    for index, file in enumerate(files):
        file_path = os.path.join(folder, file)
        print(f"Đang xử lý ảnh: {file_path}")
        # Chuyển đổi ảnh sang mảng NumPy với định dạng RGB
        image = convert_image_to_rgb(file_path)
        if image is None:
            print(f"Bỏ qua ảnh {file} do lỗi chuyển đổi.")
            continue

        try:
            face_locations = face_recognition.face_locations(image)
            print(f"Số khuôn mặt tìm được trong {file}: {len(face_locations)}")

            for i, (top, right, bottom, left) in enumerate(face_locations):
                face_image = image[top:bottom, left:right]
                pil_face = Image.fromarray(face_image)
                save_path = os.path.join(output_folder, f"{os.path.splitext(file)[0]}_face{i+1}.jpg")
                pil_face.save(save_path)

            progress['value'] = index + 1
            progress_label.config(text=f"Đang xử lý: {index + 1}/{len(files)}")
            window.update_idletasks()
        except Exception as e:
            print(f"Lỗi khi xử lý {file}: {e}")
            continue

    messagebox.showinfo("Hoàn thành", f"Đã xử lý xong tất cả ảnh!\nKết quả lưu trong thư mục: {output_folder}")
    try:
        os.startfile(output_folder)  # Chỉ hỗ trợ trên Windows
    except Exception as e:
        print(f"Lỗi mở thư mục kết quả: {e}")

# --- Giao diện Tkinter ---

window = tk.Tk()
window.title("Ứng dụng Nhận diện Khuôn Mặt")
window.geometry("700x600")
window.configure(bg="#f0f4f7")

# Tạo Style tùy chỉnh cho ttk widget
style = Style(window)
style.theme_use("clam")
style.configure("TButton", font=("Poppins", 10, "bold"), foreground="#ffffff", background="#4a90e2", padding=6)
style.map("TButton", background=[("active", "#357ABD")])
style.configure("TLabel", font=("Poppins", 10), background="#f0f4f7")
style.configure("TEntry", font=("Poppins", 10))

# Biến lưu trữ đường dẫn thư mục
folder_path = tk.StringVar()

# Frame chứa các nút và entry ở đầu cửa sổ
frame_top = tk.Frame(window, bg="#f0f4f7")
frame_top.pack(fill=tk.X, pady=15, padx=15)

btn_open = Button(frame_top, text="Mở thư mục", command=open_folder)
btn_open.pack(side=tk.LEFT, padx=5)

entry_folder = Entry(frame_top, textvariable=folder_path, width=50)
entry_folder.pack(side=tk.LEFT, padx=5)

btn_process = Button(frame_top, text="Xử lý ảnh", command=process_faces)
btn_process.pack(side=tk.LEFT, padx=5)

# Frame hiển thị danh sách ảnh
listbox_frame = tk.Frame(window, bg="#ffffff", bd=2, relief=tk.RIDGE)
listbox_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

listbox_label = Label(listbox_frame, text="Danh sách ảnh:", font=("Poppins", 11, "bold"), anchor="w")
listbox_label.pack(fill=tk.X, padx=10, pady=5)

# Scrollbar cho Listbox
scrollbar = tk.Scrollbar(listbox_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(listbox_frame, height=15, width=80, font=("Poppins", 10), bd=0, yscrollcommand=scrollbar.set)
listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
scrollbar.config(command=listbox.yview)

# Frame chứa Progressbar và nhãn hiển thị tiến trình
progress_frame = tk.Frame(window, bg="#f0f4f7")
progress_frame.pack(fill=tk.X, padx=15, pady=10)

progress = Progressbar(progress_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
progress.pack(side=tk.LEFT, padx=10, pady=10)

progress_label = Label(progress_frame, text="Đang xử lý: 0/0", font=("Poppins", 10))
progress_label.pack(side=tk.LEFT, padx=10)

window.mainloop()
