# Các thư viện cần thiết
import os  # Làm việc với hệ thống tệp/thư mục
import threading  # Dùng để xử lý song song (không bị treo giao diện)
import cv2  # OpenCV - xử lý ảnh và nhận diện khuôn mặt
import tkinter as tk  # Giao diện cơ bản
from tkinter import filedialog, messagebox, ttk  # Các widget nâng cao
from PIL import Image  

# ---------------------- HÀM CHÍNH ----------------------

# Hàm mở thư mục và liệt kê các file ảnh vào Listbox
def mo_thu_muc():
    global thu_muc  # Biến toàn cục chứa đường dẫn thư mục
    thu_muc = filedialog.askdirectory(title="Chọn thư mục chứa ảnh")  # Mở hộp thoại chọn thư mục

    if thu_muc:  # Nếu có chọn thư mục
        listbox.delete(0, tk.END)  # Xóa các item cũ trong Listbox

        # Duyệt qua tất cả file trong thư mục
        for ten_file in os.listdir(thu_muc):
            if ten_file.lower().endswith(('.png', '.jpg', '.jpeg')):  # Chỉ nhận file ảnh
                listbox.insert(tk.END, ten_file)  # Thêm vào Listbox

        if listbox.size() == 0:  # Nếu không có ảnh hợp lệ
            messagebox.showinfo("Thông báo", "Thư mục không chứa ảnh hợp lệ!")
        else:
            # Chạy xử lý ảnh trên luồng riêng để tránh treo GUI
            threading.Thread(target=xu_ly_anh, daemon=True).start()

# Hàm xử lý từng ảnh: nhận diện khuôn mặt, crop và lưu lại
def xu_ly_anh():
    os.makedirs("cropped_faces", exist_ok=True)  # Tạo thư mục lưu ảnh đã cắt nếu chưa có

    tong = listbox.size()  # Tổng số ảnh trong danh sách
    progress_var.set(0)  # Reset progress bar

    for i, ten_file in enumerate(listbox.get(0, tk.END)):  # Duyệt từng ảnh
        duong_dan = os.path.join(thu_muc, ten_file)  # Tạo đường dẫn đầy đủ
        print(f"Đang xử lý ảnh: {duong_dan}")
        anh = cv2.imread(duong_dan)  # Đọc ảnh bằng OpenCV

        if anh is None:
            print(f"Không đọc được ảnh: {duong_dan}")
            continue

        try:
            anh_gray = cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY)  # Chuyển sang ảnh xám
        except Exception as e:
            print(f"Lỗi chuyển đổi ảnh {ten_file} sang grayscale: {e}")
            continue

        # Dùng mô hình HaarCascade để nhận diện khuôn mặt
        faces = face_cascade.detectMultiScale(anh_gray, scaleFactor=1.1, minNeighbors=4)
        print(f"Trong ảnh {ten_file} tìm được {len(faces)} khuôn mặt")

        for (x, y, w, h) in faces:  # Duyệt qua các khuôn mặt được phát hiện
            khuon_mat = anh[y:y+h, x:x+w]  # Cắt vùng khuôn mặt từ ảnh gốc
            duong_luu = os.path.join("cropped_faces", f"crop_{ten_file}")  # Đặt tên file mới
            cv2.imwrite(duong_luu, khuon_mat)  # Lưu ảnh đã cắt

        # Cập nhật tiến trình (%)
        progress_var.set((i + 1) / tong * 100)
        progress_bar.update_idletasks()

    # Hiển thị thông báo khi xong
    messagebox.showinfo("Hoàn thành", "Xử lý ảnh đã hoàn thành.\nKiểm tra thư mục 'cropped_faces'.")

# ---------------------- GIAO DIỆN TKINTER ----------------------

root = tk.Tk()  # Tạo cửa sổ chính
root.title("Trình Xử Lý Ảnh Nhận Diện Khuôn Mặt")
root.geometry("550x500")  # Kích thước cửa sổ
root.configure(bg="#f7f7f7")  # Màu nền

# Tùy chỉnh style giao diện cho ttk (nút, thanh tiến trình, ...)
style = ttk.Style(root)
style.theme_use("clam")  # Giao diện thân thiện với Windows

# Style cho nút
style.configure("TButton", font=("Segoe UI", 10, "bold"), foreground="#ffffff", background="#4a90e2", padding=6)
style.map("TButton", background=[("active", "#357ABD")])

# Style cho nhãn và ô nhập
style.configure("TLabel", font=("Segoe UI", 10), background="#f7f7f7")
style.configure("TEntry", font=("Segoe UI", 10))

# Style cho thanh tiến trình
style.configure("Horizontal.TProgressbar",
                background="#0078D7",  # Màu xanh chính
                troughcolor="#E6E6E6",  # Màu nền thanh
                bordercolor="#D9D9D9",
                lightcolor="#0078D7",
                darkcolor="#005A9E",
                thickness=15)

# ----------- Giao diện bố cục -----------

# Frame chứa nút mở thư mục
frame_top = tk.Frame(root, bg="#f7f7f7")
frame_top.pack(fill=tk.X, pady=15, padx=15)

btn_mo = ttk.Button(frame_top, text="Mở thư mục", command=mo_thu_muc)
btn_mo.pack(side=tk.LEFT, padx=5)

# Frame chứa danh sách ảnh
frame_list = tk.Frame(root, bg="white", bd=2, relief=tk.RIDGE)
frame_list.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

label_list = ttk.Label(frame_list, text="Danh sách ảnh:", font=("Segoe UI", 11, "bold"))
label_list.pack(anchor="w", padx=10, pady=5)

# Listbox hiển thị tên ảnh + scrollbar
scrollbar = tk.Scrollbar(frame_list)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(frame_list, font=("Segoe UI", 10), bd=0, yscrollcommand=scrollbar.set)
listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
scrollbar.config(command=listbox.yview)

# Frame chứa thanh tiến trình
frame_progress = tk.Frame(root, bg="#f7f7f7")
frame_progress.pack(fill=tk.X, padx=15, pady=10)

progress_var = tk.DoubleVar()  # Biến để điều khiển tiến trình
progress_bar = ttk.Progressbar(frame_progress, style="Horizontal.TProgressbar",
                               variable=progress_var, maximum=100, mode="determinate")
progress_bar.pack(fill=tk.X, padx=10, pady=10)

# Tải mô hình nhận diện khuôn mặt HaarCascade từ OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Khởi chạy ứng dụng
root.mainloop()
