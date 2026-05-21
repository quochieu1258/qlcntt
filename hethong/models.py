from django.db import models

class TaiKhoan(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255) # Lưu ý: Tạm thời lưu text thường để dễ test

    class Meta:
        db_table = 'user' # Lệnh này ép tạo bảng tên chính xác là "user" trong DB

class KhoaPhong(models.Model):
    # blank=True, null=True cho phép bỏ trống trường này trong DB và Form
    ma_khoa_phong = models.CharField(max_length=50, blank=True, null=True) 
    
    # Mặc định CharField không có blank=True thì bắt buộc phải nhập
    ten_khoa_phong = models.CharField(max_length=255)

    class Meta:
        db_table = 'khoa_phong' # Ép tên bảng trong PostgreSQL
        
    def __str__(self):
        return self.ten_khoa_phong
    
# Định nghĩa các lựa chọn cho loại thiết bị
LOAI_THIET_BI_CHOICES = [
    ('Máy Tính', 'Máy Tính'),
    ('Máy In', 'Máy In'),
    ('Máy Scan', 'Máy Scan'),
    ('Máy Photo', 'Máy Photo'),
    ('Thiết Bị Mạng', 'Thiết Bị Mạng'),
    ('Quét Mã Vạch', 'Quét Mã Vạch'),
    ('Khác', 'Khác'),
]

class ThietBi(models.Model):
    ma_thiet_bi = models.CharField(max_length=50, blank=True, null=True)
    ten_thiet_bi = models.CharField(max_length=255)
    # Lưu định dạng ngày, cho phép trống
    ngay_su_dung = models.DateField(blank=True, null=True) 
    loai_thiet_bi = models.CharField(max_length=50, choices=LOAI_THIET_BI_CHOICES)
    
    # Khoá ngoại (Foreign Key) liên kết với bảng KhoaPhong
    # on_delete=models.SET_NULL: Nếu xóa Khoa Phòng, thiết bị đó chuyển về trạng thái không có khoa phòng (chưa phân bổ) chứ ko bị xóa theo
    khoa_phong = models.ForeignKey(KhoaPhong, on_delete=models.SET_NULL, null=True, blank=True)
    dang_sua_chua = models.BooleanField(default=False)
    is_hong_han = models.BooleanField(default=False)
    is_thanh_ly = models.BooleanField(default=False) # Đã thanh lý hoàn toàn
    hinh_anh_thanh_ly = models.ImageField(upload_to='thanhly/', null=True, blank=True)
    ngay_thanh_ly = models.DateField(null=True, blank=True)
    ly_do_thanh_ly = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'thiet_bi'

class LichSuSuaChua(models.Model):
    # Liên kết với thiết bị
    thiet_bi = models.ForeignKey(ThietBi, on_delete=models.CASCADE)
    ngay_sua_chua = models.DateField()
    ghi_chu = models.TextField(blank=True, null=True)
    
    # --- THÊM 2 DÒNG NÀY VÀO ---
    ngay_hoan_tat = models.DateField(blank=True, null=True)
    ghi_chu_hoan_tat = models.TextField(blank=True, null=True)
    class Meta:
        db_table = 'lich_su_sua_chua'

# Thêm vào cuối file hethong/models.py
class VatTu(models.Model):
    ma_vat_tu = models.CharField(max_length=50, blank=True, null=True)
    ten_vat_tu = models.CharField(max_length=255)
    so_luong = models.IntegerField(default=0)
    han_su_dung = models.DateField(blank=True, null=True)
    noi_de_vat_tu = models.CharField(max_length=255, blank=True, null=True)
    is_tieu_hao = models.BooleanField(default=False) # Mặc định là không đánh dấu

    class Meta:
        db_table = 'vat_tu'


