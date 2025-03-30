import os
import threading
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

# Hàm mở thư mục chứa ảnh và liệt kê các file ảnh vào Listbox
def mo_thu_muc():
    global thu_muc
    thu_muc = filedialog.askdirectory(title="Chọn thư mục chứa ảnh")
    if thu_muc:
        listbox.delete(0, tk.END)
        for ten_file in os.listdir(thu_muc):
            if ten_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                listbox.insert(tk.END, ten_file)
        if listbox.size() == 0:
            messagebox.showinfo("Thông báo", "Thư mục không chứa ảnh hợp lệ!")
        else:
            # Bắt đầu xử lý ảnh trên luồng riêng biệt
            threading.Thread(target=xu_ly_anh, daemon=True).start()

# Hàm xử lý ảnh: nhận diện khuôn mặt, crop và lưu vào thư mục "cropped_faces"
def xu_ly_anh():
    os.makedirs("cropped_faces", exist_ok=True)
    
    tong = listbox.size()
    progress_var.set(0)  # Reset progress bar

    for i, ten_file in enumerate(listbox.get(0, tk.END)):
        duong_dan = os.path.join(thu_muc, ten_file)
        print(f"Đang xử lý ảnh: {duong_dan}")
        anh = cv2.imread(duong_dan)

        if anh is None:
            print(f"Không đọc được ảnh: {duong_dan}")
            continue
        
        try:
            anh_gray = cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            print(f"Lỗi chuyển đổi ảnh {ten_file} sang grayscale: {e}")
            continue

        # Nhận diện khuôn mặt
        faces = face_cascade.detectMultiScale(anh_gray, scaleFactor=1.1, minNeighbors=4)
        print(f"Trong ảnh {ten_file} tìm được {len(faces)} khuôn mặt")

        for (x, y, w, h) in faces:
            khuon_mat = anh[y:y+h, x:x+w]
            duong_luu = os.path.join("cropped_faces", f"crop_{ten_file}")
            cv2.imwrite(duong_luu, khuon_mat)
        
        # Cập nhật progress bar
        progress_var.set((i + 1) / tong * 100)
        progress_bar.update_idletasks()

    messagebox.showinfo("Hoàn thành", "Xử lý ảnh đã hoàn thành.\nKiểm tra thư mục 'cropped_faces'.")

# ----------------- Giao diện -----------------
root = tk.Tk()
root.title("Trình Xử Lý Ảnh Nhận Diện Khuôn Mặt")
root.geometry("550x500")
root.configure(bg="#f7f7f7")

# Tùy chỉnh Style cho ttk
style = ttk.Style(root)
style.theme_use("clam")  # Chọn theme Windows

style.configure("TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#4a90e2", padding=6)
style.map("TButton", background=[("active", "#357ABD")])
style.configure("TLabel", font=("Segoe UI", 10), background="#f7f7f7")
style.configure("TEntry", font=("Segoe UI", 10))

# Tùy chỉnh thanh tiến trình giống Windows
style.configure("Horizontal.TProgressbar",
                background="#0078D7",  # Màu xanh Windows 11
                troughcolor="#E6E6E6",  # Màu nền rãnh (trough)
                bordercolor="#D9D9D9",  # Viền nhẹ
                lightcolor="#0078D7",  # Màu sáng khi đầy
                darkcolor="#005A9E",  # Màu tối của thanh
                thickness=15)  # Độ dày vừa phải

# Frame chứa nút và entry trên đầu
frame_top = tk.Frame(root, bg="#f7f7f7")
frame_top.pack(fill=tk.X, pady=15, padx=15)

btn_mo = ttk.Button(frame_top, text="Mở thư mục", command=mo_thu_muc)
btn_mo.pack(side=tk.LEFT, padx=5)

# Frame danh sách ảnh
frame_list = tk.Frame(root, bg="white", bd=2, relief=tk.RIDGE)
frame_list.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

label_list = ttk.Label(frame_list, text="Danh sách ảnh:", font=("Segoe UI", 11, "bold"))
label_list.pack(anchor="w", padx=10, pady=5)

# Listbox kèm Scrollbar
scrollbar = tk.Scrollbar(frame_list)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(frame_list, font=("Segoe UI", 10), bd=0, yscrollcommand=scrollbar.set)
listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
scrollbar.config(command=listbox.yview)

# Frame chứa progress bar
frame_progress = tk.Frame(root, bg="#f7f7f7")
frame_progress.pack(fill=tk.X, padx=15, pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(frame_progress, style="Horizontal.TProgressbar",
                               variable=progress_var, maximum=100, mode="determinate")
progress_bar.pack(fill=tk.X, padx=10, pady=10)

# Load mô hình nhận diện khuôn mặt của OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

root.mainloop()
