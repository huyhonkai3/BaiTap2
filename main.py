import psycopg2
import tkinter as tk
from tkinter import messagebox

# Kết nối đến PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="dbtest",
            user="postgres",
            password="123456",
            host="localhost",
            port="5432"
        )
        return conn
    except psycopg2.OperationalError as e:
        messagebox.showerror("Connection Error", f"Operational error: {str(e)}")
    except Exception as e:
        messagebox.showerror("Connection Error", f"Unexpected error: {str(e)}")
    return None

# Hàm tìm kiếm sinh viên
def search_student():
    conn = connect_db()
    
    mssv = entry_search_mssv.get()
    if not mssv:
        messagebox.showerror("Input Error", "Please enter a student code.")
        return

    if conn:
        try:
            cursor = conn.cursor()
            # Truy vấn tất cả sinh viên có mã số sinh viên trùng khớp
            cursor.execute("SELECT * FROM public.sinhvien WHERE mssv = %s", (mssv,))
            results = cursor.fetchall()

            # Xóa dữ liệu hiện tại trong Treeview trước khi thêm kết quả mới
            for row in tree.get_children():
                tree.delete(row)

            if results:
                # Thêm từng kết quả vào Treeview
                for result in results:
                    tree.insert('', 'end', values=(result[0], result[1], result[2], result[3]))
            else:
                messagebox.showinfo("Result", "No student found with the given code.")
        
        except psycopg2.DatabaseError as e:
            messagebox.showerror("Search Error", f"Database error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Search Error", f"Unexpected error: {str(e)}")
        finally:
            cursor.close()

# Hàm thêm mới sinh viên
def add_student():
    conn = connect_db()
    
    mssv = entry_mssv.get()
    ten = entry_name.get()
    nganhhoc = entry_nganhhoc.get()
    khoahoc = entry_khoahoc.get()

    if not (mssv and ten and nganhhoc and khoahoc):
        messagebox.showerror("Input Error", "All fields are required.")
        return
    
    try:
        khoahoc = int(khoahoc)  # Kiểm tra xem khóa học có phải là số hay không
    except ValueError:
        messagebox.showerror("Input Error", "Course year must be an integer.")
        return

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO public.sinhvien (mssv, tensinhvien, nganhhoc, khoahoc) VALUES (%s, %s, %s, %s)",
                (mssv, ten, nganhhoc, khoahoc)
            )
            conn.commit()
            messagebox.showinfo("Success", "Student added successfully!")
        except psycopg2.IntegrityError as e:
            messagebox.showerror("Insert Error", f"Integrity error: {str(e)} (Possible duplicate student code)")
            conn.rollback()
        except psycopg2.DatabaseError as e:
            messagebox.showerror("Insert Error", f"Database error: {str(e)}")
            conn.rollback()
        except Exception as e:
            messagebox.showerror("Insert Error", f"Unexpected error: {str(e)}")
        finally:
            cursor.close()

# GUI
import tkinter as tk
from tkinter import ttk

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Student Management System")

# Tạo notebook (nhiều tab)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# Tab "Thêm sinh viên"
tab_add_student = ttk.Frame(notebook)
notebook.add(tab_add_student, text="Thêm sinh viên")

# Label Frame trong tab "Thêm sinh viên"
lf_add = ttk.LabelFrame(tab_add_student, text="Nhập thông tin sinh viên")
lf_add.pack(padx=10, pady=10, fill="both", expand=True)

#Trường nhập thông tin
lbl_mssv = ttk.Label(lf_add, text="Mã sinh viên:")
lbl_mssv.grid(row=0, column=0, padx=5, pady=5)
entry_mssv = ttk.Entry(lf_add)
entry_mssv.grid(row=0, column=1, padx=5, pady=5)

lbl_name = ttk.Label(lf_add, text="Tên sinh viên:")
lbl_name.grid(row=1, column=0, padx=5, pady=5)
entry_name = ttk.Entry(lf_add)
entry_name.grid(row=1, column=1, padx=5, pady=5)

lbl_nganhhoc = tk.Label(lf_add, text="Ngành học")
lbl_nganhhoc.grid(row=2, column=0, padx=5, pady=5)
entry_nganhhoc = tk.Entry(lf_add)
entry_nganhhoc.grid(row=2, column=1, padx=5, pady=5)

lbl_khoahoc = tk.Label(lf_add, text="Khóa học")
lbl_khoahoc.grid(row=3, column=0, padx=5, pady=5)
entry_khoahoc = tk.Entry(lf_add)
entry_khoahoc.grid(row=3, column=1, padx=5, pady=5)

# Button để thêm sinh viên
btn_add = ttk.Button(lf_add, text="Thêm sinh viên", command=add_student)
btn_add.grid(row=4, columnspan=2, padx=5, pady=5)


# Tab "Tìm kiếm sinh viên"
tab_search_student = ttk.Frame(notebook)
notebook.add(tab_search_student, text="Tìm kiếm sinh viên")

# Label Frame trong tab "Tìm kiếm sinh viên"
lf_search = ttk.LabelFrame(tab_search_student, text="Tìm sinh viên")
lf_search.pack(padx=10, pady=10, fill="both", expand=True)

#Trường nhập thông tin
lbl_search_mssv = tk.Label(lf_search, text="Nhâp mã số sinh viên")
lbl_search_mssv.grid(row=0, column=0, padx=5, pady=5)
entry_search_mssv = ttk.Entry(lf_search)
entry_search_mssv.grid(row=0, column=1, padx=5, pady=5)

# Button để tìm kiếm sinh viên
btn_search = ttk.Button(lf_search, text="Tìm kiếm", command=search_student)
btn_search.grid(row=1, columnspan=2, padx=5, pady=5)

# Bảng (Treeview) để hiển thị kết quả tìm kiếm
columns = ('MSSV', 'Tên', 'Ngành học', 'Khóa học')
tree = ttk.Treeview(lf_search, columns=columns, show='headings')
tree.grid(row=2, column=0, columnspan=2)

# Đặt tiêu đề cho từng cột
tree.heading('MSSV', text='Mã sinh viên')
tree.heading('Tên', text='Tên sinh viên')
tree.heading('Ngành học', text='Ngành học')
tree.heading('Khóa học', text='Khóa học')

# Điều chỉnh độ rộng cột (nếu cần)
tree.column('MSSV', width=100)
tree.column('Tên', width=150)
tree.column('Ngành học', width=100)
tree.column('Khóa học', width=100)

root.mainloop()