# --- Thêm vào cuối file hethong/models.py ---
class PhieuNhapKho(models.Model):
    ma_phieu = models.CharField(max_length=50, unique=True)
    ngay_phieu = models.DateField()
    khoa_phong = models.ForeignKey(KhoaPhong, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'phieu_nhap_kho'

class ChiTietPhieuNhap(models.Model):
    phieu_nhap = models.ForeignKey(PhieuNhapKho, on_delete=models.CASCADE)
    vat_tu = models.ForeignKey(VatTu, on_delete=models.CASCADE)
    so_luong = models.IntegerField()

    class Meta:
        db_table = 'chi_tiet_phieu_nhap'

# --- Thêm vào cuối file hethong/models.py ---
class PhieuXuatKho(models.Model):
    ma_phieu = models.CharField(max_length=50, unique=True)
    ngay_phieu = models.DateField()
    
    # Khoa xuất (Đổi related_name để không bị lỗi xung đột)
    khoa_phong = models.ForeignKey(KhoaPhong, on_delete=models.SET_NULL, null=True, blank=True, related_name='phieu_xuat_kho')
    
    # THÊM MỚI: Khoa nhận (Khoa sẽ được cộng số lượng)
    khoa_nhan = models.ForeignKey(KhoaPhong, on_delete=models.SET_NULL, null=True, blank=True, related_name='phieu_nhan_kho')

    class Meta:
        db_table = 'phieu_xuat_kho'

class ChiTietPhieuXuat(models.Model):
    phieu_xuat = models.ForeignKey(PhieuXuatKho, on_delete=models.CASCADE)
    vat_tu = models.ForeignKey(VatTu, on_delete=models.CASCADE)
    so_luong = models.IntegerField()

    class Meta:
        db_table = 'chi_tiet_phieu_xuat'

class HinhAnhThanhLy(models.Model):
    thiet_bi = models.ForeignKey(ThietBi, related_name='danh_sach_anh_thanh_ly', on_delete=models.CASCADE)
    hinh_anh = models.ImageField(upload_to='thanhly/')

class NhanVien(models.Model):
    ma_nhan_vien = models.CharField(max_length=50, null=True, blank=True) # Có thể bỏ trống
    ten_nhan_vien = models.CharField(max_length=255) # Bắt buộc nhập

    class Meta:
        db_table = 'nhan_vien'

    def __str__(self):
        return self.ten_nhan_vien

# --- THÊM VÀO CUỐI FILE models.py ---
TRANG_THAI_GIAO_BAN = [
    ('Đã hoàn thành', 'Đã hoàn thành'),
    ('Đang xử lý', 'Đang xử lý'),
    ('Chưa xử lý', 'Chưa xử lý'),
    ('Cần theo dõi thêm', 'Cần theo dõi thêm'),
    ('Khác', 'Khác'),
]

class GiaoBanCNTT(models.Model):
    ngay_giao_ban = models.DateField()
    khoa_phong = models.ForeignKey(KhoaPhong, on_delete=models.CASCADE)
    nhan_vien = models.ForeignKey(NhanVien, on_delete=models.CASCADE)
    tinh_trang_tiep_nhan = models.TextField()
    cach_xu_ly = models.TextField()
    trang_thai = models.CharField(max_length=50, choices=TRANG_THAI_GIAO_BAN)
    ghi_chu = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'giao_ban_cntt'


# --- THÊM VÀO CUỐI FILE models.py ---
class TonKhoKhoaPhong(models.Model):
    khoa_phong = models.ForeignKey(KhoaPhong, on_delete=models.CASCADE)
    vat_tu = models.ForeignKey(VatTu, on_delete=models.CASCADE)
    so_luong = models.IntegerField(default=0)
    so_luong_hong = models.IntegerField(default=0) # THÊM DÒNG NÀY ĐỂ LƯU ĐỒ HỎNG

    class Meta:
        db_table = 'ton_kho_khoa_phong'
        # Đảm bảo mỗi khoa phòng chỉ có 1 dòng tồn kho cho 1 loại vật tư
        unique_together = ('khoa_phong', 'vat_tu')


# --- THÊM VÀO CUỐI FILE models.py ---
class LichSuBaoHong(models.Model):
    vat_tu = models.ForeignKey(VatTu, on_delete=models.CASCADE)
    khoa_xuat = models.ForeignKey(KhoaPhong, related_name='khoa_xuat_hong', on_delete=models.CASCADE)
    khoa_nhan = models.ForeignKey(KhoaPhong, related_name='khoa_nhan_hong', on_delete=models.CASCADE)
    so_luong = models.IntegerField()
    ngay_bao_hong = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lich_su_bao_hong'

# --- THÊM VÀO CUỐI FILE models.py ---
class LichSuTieuHao(models.Model):
    vat_tu = models.ForeignKey(VatTu, on_delete=models.CASCADE)
    # Khoa xuất (Khoa đang giữ tồn kho)
    khoa_xuat = models.ForeignKey(KhoaPhong, related_name='khoa_xuat_tieu_hao', on_delete=models.CASCADE)
    # Khoa nhận (Khoa lấy ra để sử dụng)
    khoa_nhan = models.ForeignKey(KhoaPhong, related_name='khoa_nhan_tieu_hao', on_delete=models.CASCADE)
    so_luong = models.IntegerField()
    ngay_tieu_hao = models.DateTimeField(auto_now_add=True)
    is_hong = models.BooleanField(default=False)

    class Meta:
        db_table = 'lich_su_tieu_hao'