from django.shortcuts import render, redirect # Thêm redirect
from .models import TaiKhoan, KhoaPhong, ThietBi ,LOAI_THIET_BI_CHOICES, LichSuSuaChua,VatTu,PhieuNhapKho,ChiTietPhieuNhap,PhieuXuatKho,ChiTietPhieuXuat,HinhAnhThanhLy,NhanVien,GiaoBanCNTT,TonKhoKhoaPhong,LichSuBaoHong,LichSuTieuHao
from django.db.models import Q,Count , Max
from django.http import JsonResponse
from django.core.paginator import Paginator
import openpyxl
import pdfkit # Import thư viện mới
from django.http import HttpResponse
from django.template.loader import render_to_string # Đổi get_template thành render_to_string
import json, random, string
from django.http import JsonResponse
from django.db.models import Count, Sum
import json
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
def login_view(request):
    if request.session.get('is_login'):
        return redirect('dashboard')
    
    thong_bao_loi = ""
    if request.method == "POST":
        u = request.POST.get('nhap_username')
        p = request.POST.get('nhap_password')
        try:
            nguoi_dung = TaiKhoan.objects.get(username=u, password=p)
            request.session['is_login'] = True # Lưu trạng thái đăng nhập
            request.session['username'] = nguoi_dung.username
            return redirect('dashboard') # Chuyển hướng sang trang dashboard
        except TaiKhoan.DoesNotExist:
            thong_bao_loi = "Tài khoản hoặc mật khẩu không đúng!"
    return render(request, 'login_custom.html', {'error': thong_bao_loi})

def dashboard_view(request):
    if not request.session.get('is_login'): 
        return redirect('dang_nhap')
    
    # Đếm số liệu cho 4 thẻ Thống kê ở trên cùng
    tong_thiet_bi = ThietBi.objects.count()
    dang_bao_tri = ThietBi.objects.filter(dang_sua_chua=True).count()
    
    # LẤY 10 BÁO CÁO SỬA CHỮA MỚI NHẤT ĐỂ ĐƯA RA TRANG CHỦ
    lich_su_moi = LichSuSuaChua.objects.select_related(
        'thiet_bi', 'thiet_bi__khoa_phong'
    ).order_by('-ngay_sua_chua', '-id')[:10]

    return render(request, 'dashboard.html', {
        'tong_thiet_bi': tong_thiet_bi,
        'dang_bao_tri': dang_bao_tri,
        'lich_su_moi': lich_su_moi,
        # Bạn có thể truyền thêm yêu_cầu_mới hoặc nhân_sự_it vào đây nếu có database
    })

def logout_view(request):
    request.session.flush() # Xóa sạch session
    return redirect('dang_nhap')

def them_khoa_phong_view(request):
    if not request.session.get('is_login'):
        return redirect('dang_nhap')

    thong_bao = ""
    thong_bao_loi = ""

    if request.method == "POST":
        ma = request.POST.get('ma_khoa_phong', '').strip()
        ten = request.POST.get('ten_khoa_phong', '').strip()

        if ten:
            KhoaPhong.objects.create(ma_khoa_phong=ma, ten_khoa_phong=ten)
            thong_bao = f"Đã thêm khoa/phòng '{ten}' thành công!"
        else:
            thong_bao_loi = "Tên khoa phòng là bắt buộc!"

    # Lấy toàn bộ danh sách khoa phòng, sắp xếp mới nhất lên đầu
    danh_sach_kp = KhoaPhong.objects.all().order_by('-id')

    return render(request, 'them_khoaphong.html', {
        'thong_bao': thong_bao,
        'thong_bao_loi': thong_bao_loi,
        'danh_sach_kp': danh_sach_kp # Truyền dữ liệu ra ngoài giao diện
    })

# HÀM XỬ LÝ XÓA
def xoa_khoa_phong_view(request, id):
    if not request.session.get('is_login'):
        return redirect('dang_nhap')
    
    # Tìm và xóa bản ghi theo ID
    KhoaPhong.objects.filter(id=id).delete()
    return redirect('them_khoa_phong')

# HÀM XỬ LÝ SỬA
def sua_khoa_phong_view(request, id):
    if not request.session.get('is_login'):
        return redirect('dang_nhap')
    
    # Lấy thông tin khoa phòng hiện tại
    try:
        kp = KhoaPhong.objects.get(id=id)
    except KhoaPhong.DoesNotExist:
        return redirect('them_khoa_phong')

    if request.method == "POST":
        ma = request.POST.get('ma_khoa_phong', '').strip()
        ten = request.POST.get('ten_khoa_phong', '').strip()

        if ten:
            kp.ma_khoa_phong = ma
            kp.ten_khoa_phong = ten
            kp.save() # Cập nhật vào DB
            return redirect('them_khoa_phong')

    return render(request, 'sua_khoaphong.html', {'kp': kp})

def them_thiet_bi_view(request):
    if not request.session.get('is_login'):
        return redirect('dang_nhap')

    thong_bao = ""
    thong_bao_loi = ""

    if request.method == "POST":
        ma = request.POST.get('ma_thiet_bi', '').strip()
        ten = request.POST.get('ten_thiet_bi', '').strip()
        ngay = request.POST.get('ngay_su_dung', '') 
        loai = request.POST.get('loai_thiet_bi', '')
        kp_id = request.POST.get('khoa_phong', '')

        if ten and loai:
            tb = ThietBi(
                ten_thiet_bi=ten, 
                loai_thiet_bi=loai
            )
            if ma: tb.ma_thiet_bi = ma
            if ngay: tb.ngay_su_dung = ngay
            if kp_id: tb.khoa_phong_id = kp_id
            
            tb.save()
            thong_bao = f"Đã thêm thiết bị '{ten}' thành công!"
        else:
            thong_bao_loi = "Tên thiết bị và Loại thiết bị là bắt buộc!"

    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong')
    
    # Đã xóa đoạn query danh_sach_tb ở đây

    return render(request, 'them_thietbi.html', {
        'thong_bao': thong_bao,
        'thong_bao_loi': thong_bao_loi,
        'khoa_phongs': khoa_phongs,
        # Đã xóa danh_sach_tb khỏi thư viện trả về
    })
def danh_sach_tai_san_view(request):
    if not request.session.get('is_login'):
        return redirect('dang_nhap')

    query = request.GET.get('q', '').strip()
    kp_id = request.GET.get('khoa_phong', '')
    loai = request.GET.get('loai_thiet_bi', '')
    trang_thai = request.GET.get('trang_thai', '')
    
    # 1. NHẬN YÊU CẦU SẮP XẾP TỪ GIAO DIỆN
    sort_by = request.GET.get('sort_by', '') 

    # 2. DÙNG COUNT ĐỂ ĐẾM SỐ LẦN SỬA CHỮA TỪ BẢNG LỊCH SỬ
    danh_sach_tb = ThietBi.objects.select_related('khoa_phong').filter(is_thanh_ly=False).annotate(
        so_lan_sua=Count('lichsusuachua')
    )

    # 3. CHẠY BỘ LỌC
    if query:
        danh_sach_tb = danh_sach_tb.filter(
            Q(ten_thiet_bi__unaccent__icontains=query) | 
            Q(ma_thiet_bi__unaccent__icontains=query)
        )
    if kp_id:
        danh_sach_tb = danh_sach_tb.filter(khoa_phong_id=kp_id)
    if loai:
        danh_sach_tb = danh_sach_tb.filter(loai_thiet_bi=loai)
        
   
    if trang_thai == 'dang_sua':
        danh_sach_tb = danh_sach_tb.filter(dang_sua_chua=True)
    elif trang_thai == 'binh_thuong':
        danh_sach_tb = danh_sach_tb.filter(dang_sua_chua=False, is_hong_han=False)
    elif trang_thai == 'hong_han': # <-- THÊM DÒNG NÀY
        danh_sach_tb = danh_sach_tb.filter(is_hong_han=True)

    # 4. CHẠY LỆNH SẮP XẾP 
    if sort_by == 'asc':
        danh_sach_tb = danh_sach_tb.order_by('so_lan_sua', '-id') # Tăng dần
    elif sort_by == 'desc':
        danh_sach_tb = danh_sach_tb.order_by('-so_lan_sua', '-id') # Giảm dần
    else:
        danh_sach_tb = danh_sach_tb.order_by('-id') # Mặc định: Mới nhất lên đầu

    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong')

    return render(request, 'danhsach_taisan.html', {
        'danh_sach_tb': danh_sach_tb,
        'khoa_phongs': khoa_phongs,
        'loai_choices': LOAI_THIET_BI_CHOICES,
        'q_value': query,
        'kp_value': kp_id,
        'loai_value': loai,
        'trang_thai_value': trang_thai,
        'sort_by': sort_by, # Trả về để ghi nhớ đang sắp xếp kiểu gì
        'tong_so': danh_sach_tb.count()
    })

# --- HÀM XỬ LÝ XÓA THIẾT BỊ ---
def xoa_thiet_bi_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    ThietBi.objects.filter(id=id).delete()
    return redirect('danh_sach_tai_san')

# --- HÀM XỬ LÝ SỬA THIẾT BỊ ---
def sua_thiet_bi_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    
    try:
        tb = ThietBi.objects.get(id=id)
    except ThietBi.DoesNotExist:
        return redirect('danh_sach_tai_san')

    if request.method == "POST":
        ma = request.POST.get('ma_thiet_bi', '').strip()
        ten = request.POST.get('ten_thiet_bi', '').strip()
        ngay = request.POST.get('ngay_su_dung', '') 
        loai = request.POST.get('loai_thiet_bi', '')
        kp_id = request.POST.get('khoa_phong', '')

        if ten and loai:
            tb.ma_thiet_bi = ma
            tb.ten_thiet_bi = ten
            tb.loai_thiet_bi = loai
            # Cập nhật ngày và khoa phòng (nếu rỗng thì lưu null)
            tb.ngay_su_dung = ngay if ngay else None
            tb.khoa_phong_id = kp_id if kp_id else None
            
            tb.save()
            return redirect('danh_sach_tai_san')

    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong')
    return render(request, 'sua_thietbi.html', {
        'tb': tb, 
        'khoa_phongs': khoa_phongs,
        'loai_choices': LOAI_THIET_BI_CHOICES
    })
# Mở file hethong/views.py và SỬA LẠI HÀM NÀY:

def luu_sua_chua_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    
    if request.method == "POST":
        tb_id = request.POST.get('thiet_bi_id')
        ngay = request.POST.get('ngay_sua_chua')
        ghi_chu = request.POST.get('ghi_chu')
        
        # 1. Gọi thiết bị ra từ Database
        tb = ThietBi.objects.get(id=tb_id)
        
        # 2. KIỂM TRA CHẶN: Nếu thiết bị ĐÃ ĐANG SỬA thì chặn lại ngay, không lưu gì cả
        if tb.dang_sua_chua == True:
            return redirect('danh_sach_tai_san')
            
        # 3. Nếu chưa sửa, thì tạo lịch sử sửa chữa mới
        LichSuSuaChua.objects.create(
            thiet_bi_id=tb_id,
            ngay_sua_chua=ngay,
            ghi_chu=ghi_chu
        )
        
        # 4. QUAN TRỌNG NHẤT: Bật cờ "Đang sửa chữa" lên và lưu lại
        tb.dang_sua_chua = True
        tb.save() # Bắt buộc phải có dòng này thì UI mới đổi màu được
        
    return redirect('danh_sach_tai_san')

# THÊM HÀM MỚI NÀY XUỐNG DƯỚI CÙNG
def hoan_tat_sua_chua_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    
    if request.method == "POST":
        tb_id = request.POST.get('thiet_bi_id')
        ngay_xong = request.POST.get('ngay_hoan_tat')
        ghi_chu_xong = request.POST.get('ghi_chu_hoan_tat')
        # Nhận giá trị từ Checkbox (Nếu có check thì là 'on')
        check_hong = request.POST.get('check_hong_han') == 'on'
        
        try:
            tb = ThietBi.objects.get(id=tb_id)
            
            # 1. Trả thiết bị về trạng thái bình thường (Hết tô đỏ)
            tb.dang_sua_chua = False
            tb.is_hong_han = check_hong # LƯU TRẠNG THÁI VÀO DATABASE
            tb.save()
            
            # 2. Tìm phiếu sửa chữa gần nhất của thiết bị này và điền ngày hoàn tất vào
            phieu_cuoi = LichSuSuaChua.objects.filter(thiet_bi_id=tb_id).order_by('-id').first()
            if phieu_cuoi:
                phieu_cuoi.ngay_hoan_tat = ngay_xong
                phieu_cuoi.ghi_chu_hoan_tat = ghi_chu_xong
                phieu_cuoi.save()
                
        except ThietBi.DoesNotExist:
            pass
            
    return redirect('danh_sach_tai_san')

def lay_lich_su_sua_chua_api(request, tb_id):
    # Lấy toàn bộ lịch sử của thiết bị, sắp xếp mới nhất lên đầu
    lich_su = LichSuSuaChua.objects.filter(thiet_bi_id=tb_id).order_by('-id')
    
    tong_so_lan = lich_su.count()
    
    # Phân trang: 20 bản ghi mỗi trang
    page_number = request.GET.get('page', 1)
    paginator = Paginator(lich_su, 20)
    page_obj = paginator.get_page(page_number)
    
    data = []
    for ls in page_obj:
        # Xử lý định dạng ngày tháng an toàn
        if hasattr(ls, 'ngay_sua_chua') and ls.ngay_sua_chua:
            ngay_sua_str = ls.ngay_sua_chua.strftime('%d/%m/%Y')
        elif hasattr(ls, 'ngay_sua') and ls.ngay_sua:
            ngay_sua_str = ls.ngay_sua.strftime('%d/%m/%Y')
        else:
            ngay_sua_str = "---"

        data.append({
            'id': ls.id, # Bắt buộc phải có ID để truyền ra nút in
            'ngay_sua': ngay_sua_str,
            'ghi_chu': ls.ghi_chu or "",
            'ngay_ht': ls.ngay_hoan_tat.strftime('%d/%m/%Y') if ls.ngay_hoan_tat else "Chưa xong",
            'ghi_chu_ht': ls.ghi_chu_hoan_tat or ""
        })
        
    return JsonResponse({
        'lich_su': data,
        'tong_so_lan': tong_so_lan,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages
    })

# HÀM XỬ LÝ TRANG BÁO CÁO SỬA CHỮA
def bao_cao_sua_chua_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')

    # 1. Nhận các tham số lọc từ URL
    tu_ngay = request.GET.get('tu_ngay', '')
    den_ngay = request.GET.get('den_ngay', '')
    query = request.GET.get('q', '').strip()
    kp_id = request.GET.get('khoa_phong', '')
    loai = request.GET.get('loai_thiet_bi', '')

    # 2. Truy vấn từ bảng Lịch Sử Sửa Chữa (Lấy kèm thông tin Thiết bị để tối ưu)
    lich_su = LichSuSuaChua.objects.select_related('thiet_bi', 'thiet_bi__khoa_phong').all().order_by('-ngay_sua_chua', '-id')

    # 3. Áp dụng các bộ lọc
    if tu_ngay:
        lich_su = lich_su.filter(ngay_sua_chua__gte=tu_ngay) # gte: Lớn hơn hoặc bằng
    if den_ngay:
        lich_su = lich_su.filter(ngay_sua_chua__lte=den_ngay) # lte: Nhỏ hơn hoặc bằng
    if query:
        lich_su = lich_su.filter(thiet_bi__ten_thiet_bi__unaccent__icontains=query)
    if kp_id:
        lich_su = lich_su.filter(thiet_bi__khoa_phong_id=kp_id)
    if loai:
        lich_su = lich_su.filter(thiet_bi__loai_thiet_bi=loai)

    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong')

    return render(request, 'baocao_suachua.html', {
        'lich_su': lich_su,
        'khoa_phongs': khoa_phongs,
        'loai_choices': LOAI_THIET_BI_CHOICES,
        'tu_ngay': tu_ngay,
        'den_ngay': den_ngay,
        'q_value': query,
        'kp_value': kp_id,
        'loai_value': loai,
        'tong_so': lich_su.count()
    })

# --- 1. Hàm hỗ trợ: Lọc dữ liệu dùng chung ---
def lay_du_lieu_bao_cao_da_loc(request):
    tu_ngay = request.GET.get('tu_ngay', '')
    den_ngay = request.GET.get('den_ngay', '')
    query = request.GET.get('q', '').strip()
    kp_id = request.GET.get('khoa_phong', '')
    loai = request.GET.get('loai_thiet_bi', '')

    lich_su = LichSuSuaChua.objects.select_related('thiet_bi', 'thiet_bi__khoa_phong').all().order_by('-ngay_sua_chua', '-id')

    if tu_ngay: lich_su = lich_su.filter(ngay_sua_chua__gte=tu_ngay)
    if den_ngay: lich_su = lich_su.filter(ngay_sua_chua__lte=den_ngay)
    if query: lich_su = lich_su.filter(thiet_bi__ten_thiet_bi__unaccent__icontains=query)
    if kp_id: lich_su = lich_su.filter(thiet_bi__khoa_phong_id=kp_id)
    if loai: lich_su = lich_su.filter(thiet_bi__loai_thiet_bi=loai)
    
    return lich_su

# --- 2. Hàm Xuất Excel ---
def xuat_excel_sua_chua(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    
    lich_su = lay_du_lieu_bao_cao_da_loc(request)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="BaoCao_SuaChua_ThietBi.xlsx"'
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Báo Cáo Sửa Chữa'
    
    # Ghi tiêu đề cột
    columns = ['STT', 'Mã TB', 'Tên Thiết Bị', 'Loại', 'Khoa Phòng', 'Ngày Báo Hỏng', 'Nội Dung Lỗi', 'Ngày Hoàn Tất', 'Tình Trạng']
    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.value = column_title
        cell.font = openpyxl.styles.Font(bold=True)
        
    # Ghi dữ liệu
    for index, ls in enumerate(lich_su, 1):
        tinh_trang = "Đã Xong" if ls.ngay_hoan_tat else "Đang sửa"
        ngay_ht = ls.ngay_hoan_tat.strftime('%d/%m/%Y') if ls.ngay_hoan_tat else "---"
        
        row = [
            index,
            ls.thiet_bi.ma_thiet_bi or "---",
            ls.thiet_bi.ten_thiet_bi,
            ls.thiet_bi.loai_thiet_bi,
            ls.thiet_bi.khoa_phong.ten_khoa_phong if ls.thiet_bi.khoa_phong else "---",
            ls.ngay_sua_chua.strftime('%d/%m/%Y'),
            ls.ghi_chu,
            ngay_ht,
            tinh_trang
        ]
        for col_num, cell_value in enumerate(row, 1):
            worksheet.cell(row=index+1, column=col_num).value = cell_value
            
    workbook.save(response)
    return response

# --- 3. Hàm Xuất PDF ---
def xuat_pdf_sua_chua(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    
    # 1. Lấy dữ liệu
    lich_su = lay_du_lieu_bao_cao_da_loc(request)
    
    # 2. Đổ dữ liệu vào file HTML
    html_string = render_to_string('pdf_baocao_suachua.html', {'lich_su': lich_su})
    
    # 3. Chỉ đường dẫn tới phần mềm lõi bạn vừa cài ở Bước 2
    # LƯU Ý: Chữ r ở đầu chuỗi là bắt buộc trên Windows để tránh lỗi dấu gạch chéo
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    
    # Cấu hình lề cho PDF và ép khổ giấy A4, xoay ngang (Landscape)
    options = {
        'page-size': 'A4',
        'orientation': 'Landscape',
        'margin-top': '1cm',
        'margin-right': '1cm',
        'margin-bottom': '1cm',
        'margin-left': '1cm',
        'encoding': "UTF-8",
    }
    
    # 4. Tạo file PDF
    pdf = pdfkit.from_string(html_string, False, configuration=config, options=options)
    
    # 5. Trả file về cho trình duyệt tải xuống
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="BaoCao_SuaChua.pdf"'
    
    return response

# HÀM XỬ LÝ THÊM VẬT TƯ
def them_vat_tu_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')

    thong_bao = ""
    thong_bao_loi = ""

    # TÌM VÀ SỬA LẠI ĐOẠN LẤY DỮ LIỆU NHƯ SAU:
    if request.method == "POST":
        ma = request.POST.get('ma_vat_tu', '').strip()
        ten = request.POST.get('ten_vat_tu', '').strip()
        noi_de = request.POST.get('noi_de_vat_tu', '').strip()
        ghi_chu = request.POST.get('ghi_chu', '').strip()
        han_sd = request.POST.get('han_su_dung', '') 
        
        # Nhận giá trị từ Checkbox (nếu có check thì nó trả về 'on')
        is_tieu_hao = request.POST.get('is_tieu_hao') == 'on'

        if ten:
            if not ma:
                while True:
                    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                    ma = f"VT{random_str}"
                    if not VatTu.objects.filter(ma_vat_tu=ma).exists():
                        break

            # TRUYỀN THÊM BIẾN is_tieu_hao VÀO ĐÂY
            vt = VatTu(ten_vat_tu=ten, ma_vat_tu=ma, noi_de_vat_tu=noi_de, ghi_chu=ghi_chu, is_tieu_hao=is_tieu_hao)
            if han_sd: vt.han_su_dung = han_sd
            
            vt.save()
            thong_bao = f"Đã thêm vật tư '{ten}' thành công!"
        else:
            thong_bao_loi = "Tên vật tư là thông tin bắt buộc!"

    return render(request, 'them_vattu.html', {
        'thong_bao': thong_bao,
        'thong_bao_loi': thong_bao_loi,
    })

# Thêm vào cuối file views.py
def danh_sach_vat_tu_view(request):
    if not request.session.get('is_login'):
        return redirect('dang_nhap')

    query = request.GET.get('q', '').strip()
    
    # Lấy toàn bộ danh sách vật tư, sắp xếp mới nhất lên đầu
    danh_sach_vt = VatTu.objects.all().order_by('-id')

    # Lọc nếu người dùng có gõ tìm kiếm
    if query:
        danh_sach_vt = danh_sach_vt.filter(
            Q(ten_vat_tu__unaccent__icontains=query) | 
            Q(ma_vat_tu__unaccent__icontains=query)
        )

    # THÊM DÒNG NÀY ĐỂ TRUYỀN VÀO POPUP:
    danh_sach_tat_ca_vt = VatTu.objects.all().order_by('ten_vat_tu')
    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong')

    return render(request, 'danhsach_vattu.html', {
        'khoa_phongs': khoa_phongs,
        'danh_sach_vt': danh_sach_vt,
        'danh_sach_tat_ca_vt': danh_sach_tat_ca_vt, # TRUYỀN THÊM BIẾN NÀY
        'q_value': query,
        'tong_so': danh_sach_vt.count()
    })

# --- HÀM XỬ LÝ XÓA VẬT TƯ ---
def xoa_vat_tu_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    VatTu.objects.filter(id=id).delete()
    return redirect('danh_sach_vat_tu')

# --- HÀM XỬ LÝ SỬA VẬT TƯ ---
def sua_vat_tu_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    
    try:
        vt = VatTu.objects.get(id=id)
    except VatTu.DoesNotExist:
        return redirect('danh_sach_vat_tu')

    # TÌM VÀ SỬA LẠI ĐOẠN LẤY DỮ LIỆU NHƯ SAU:
    if request.method == "POST":
        ma = request.POST.get('ma_vat_tu', '').strip()
        ten = request.POST.get('ten_vat_tu', '').strip()
        noi_de = request.POST.get('noi_de_vat_tu', '').strip()
        ghi_chu = request.POST.get('ghi_chu', '').strip()
        han_sd = request.POST.get('han_su_dung', '') 
        
        is_tieu_hao = request.POST.get('is_tieu_hao') == 'on'

        if ten:
            if not ma:
                while True:
                    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                    ma = f"VT{random_str}"
                    if not VatTu.objects.filter(ma_vat_tu=ma).exists():
                        break

            vt.ma_vat_tu = ma
            vt.ten_vat_tu = ten
            vt.noi_de_vat_tu = noi_de
            vt.ghi_chu = ghi_chu
            vt.han_su_dung = han_sd if han_sd else None
            
            # CẬP NHẬT LẠI TRẠNG THÁI TIÊU HAO VÀ LƯU
            vt.is_tieu_hao = is_tieu_hao
            vt.save()
            return redirect('danh_sach_vat_tu')

    return render(request, 'sua_vattu.html', {'vt': vt})

# --- HÀM API LƯU PHIẾU NHẬP KHO ---
# --- HÀM API LƯU PHIẾU NHẬP KHO (CẬP NHẬT THEO KHOA PHÒNG) ---
def luu_phieu_nhap_kho_api(request):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error', 'msg': 'Chưa đăng nhập'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ma_phieu = data.get('ma_phieu', '').strip()
            ngay_phieu = data.get('ngay_phieu')
            khoa_phong_id = data.get('khoa_phong_id') # Lấy khoa phòng từ giao diện
            items = data.get('items', [])

            if not ngay_phieu or len(items) == 0:
                return JsonResponse({'status': 'error', 'msg': 'Thiếu ngày phiếu hoặc chưa có vật tư nào trong lưới!'})
            
            # Bắt buộc phải chọn Khoa Phòng nhập vì hệ thống quản lý tồn theo phòng
            if not khoa_phong_id:
                return JsonResponse({'status': 'error', 'msg': 'Vui lòng chọn Khoa / Phòng nhập kho!'})

            # TỰ TẠO MÃ NẾU ĐỂ TRỐNG (BVSN + 4 ký tự ngẫu nhiên)
            if not ma_phieu:
                while True:
                    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                    ma_phieu = f"BVSN{random_str}"
                    if not PhieuNhapKho.objects.filter(ma_phieu=ma_phieu).exists():
                        break

            # 1. Lưu Header Phiếu (Có kèm khoa phòng)
            phieu = PhieuNhapKho.objects.create(ma_phieu=ma_phieu, ngay_phieu=ngay_phieu, khoa_phong_id=khoa_phong_id)

            # 2. Lưu Chi tiết & Cộng số lượng tồn kho VÀO KHOA PHÒNG ĐƯỢC CHỌN
            for item in items:
                vt_id = item['vt_id']
                sl = int(item['so_luong'])
                
                vt = VatTu.objects.get(id=vt_id)
                ChiTietPhieuNhap.objects.create(phieu_nhap=phieu, vat_tu=vt, so_luong=sl)
                
                # Tìm bản ghi tồn kho của phòng này, nếu chưa có thì tạo mới bằng 0 và cộng dồn vào
                ton_kho, created = TonKhoKhoaPhong.objects.get_or_create(
                    khoa_phong_id=khoa_phong_id,
                    vat_tu=vt,
                    defaults={'so_luong': 0}
                )
                ton_kho.so_luong += sl
                ton_kho.save()

            return JsonResponse({'status': 'success', 'msg': 'Đã lưu phiếu nhập kho thành công!'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})

def danh_sach_phieu_nhap_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')

    tu_ngay = request.GET.get('tu_ngay', '')
    den_ngay = request.GET.get('den_ngay', '')
    
    # Lấy danh sách phiếu, đếm xem mỗi phiếu có bao nhiêu loại vật tư và tổng số lượng
    danh_sach_phieu = PhieuNhapKho.objects.annotate(
        so_mon=Count('chitietphieunhap'),
        tong_sl=Sum('chitietphieunhap__so_luong')
    ).order_by('-ngay_phieu', '-id')

    # Lọc theo ngày
    if tu_ngay:
        danh_sach_phieu = danh_sach_phieu.filter(ngay_phieu__gte=tu_ngay)
    if den_ngay:
        danh_sach_phieu = danh_sach_phieu.filter(ngay_phieu__lte=den_ngay)

    return render(request, 'danhsach_phieunhap.html', {
        'danh_sach_phieu': danh_sach_phieu,
        'tu_ngay': tu_ngay,
        'den_ngay': den_ngay,
        'tong_so': danh_sach_phieu.count()
    })

# 2. HÀM API TRẢ VỀ CHI TIẾT KHI NHÁY ĐÚP CHUỘT
def chi_tiet_phieu_nhap_api(request, phieu_id):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error'})
    
    # Lấy thông tin khoa phòng đã nhập kèm theo phiếu
    try:
        phieu = PhieuNhapKho.objects.select_related('khoa_phong').get(id=phieu_id)
        ten_khoa = phieu.khoa_phong.ten_khoa_phong if phieu.khoa_phong else "Chưa phân bổ"
    except Exception:
        ten_khoa = "---"

    chi_tiet = ChiTietPhieuNhap.objects.filter(phieu_nhap_id=phieu_id).select_related('vat_tu')
    data = []
    for ct in chi_tiet:
        data.append({
            'ma_vt': ct.vat_tu.ma_vat_tu or '---',
            'ten_vt': ct.vat_tu.ten_vat_tu,
            'so_luong': ct.so_luong
        })
        
    return JsonResponse({'status': 'success', 'ten_khoa': ten_khoa, 'data': data})

def xoa_phieu_nhap_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    try:
        phieu = PhieuNhapKho.objects.get(id=id)
        
        # Lấy các chi tiết cũ ra để TRỪ số lượng khỏi kho
        chi_tiet_cu = ChiTietPhieuNhap.objects.filter(phieu_nhap=phieu)
        for ct in chi_tiet_cu:
            vt = ct.vat_tu
            vt.so_luong -= ct.so_luong
            if vt.so_luong < 0: vt.so_luong = 0 # Không để số âm
            vt.save()
            
        phieu.delete() # Xóa phiếu (các chi tiết sẽ tự xóa theo)
    except PhieuNhapKho.DoesNotExist:
        pass
    return redirect('danh_sach_phieu_nhap')

# 2. HÀM HIỂN THỊ TRANG SỬA PHIẾU
def sua_phieu_nhap_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    try:
        phieu = PhieuNhapKho.objects.get(id=id)
    except PhieuNhapKho.DoesNotExist:
        return redirect('danh_sach_phieu_nhap')

    danh_sach_tat_ca_vt = VatTu.objects.all().order_by('ten_vat_tu')
    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong') # Thêm dòng này

    chi_tiet_cu = ChiTietPhieuNhap.objects.filter(phieu_nhap=phieu)
    ds_luoi = []
    for ct in chi_tiet_cu:
        ds_luoi.append({
            'vt_id': str(ct.vat_tu.id),
            'ten_vt': ct.vat_tu.ten_vat_tu,
            'so_luong': ct.so_luong
        })

    return render(request, 'sua_phieunhap.html', {
        'phieu': phieu,
        'danh_sach_tat_ca_vt': danh_sach_tat_ca_vt,
        'khoa_phongs': khoa_phongs, # Thêm biến này
        'chi_tiet_json': json.dumps(ds_luoi)
    })

# 3. HÀM API LƯU CẬP NHẬT PHIẾU NHẬP
def cap_nhat_phieu_nhap_api(request, id):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error'})
    if request.method == 'POST':
        try:
            with transaction.atomic():
                phieu = PhieuNhapKho.objects.get(id=id)
                khoa_cu_id = phieu.khoa_phong_id # Ghi nhớ khoa cũ để trừ tồn kho

                data = json.loads(request.body)
                ngay_phieu = data.get('ngay_phieu')
                khoa_moi_id = data.get('khoa_phong_id') # Nhận khoa phòng mới từ giao diện
                items = data.get('items', [])

                if not ngay_phieu or not khoa_moi_id or len(items) == 0:
                    return JsonResponse({'status': 'error', 'msg': 'Thiếu ngày phiếu, khoa phòng hoặc danh sách vật tư!'})

                # BƯỚC A: HOÀN TÁC TRỪ SỐ LƯỢNG CŨ KHỎI KHO CỦA KHOA CŨ
                chi_tiet_cu = ChiTietPhieuNhap.objects.filter(phieu_nhap=phieu)
                for ct in chi_tiet_cu:
                    if khoa_cu_id:
                        try:
                            ton_kho_cu = TonKhoKhoaPhong.objects.get(khoa_phong_id=khoa_cu_id, vat_tu=ct.vat_tu)
                            ton_kho_cu.so_luong -= ct.so_luong
                            if ton_kho_cu.so_luong < 0: ton_kho_cu.so_luong = 0
                            ton_kho_cu.save()
                        except TonKhoKhoaPhong.DoesNotExist:
                            pass
                chi_tiet_cu.delete() # Xóa chi tiết cũ

                # BƯỚC B: Cập nhật thông tin Header của phiếu sang Khoa phòng mới
                phieu.ngay_phieu = ngay_phieu
                phieu.khoa_phong_id = khoa_moi_id
                phieu.save()

                # BƯỚC C: Lưu Chi tiết mới & Cộng số lượng vào tồn kho của KHOA PHÒNG MỚI
                for item in items:
                    vt = VatTu.objects.get(id=item['vt_id'])
                    sl = int(item['so_luong'])
                    
                    # Tạo chi tiết mới
                    ChiTietPhieuNhap.objects.create(phieu_nhap=phieu, vat_tu=vt, so_luong=sl)
                    
                    # Cộng dồn tồn kho vào khoa phòng mới được chọn
                    ton_kho_moi, created = TonKhoKhoaPhong.objects.get_or_create(
                        khoa_phong_id=khoa_moi_id,
                        vat_tu=vt,
                        defaults={'so_luong': 0}
                    )
                    ton_kho_moi.so_luong += sl
                    ton_kho_moi.save()

                return JsonResponse({'status': 'success', 'msg': 'Cập nhật phiếu nhập kho và điều chỉnh tồn kho thành công!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})
# --- HÀM API LƯU PHIẾU XUẤT KHO (CÓ XUẤT CHO KHOA KHÁC & CHECK TIÊU HAO) ---
def luu_phieu_xuat_kho_api(request):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error', 'msg': 'Chưa đăng nhập'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ma_phieu = data.get('ma_phieu', '').strip()
            ngay_phieu = data.get('ngay_phieu')
            khoa_xuat_id = data.get('khoa_xuat_id') # Khoa bị trừ
            khoa_nhan_id = data.get('khoa_nhan_id') # Khoa được cộng
            items = data.get('items', [])

            if not ngay_phieu or len(items) == 0:
                return JsonResponse({'status': 'error', 'msg': 'Thiếu ngày phiếu hoặc chưa có vật tư!'})
            if not khoa_xuat_id or not khoa_nhan_id:
                return JsonResponse({'status': 'error', 'msg': 'Vui lòng chọn đầy đủ Khoa Xuất và Khoa Nhận!'})
            if khoa_xuat_id == khoa_nhan_id:
                return JsonResponse({'status': 'error', 'msg': 'Khoa xuất và Khoa nhận không được trùng nhau!'})

            # BƯỚC 1: KIỂM TRA TỒN KHO TẠI KHOA XUẤT TRƯỚC (NẾU THIẾU THÌ BÁO LỖI)
            for item in items:
                vt = VatTu.objects.get(id=item['vt_id'])
                try:
                    ton_kho = TonKhoKhoaPhong.objects.get(khoa_phong_id=khoa_xuat_id, vat_tu=vt)
                    if ton_kho.so_luong < int(item['so_luong']):
                        return JsonResponse({'status': 'error', 'msg': f'Vật tư [{vt.ten_vat_tu}] tại khoa này chỉ còn {ton_kho.so_luong}, không đủ xuất!'})
                except TonKhoKhoaPhong.DoesNotExist:
                    return JsonResponse({'status': 'error', 'msg': f'Vật tư [{vt.ten_vat_tu}] không tồn tại trong kho của khoa xuất!'})

            # BƯỚC 2: TỰ TẠO MÃ NẾU ĐỂ TRỐNG
            if not ma_phieu:
                while True:
                    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                    ma_phieu = f"BVSX{random_str}"
                    if not PhieuXuatKho.objects.filter(ma_phieu=ma_phieu).exists():
                        break

            # BƯỚC 3: Lưu Header Phiếu
            phieu = PhieuXuatKho.objects.create(
                ma_phieu=ma_phieu, 
                ngay_phieu=ngay_phieu, 
                khoa_phong_id=khoa_xuat_id, 
                khoa_nhan_id=khoa_nhan_id
            )

            # BƯỚC 4: LƯU CHI TIẾT & XỬ LÝ SỐ LƯỢNG KHO
            for item in items:
                vt_id = item['vt_id']
                sl = int(item['so_luong'])
                
                vt = VatTu.objects.get(id=vt_id)
                # Vẫn lưu phiếu bình thường để báo cáo
                ChiTietPhieuXuat.objects.create(phieu_xuat=phieu, vat_tu=vt, so_luong=sl)
                
                # 4.1: TRỪ KHO XUẤT
                ton_kho_xuat = TonKhoKhoaPhong.objects.get(khoa_phong_id=khoa_xuat_id, vat_tu=vt)
                ton_kho_xuat.so_luong -= sl 
                ton_kho_xuat.save()

                # 4.2: CỘNG KHO NHẬN (Chỉ cộng nếu KHÔNG PHẢI VẬT TƯ TIÊU HAO)
                if not vt.is_tieu_hao:
                    ton_kho_nhan, created = TonKhoKhoaPhong.objects.get_or_create(
                        khoa_phong_id=khoa_nhan_id,
                        vat_tu=vt,
                        defaults={'so_luong': 0}
                    )
                    ton_kho_nhan.so_luong += sl
                    ton_kho_nhan.save()

            return JsonResponse({'status': 'success', 'msg': 'Đã xuất kho thành công!'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})

# ================= KHU VỰC QUẢN LÝ PHIẾU XUẤT KHO =================

# 1. HÀM HIỂN THỊ DANH SÁCH PHIẾU XUẤT
def danh_sach_phieu_xuat_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')

    tu_ngay = request.GET.get('tu_ngay', '')
    den_ngay = request.GET.get('den_ngay', '')
    
    danh_sach_phieu = PhieuXuatKho.objects.annotate(
        so_mon=Count('chitietphieuxuat'),
        tong_sl=Sum('chitietphieuxuat__so_luong')
    ).order_by('-ngay_phieu', '-id')

    if tu_ngay: danh_sach_phieu = danh_sach_phieu.filter(ngay_phieu__gte=tu_ngay)
    if den_ngay: danh_sach_phieu = danh_sach_phieu.filter(ngay_phieu__lte=den_ngay)

    return render(request, 'danhsach_phieuxuat.html', {
        'danh_sach_phieu': danh_sach_phieu,
        'tu_ngay': tu_ngay,
        'den_ngay': den_ngay,
        'tong_so': danh_sach_phieu.count()
    })

# 2. HÀM API TRẢ VỀ CHI TIẾT KHI NHÁY ĐÚP CHUỘT
def chi_tiet_phieu_xuat_api(request, phieu_id):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error'})
    
    try:
        phieu = PhieuXuatKho.objects.select_related('khoa_phong', 'khoa_nhan').get(id=phieu_id)
        ten_khoa_xuat = phieu.khoa_phong.ten_khoa_phong if phieu.khoa_phong else "Chưa phân bổ"
        ten_khoa_nhan = phieu.khoa_nhan.ten_khoa_phong if phieu.khoa_nhan else "Chưa phân bổ"
    except Exception:
        ten_khoa_xuat = "---"
        ten_khoa_nhan = "---"

    chi_tiet = ChiTietPhieuXuat.objects.filter(phieu_xuat_id=phieu_id).select_related('vat_tu')
    data = [{'ma_vt': ct.vat_tu.ma_vat_tu or '---', 'ten_vt': ct.vat_tu.ten_vat_tu, 'so_luong': ct.so_luong} for ct in chi_tiet]
    
    return JsonResponse({
        'status': 'success', 
        'ten_khoa_xuat': ten_khoa_xuat, 
        'ten_khoa_nhan': ten_khoa_nhan, 
        'data': data
    })

# 3. HÀM XÓA PHIẾU XUẤT (HOÀN TRẢ KHO)
def xoa_phieu_xuat_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    try:
        phieu = PhieuXuatKho.objects.get(id=id)
        # Hoàn trả số lượng vật tư bị xuất lại vào kho
        chi_tiet_cu = ChiTietPhieuXuat.objects.filter(phieu_xuat=phieu)
        for ct in chi_tiet_cu:
            vt = ct.vat_tu
            vt.so_luong += ct.so_luong
            vt.save()
        phieu.delete()
    except PhieuXuatKho.DoesNotExist:
        pass
    return redirect('danh_sach_phieu_xuat')

# 4. HÀM HIỂN THỊ TRANG SỬA PHIẾU XUẤT
def sua_phieu_xuat_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    try:
        phieu = PhieuXuatKho.objects.get(id=id)
    except PhieuXuatKho.DoesNotExist:
        return redirect('danh_sach_phieu_xuat')

    danh_sach_tat_ca_vt = VatTu.objects.all().order_by('ten_vat_tu')
    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong') # Thêm dòng này

    chi_tiet_cu = ChiTietPhieuXuat.objects.filter(phieu_xuat=phieu)
    ds_luoi = [{'vt_id': str(ct.vat_tu.id), 'ten_vt': ct.vat_tu.ten_vat_tu, 'so_luong': ct.so_luong} for ct in chi_tiet_cu]

    return render(request, 'sua_phieuxuat.html', {
        'phieu': phieu,
        'danh_sach_tat_ca_vt': danh_sach_tat_ca_vt,
        'khoa_phongs': khoa_phongs, # Truyền biến này ra giao diện
        'chi_tiet_json': json.dumps(ds_luoi)
    })

# 5. HÀM API LƯU CẬP NHẬT PHIẾU XUẤT
def cap_nhat_phieu_xuat_api(request, id):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error'})
    if request.method == 'POST':
        try:
            with transaction.atomic():
                phieu = PhieuXuatKho.objects.get(id=id)
                old_khoa_xuat_id = phieu.khoa_phong_id
                old_khoa_nhan_id = phieu.khoa_nhan_id

                data = json.loads(request.body)
                ngay_phieu = data.get('ngay_phieu')
                new_khoa_xuat_id = data.get('khoa_xuat_id')
                new_khoa_nhan_id = data.get('khoa_nhan_id')
                items = data.get('items', [])

                if not ngay_phieu or not new_khoa_xuat_id or not new_khoa_nhan_id or len(items) == 0:
                    return JsonResponse({'status': 'error', 'msg': 'Thiếu ngày phiếu, khoa phòng hoặc vật tư!'})
                if new_khoa_xuat_id == new_khoa_nhan_id:
                    return JsonResponse({'status': 'error', 'msg': 'Khoa xuất và Khoa nhận không được trùng nhau!'})

                # BƯỚC A: HOÀN TRẢ SỐ LƯỢNG CŨ VÀO KHO (Cộng trả lại khoa xuất cũ, trừ bớt khoa nhận cũ)
                chi_tiet_cu = ChiTietPhieuXuat.objects.filter(phieu_xuat=phieu).select_related('vat_tu')
                for ct in chi_tiet_cu:
                    if old_khoa_xuat_id:
                        ton_xuat_cu, _ = TonKhoKhoaPhong.objects.get_or_create(khoa_phong_id=old_khoa_xuat_id, vat_tu=ct.vat_tu, defaults={'so_luong': 0})
                        ton_xuat_cu.so_luong += ct.so_luong
                        ton_xuat_cu.save()
                    if old_khoa_nhan_id and not ct.vat_tu.is_tieu_hao:
                        try:
                            ton_nhan_cu = TonKhoKhoaPhong.objects.get(khoa_phong_id=old_khoa_nhan_id, vat_tu=ct.vat_tu)
                            ton_nhan_cu.so_luong -= ct.so_luong
                            if ton_nhan_cu.so_luong < 0: ton_nhan_cu.so_luong = 0
                            ton_nhan_cu.save()
                        except TonKhoKhoaPhong.DoesNotExist: pass
                chi_tiet_cu.delete()

                # BƯỚC B: KIỂM TRA ĐỦ TỒN KHO TẠI KHOA XUẤT MỚI
                for item in items:
                    vt = VatTu.objects.get(id=item['vt_id'])
                    try:
                        ton_kho_moi = TonKhoKhoaPhong.objects.get(khoa_phong_id=new_khoa_xuat_id, vat_tu=vt)
                        if ton_kho_moi.so_luong < int(item['so_luong']):
                            raise Exception(f"Vật tư [{vt.ten_vat_tu}] tại khoa xuất mới chỉ còn {ton_kho_moi.so_luong}, không đủ xuất!")
                    except TonKhoKhoaPhong.DoesNotExist:
                        raise Exception(f"Vật tư [{vt.ten_vat_tu}] không có trong kho của khoa xuất mới!")

                # BƯỚC C: TIẾN HÀNH LƯU VÀ ĐIỀU CHỈNH KHO MỚI
                phieu.ngay_phieu = ngay_phieu
                phieu.khoa_phong_id = new_khoa_xuat_id
                phieu.khoa_nhan_id = new_khoa_nhan_id
                phieu.save()

                for item in items:
                    vt = VatTu.objects.get(id=item['vt_id'])
                    sl = int(item['so_luong'])
                    ChiTietPhieuXuat.objects.create(phieu_xuat=phieu, vat_tu=vt, so_luong=sl)
                    
                    # Trừ kho khoa xuất mới
                    ton_xuat_moi = TonKhoKhoaPhong.objects.get(khoa_phong_id=new_khoa_xuat_id, vat_tu=vt)
                    ton_xuat_moi.so_luong -= sl
                    ton_xuat_moi.save()

                    # Cộng kho khoa nhận mới (Nếu không phải tiêu hao)
                    if not vt.is_tieu_hao:
                        ton_nhan_moi, _ = TonKhoKhoaPhong.objects.get_or_create(khoa_phong_id=new_khoa_nhan_id, vat_tu=vt, defaults={'so_luong': 0})
                        ton_nhan_moi.so_luong += sl
                        ton_nhan_moi.save()

                return JsonResponse({'status': 'success', 'msg': 'Cập nhật phiếu xuất kho và điều chỉnh tồn kho thành công!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})
# ================= BÁO CÁO TỔNG HỢP XUẤT - NHẬP - TỒN (ĐÃ FIX TỒN ĐẦU) =================
def bao_cao_nhap_xuat_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    from datetime import datetime
    from django.db.models import Q

    tu_ngay = request.GET.get('tu_ngay', '')
    den_ngay = request.GET.get('den_ngay', '')
    query = request.GET.get('q', '').strip()

    tu_date = None
    den_date = None
    try:
        if tu_ngay: tu_date = datetime.strptime(tu_ngay, '%Y-%m-%d').date()
        if den_ngay: den_date = datetime.strptime(den_ngay, '%Y-%m-%d').date()
    except ValueError: pass

    # Lấy danh sách vật tư
    danh_sach_vt = VatTu.objects.all().order_by('ten_vat_tu')
    if query:
        danh_sach_vt = danh_sach_vt.filter(Q(ten_vat_tu__unaccent__icontains=query) | Q(ma_vat_tu__unaccent__icontains=query))

    bao_cao = []
    for vt in danh_sach_vt:
        nhap_qs = ChiTietPhieuNhap.objects.filter(vat_tu=vt).select_related('phieu_nhap')
        xuat_qs = ChiTietPhieuXuat.objects.filter(vat_tu=vt).select_related('phieu_xuat')

        nhap_ky = 0
        xuat_ky = 0
        
        # Biến phụ: Lấy tổng số lượng nhập/xuất từ mốc "Từ ngày" cho đến THỜI ĐIỂM HIỆN TẠI
        nhap_tu_ngay_den_nay = 0
        xuat_tu_ngay_den_nay = 0

        # Quét lịch sử Nhập
        for n in nhap_qs:
            ngay = n.phieu_nhap.ngay_phieu
            if tu_date and ngay >= tu_date:
                nhap_tu_ngay_den_nay += n.so_luong
            if (not tu_date or ngay >= tu_date) and (not den_date or ngay <= den_date):
                nhap_ky += n.so_luong

        # Quét lịch sử Xuất
        for x in xuat_qs:
            ngay = x.phieu_xuat.ngay_phieu
            if tu_date and ngay >= tu_date:
                xuat_tu_ngay_den_nay += x.so_luong
            if (not tu_date or ngay >= tu_date) and (not den_date or ngay <= den_date):
                xuat_ky += x.so_luong

        # --- THUẬT TOÁN ĐI LÙI (REVERSE CALCULATION) ---
        if tu_date:
            # Tồn đầu = Tồn thực tế hiện tại - (Số đã nhập từ lúc đó đến nay) + (Số đã xuất từ lúc đó đến nay)
            ton_dau = vt.so_luong - nhap_tu_ngay_den_nay + xuat_tu_ngay_den_nay
        else:
            # Nếu không chọn "Từ ngày", Tồn đầu chính là số lượng vật tư lúc bạn gõ tay ở menu "Thêm vật tư"
            tong_nhap_all = sum([n.so_luong for n in nhap_qs])
            tong_xuat_all = sum([x.so_luong for x in xuat_qs])
            ton_dau = vt.so_luong - tong_nhap_all + tong_xuat_all

        # Tồn cuối kỳ = Tồn Đầu + Nhập trong kỳ - Xuất trong kỳ
        ton_cuoi = ton_dau + nhap_ky - xuat_ky

        # Đẩy ra giao diện
        if ton_dau != 0 or nhap_ky != 0 or xuat_ky != 0 or ton_cuoi != 0:
            bao_cao.append({
                'ma_vt': vt.ma_vat_tu or '---',
                'ten_vt': vt.ten_vat_tu,
                'ton_dau': ton_dau,
                'nhap_ky': nhap_ky,
                'xuat_ky': xuat_ky,
                'ton_cuoi': ton_cuoi
            })

    return render(request, 'baocao_nhapxuat.html', {
        'bao_cao': bao_cao,
        'tu_ngay': tu_ngay,
        'den_ngay': den_ngay,
        'q_value': query,
        'tong_so': len(bao_cao)
    })

# 1. HÀM HỖ TRỢ: CHUYÊN TÍNH TOÁN DỮ LIỆU NHẬP XUẤT TỒN (Dùng chung cho cả 3 hàm dưới)
def get_du_lieu_bao_cao_nhap_xuat(request):
    from datetime import datetime
    from django.db.models import Q

    tu_ngay = request.GET.get('tu_ngay', '')
    den_ngay = request.GET.get('den_ngay', '')
    query = request.GET.get('q', '').strip()

    tu_date = None
    den_date = None
    try:
        if tu_ngay: tu_date = datetime.strptime(tu_ngay, '%Y-%m-%d').date()
        if den_ngay: den_date = datetime.strptime(den_ngay, '%Y-%m-%d').date()
    except ValueError: pass

    danh_sach_vt = VatTu.objects.all().order_by('ten_vat_tu')
    if query:
        danh_sach_vt = danh_sach_vt.filter(Q(ten_vat_tu__unaccent__icontains=query) | Q(ma_vat_tu__unaccent__icontains=query))

    bao_cao = []
    for vt in danh_sach_vt:
        nhap_qs = ChiTietPhieuNhap.objects.filter(vat_tu=vt).select_related('phieu_nhap')
        xuat_qs = ChiTietPhieuXuat.objects.filter(vat_tu=vt).select_related('phieu_xuat')

        nhap_ky = 0
        xuat_ky = 0
        nhap_tu_ngay_den_nay = 0
        xuat_tu_ngay_den_nay = 0

        for n in nhap_qs:
            ngay = n.phieu_nhap.ngay_phieu
            if tu_date and ngay >= tu_date: nhap_tu_ngay_den_nay += n.so_luong
            if (not tu_date or ngay >= tu_date) and (not den_date or ngay <= den_date): nhap_ky += n.so_luong

        for x in xuat_qs:
            ngay = x.phieu_xuat.ngay_phieu
            if tu_date and ngay >= tu_date: xuat_tu_ngay_den_nay += x.so_luong
            if (not tu_date or ngay >= tu_date) and (not den_date or ngay <= den_date): xuat_ky += x.so_luong

        if tu_date:
            ton_dau = vt.so_luong - nhap_tu_ngay_den_nay + xuat_tu_ngay_den_nay
        else:
            tong_nhap_all = sum([n.so_luong for n in nhap_qs])
            tong_xuat_all = sum([x.so_luong for x in xuat_qs])
            ton_dau = vt.so_luong - tong_nhap_all + tong_xuat_all

        ton_cuoi = ton_dau + nhap_ky - xuat_ky

        if ton_dau != 0 or nhap_ky != 0 or xuat_ky != 0 or ton_cuoi != 0:
            bao_cao.append({
                'ma_vt': vt.ma_vat_tu or '---',
                'ten_vt': vt.ten_vat_tu,
                'ton_dau': ton_dau,
                'nhap_ky': nhap_ky,
                'xuat_ky': xuat_ky,
                'ton_cuoi': ton_cuoi
            })
    return bao_cao

# 2. HÀM GỐC: HIỂN THỊ LÊN TRÌNH DUYỆT (Đã gọi hàm hỗ trợ cho gọn)
def bao_cao_nhap_xuat_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    bao_cao = get_du_lieu_bao_cao_nhap_xuat(request)
    return render(request, 'baocao_nhapxuat.html', {
        'bao_cao': bao_cao,
        'tu_ngay': request.GET.get('tu_ngay', ''),
        'den_ngay': request.GET.get('den_ngay', ''),
        'q_value': request.GET.get('q', '').strip(),
        'tong_so': len(bao_cao)
    })

# 3. HÀM MỚI: XUẤT EXCEL
def xuat_excel_nhap_xuat(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    bao_cao = get_du_lieu_bao_cao_nhap_xuat(request)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="BaoCao_NhapXuatTon.xlsx"'
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Báo Cáo Xuất Nhập Tồn'
    
    # Ghi tiêu đề
    columns = ['STT', 'Mã Vật Tư', 'Tên Vật Tư', 'Tồn Đầu', 'Tổng Nhập', 'Tổng Xuất', 'Tồn Cuối Kỳ']
    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.value = column_title
        cell.font = openpyxl.styles.Font(bold=True)
        
    # Ghi dữ liệu
    for index, t in enumerate(bao_cao, 1):
        row = [index, t['ma_vt'], t['ten_vt'], t['ton_dau'], t['nhap_ky'], t['xuat_ky'], t['ton_cuoi']]
        for col_num, cell_value in enumerate(row, 1):
            worksheet.cell(row=index+1, column=col_num).value = cell_value
            
    workbook.save(response)
    return response

# 4. HÀM MỚI: XUẤT PDF
def xuat_pdf_nhap_xuat(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    
    bao_cao = get_du_lieu_bao_cao_nhap_xuat(request)
    html_string = render_to_string('pdf_baocao_nhapxuat.html', {
        'bao_cao': bao_cao,
        'tu_ngay': request.GET.get('tu_ngay', ''),
        'den_ngay': request.GET.get('den_ngay', '')
    })
    
    # Cấu hình PDFKit (Đảm bảo máy bạn đã cài đặt wkhtmltopdf như đợt trước)
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    options = {
        'page-size': 'A4',
        'orientation': 'Landscape', # In ngang
        'margin-top': '1cm',
        'margin-right': '1cm',
        'margin-bottom': '1cm',
        'margin-left': '1cm',
        'encoding': "UTF-8",
    }
    
    pdf = pdfkit.from_string(html_string, False, configuration=config, options=options)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="BaoCao_NhapXuatTon.pdf"'
    return response

# ================= BÁO CÁO THIẾT BỊ HƯ HỎNG (THANH LÝ) =================
def bao_cao_thiet_bi_hong_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')

    tu_ngay = request.GET.get('tu_ngay', '')
    den_ngay = request.GET.get('den_ngay', '')
    query = request.GET.get('q', '').strip()
    kp_id = request.GET.get('khoa_phong', '')
    loai = request.GET.get('loai_thiet_bi', '')

    # 1. Lấy danh sách máy hỏng hẳn, KÈM THEO ngày hoàn tất sửa chữa cuối cùng (Ngày xác nhận hỏng)
    ds_tb_hong = ThietBi.objects.filter(is_hong_han=True, is_thanh_ly=False).annotate(
        ngay_xac_nhan_hong=Max('lichsusuachua__ngay_hoan_tat')
    ).order_by('-ngay_xac_nhan_hong', '-id')

    # 2. Bộ lọc thời gian (Dựa trên ngày xác nhận hỏng)
    if tu_ngay:
        ds_tb_hong = ds_tb_hong.filter(ngay_xac_nhan_hong__gte=tu_ngay)
    if den_ngay:
        ds_tb_hong = ds_tb_hong.filter(ngay_xac_nhan_hong__lte=den_ngay)
        
    # 3. Các bộ lọc khác
    if query:
        ds_tb_hong = ds_tb_hong.filter(Q(ten_thiet_bi__unaccent__icontains=query) | Q(ma_thiet_bi__unaccent__icontains=query))
    if kp_id:
        ds_tb_hong = ds_tb_hong.filter(khoa_phong_id=kp_id)
    if loai:
        ds_tb_hong = ds_tb_hong.filter(loai_thiet_bi=loai)

    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong')

    return render(request, 'baocao_thietbihong.html', {
        'ds_tb_hong': ds_tb_hong,
        'tu_ngay': tu_ngay,
        'den_ngay': den_ngay,
        'q_value': query,
        'kp_value': kp_id,
        'loai_value': loai,
        'khoa_phongs': khoa_phongs,
        'loai_choices': LOAI_THIET_BI_CHOICES,
        'tong_so': ds_tb_hong.count()
    })

# --- HÀM XỬ LÝ THANH LÝ NHANH CÓ ẢNH ---
# TÌM VÀ THAY THẾ HÀM NÀY:
# TÌM VÀ THAY THẾ HÀM NÀY:
def thanh_ly_tai_san_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    
    if request.method == 'POST':
        tb_id = request.POST.get('thiet_bi_id')
        ngay = request.POST.get('ngay_thanh_ly')
        ghi_chu = request.POST.get('ghi_chu')
        
        tb = ThietBi.objects.get(id=tb_id)
        tb.is_thanh_ly = True 
        tb.dang_sua_chua = False
        tb.ngay_thanh_ly = ngay
        tb.ly_do_thanh_ly = ghi_chu
        tb.save()

        # LẤY DANH SÁCH NHIỀU ẢNH VÀ LƯU VÀO BẢNG MỚI
        hinh_anhs = request.FILES.getlist('hinh_anh') # Dùng getlist để lấy nhiều file
        for anh in hinh_anhs:
            HinhAnhThanhLy.objects.create(thiet_bi=tb, hinh_anh=anh)

    return redirect('danh_sach_tai_san')

# TÌM VÀ THAY THẾ HÀM NÀY:
# ================= BÁO CÁO TÀI SẢN ĐÃ THANH LÝ =================
def bao_cao_thanh_ly_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')

    tu_ngay = request.GET.get('tu_ngay', '')
    den_ngay = request.GET.get('den_ngay', '')
    query = request.GET.get('q', '').strip()
    kp_id = request.GET.get('khoa_phong', '')
    loai = request.GET.get('loai_thiet_bi', '')

    # Chỉ lấy các máy đã thanh lý
    ds_thanh_ly = ThietBi.objects.filter(is_thanh_ly=True).order_by('-ngay_thanh_ly', '-id')

    if tu_ngay: ds_thanh_ly = ds_thanh_ly.filter(ngay_thanh_ly__gte=tu_ngay)
    if den_ngay: ds_thanh_ly = ds_thanh_ly.filter(ngay_thanh_ly__lte=den_ngay)
    if query: ds_thanh_ly = ds_thanh_ly.filter(Q(ten_thiet_bi__unaccent__icontains=query) | Q(ma_thiet_bi__unaccent__icontains=query))
    if kp_id: ds_thanh_ly = ds_thanh_ly.filter(khoa_phong_id=kp_id)
    if loai: ds_thanh_ly = ds_thanh_ly.filter(loai_thiet_bi=loai)

    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong')

    # GOM NHIỀU LINK ẢNH THÀNH 1 CHUỖI ĐỂ TRUYỀN VÀO JAVASCRIPT POPUP XEM CHI TIẾT
    for tb in ds_thanh_ly:
        tb.chuoi_url_anh = ",".join([anh.hinh_anh.url for anh in tb.danh_sach_anh_thanh_ly.all()])

    return render(request, 'baocao_thanhly.html', {
        'ds_thanh_ly': ds_thanh_ly,
        'tu_ngay': tu_ngay, 'den_ngay': den_ngay, 'q_value': query,
        'kp_value': kp_id, 'loai_value': loai,
        'khoa_phongs': khoa_phongs, 'loai_choices': LOAI_THIET_BI_CHOICES,
        'tong_so': ds_thanh_ly.count()
    })

# ================= HÀM HỦY THANH LÝ (Khôi phục trạng thái máy) =================
def huy_thanh_ly_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    try:
        tb = ThietBi.objects.get(id=id)
        tb.is_thanh_ly = False
        tb.ngay_thanh_ly = None
        tb.ly_do_thanh_ly = None
        # Xóa toàn bộ ảnh thanh lý trong bảng phụ
        HinhAnhThanhLy.objects.filter(thiet_bi=tb).delete()
        tb.save()
    except ThietBi.DoesNotExist: pass
    return redirect('bao_cao_thanh_ly')

# ================= HÀM SỬA THÔNG TIN THANH LÝ (Xóa ảnh cũ / Thêm nhiều ảnh mới) =================
def sua_thanh_ly_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    tb = ThietBi.objects.get(id=id)

    if request.method == 'POST':
        tb.ngay_thanh_ly = request.POST.get('ngay_thanh_ly')
        tb.ly_do_thanh_ly = request.POST.get('ghi_chu')
        tb.save()

        # 1. XỬ LÝ XÓA ẢNH CŨ (Nhận danh sách ID các ảnh bị tích dấu xóa ở giao diện)
        xoa_anh_ids = request.POST.getlist('xoa_anh') 
        if xoa_anh_ids:
            HinhAnhThanhLy.objects.filter(id__in=xoa_anh_ids).delete()

        # 2. XỬ LÝ THÊM ẢNH MỚI (Dùng getlist để lấy nhiều ảnh)
        hinh_anhs = request.FILES.getlist('hinh_anh')
        for anh in hinh_anhs:
            HinhAnhThanhLy.objects.create(thiet_bi=tb, hinh_anh=anh)

        return redirect('bao_cao_thanh_ly')

    # Lấy danh sách ảnh cũ truyền ra giao diện
    anh_cu = HinhAnhThanhLy.objects.filter(thiet_bi=tb)
    return render(request, 'sua_thanhly.html', {'tb': tb, 'anh_cu': anh_cu})

# ================= HÀM KHÔI PHỤC (UNDO) THIẾT BỊ HƯ HỎNG =================
# ================= HÀM KHÔI PHỤC (UNDO) THIẾT BỊ HƯ HỎNG =================
def huy_hong_han_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    try:
        tb = ThietBi.objects.get(id=id)
        # 1. Bỏ trạng thái hỏng hẳn, trả về trạng thái ĐANG SỬA CHỮA
        tb.is_hong_han = False 
        tb.dang_sua_chua = True
        tb.save()
        
        # 2. Xóa ngày hoàn tất ở phiếu sửa chữa cuối cùng (để nó thành 'chưa xong')
        phieu_cuoi = LichSuSuaChua.objects.filter(thiet_bi=tb).order_by('-id').first()
        if phieu_cuoi:
            phieu_cuoi.ngay_hoan_tat = None
            phieu_cuoi.ghi_chu_hoan_tat = ""
            phieu_cuoi.save()
            
    except ThietBi.DoesNotExist:
        pass
    return redirect('bao_cao_thiet_bi_hong')

# ================= HÀM SỬA NỘI DUNG HƯ HỎNG =================
def sua_loi_hu_hong_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    
    try:
        tb = ThietBi.objects.get(id=id)
        # Lấy bản ghi sửa chữa cuối cùng (chính là bản ghi đánh dấu hỏng)
        lich_su_cuoi = LichSuSuaChua.objects.filter(thiet_bi=tb).order_by('-id').first()
    except ThietBi.DoesNotExist:
        return redirect('bao_cao_thiet_bi_hong')

    if request.method == "POST":
        ngay_ht = request.POST.get('ngay_hoan_tat')
        ghi_chu_ht = request.POST.get('ghi_chu_hoan_tat')
        
        if lich_su_cuoi:
            lich_su_cuoi.ngay_hoan_tat = ngay_ht
            lich_su_cuoi.ghi_chu_hoan_tat = ghi_chu_ht
            lich_su_cuoi.save()
            
        return redirect('bao_cao_thiet_bi_hong')
        
    return render(request, 'sua_loihuhong.html', {
        'tb': tb,
        'lich_su': lich_su_cuoi
    })
# ================= KHU VỰC DANH MỤC NHÂN VIÊN =================

def them_nhan_vien_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')

    thong_bao = ""
    thong_bao_loi = ""

    if request.method == "POST":
        ma = request.POST.get('ma_nhan_vien', '').strip()
        ten = request.POST.get('ten_nhan_vien', '').strip()

        if ten:
            NhanVien.objects.create(ma_nhan_vien=ma, ten_nhan_vien=ten)
            thong_bao = f"Đã thêm nhân viên '{ten}' thành công!"
        else:
            thong_bao_loi = "Tên nhân viên là bắt buộc!"

    # Kéo danh sách để hiển thị ở bảng bên dưới
    danh_sach_nv = NhanVien.objects.all().order_by('-id')

    return render(request, 'them_nhanvien.html', {
        'thong_bao': thong_bao,
        'thong_bao_loi': thong_bao_loi,
        'danh_sach_nv': danh_sach_nv
    })

def xoa_nhan_vien_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    NhanVien.objects.filter(id=id).delete()
    return redirect('them_nhan_vien')

def sua_nhan_vien_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    try:
        nv = NhanVien.objects.get(id=id)
    except NhanVien.DoesNotExist:
        return redirect('them_nhan_vien')

    if request.method == "POST":
        ma = request.POST.get('ma_nhan_vien', '').strip()
        ten = request.POST.get('ten_nhan_vien', '').strip()

        if ten:
            nv.ma_nhan_vien = ma
            nv.ten_nhan_vien = ten
            nv.save()
            return redirect('them_nhan_vien')

    return render(request, 'sua_nhanvien.html', {'nv': nv})

# ================= KHU VỰC GIAO BAN CNTT =================
def giao_ban_cntt_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')

    tu_ngay = request.GET.get('tu_ngay', '')
    den_ngay = request.GET.get('den_ngay', '')
    kp_id = request.GET.get('khoa_phong', '')
    nv_id = request.GET.get('nhan_vien', '')
    trang_thai = request.GET.get('trang_thai', '') 

    # Dùng prefetch_related cho ManyToManyField
    danh_sach = GiaoBanCNTT.objects.select_related('khoa_phong').prefetch_related('nhan_vien').all().order_by('-ngay_giao_ban', '-id')

    if tu_ngay: danh_sach = danh_sach.filter(ngay_giao_ban__gte=tu_ngay)
    if den_ngay: danh_sach = danh_sach.filter(ngay_giao_ban__lte=den_ngay)
    if kp_id: danh_sach = danh_sach.filter(khoa_phong_id=kp_id)
    if nv_id: danh_sach = danh_sach.filter(nhan_vien__id=nv_id) # Thay đổi cách lọc nhân viên
    if trang_thai: danh_sach = danh_sach.filter(trang_thai=trang_thai) 

    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong')
    nhan_viens = NhanVien.objects.all().order_by('ten_nhan_vien')

    return render(request, 'giaoban_cntt.html', {
        'danh_sach': danh_sach,
        'khoa_phongs': khoa_phongs,
        'nhan_viens': nhan_viens,
        'tu_ngay': tu_ngay,
        'den_ngay': den_ngay,
        'kp_value': kp_id,
        'nv_value': nv_id,
        'trang_thai_value': trang_thai, 
        'tong_so': danh_sach.count()
    })

def luu_giao_ban_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    
    if request.method == 'POST':
        gb = GiaoBanCNTT.objects.create(
            ngay_giao_ban=request.POST.get('ngay_giao_ban'),
            khoa_phong_id=request.POST.get('khoa_phong'),
            tinh_trang_tiep_nhan=request.POST.get('tinh_trang_tiep_nhan'),
            cach_xu_ly=request.POST.get('cach_xu_ly'),
            trang_thai=request.POST.get('trang_thai'),
            ghi_chu=request.POST.get('ghi_chu')
        )
        
        # Nhận mảng các ID nhân viên và gán vào phiếu
        nv_ids = request.POST.getlist('nhan_vien')
        if nv_ids:
            gb.nhan_vien.set(nv_ids)

    return redirect('giao_ban_cntt')

def xoa_giao_ban_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    GiaoBanCNTT.objects.filter(id=id).delete()
    return redirect('giao_ban_cntt')
def sua_giao_ban_view(request, id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    
    try:
        gb = GiaoBanCNTT.objects.get(id=id)
    except GiaoBanCNTT.DoesNotExist:
        return redirect('giao_ban_cntt')

    if request.method == "POST":
        gb.ngay_giao_ban = request.POST.get('ngay_giao_ban')
        gb.khoa_phong_id = request.POST.get('khoa_phong')
        gb.tinh_trang_tiep_nhan = request.POST.get('tinh_trang_tiep_nhan')
        gb.cach_xu_ly = request.POST.get('cach_xu_ly')
        gb.trang_thai = request.POST.get('trang_thai')
        gb.ghi_chu = request.POST.get('ghi_chu')
        gb.save()
        
        # Cập nhật lại danh sách nhân viên
        nv_ids = request.POST.getlist('nhan_vien')
        gb.nhan_vien.set(nv_ids)
        
        return redirect('giao_ban_cntt')

    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong')
    nhan_viens = NhanVien.objects.all().order_by('ten_nhan_vien')
    
    # Lấy danh sách ID các nhân viên đã chọn để load lên form sửa
    selected_nvs = list(gb.nhan_vien.values_list('id', flat=True))

    return render(request, 'sua_giaoban.html', {
        'gb': gb,
        'khoa_phongs': khoa_phongs,
        'nhan_viens': nhan_viens,
        'selected_nvs': selected_nvs
    })

# ================= KHU VỰC TỒN KHO KHOA PHÒNG =================
# ================= KHU VỰC TỒN KHO KHOA PHÒNG =================
def ton_kho_khoa_phong_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')

    kp_id = request.GET.get('khoa_phong', '')
    trang_thai = request.GET.get('trang_thai', 'tat_ca') # Mặc định là tất cả
    query = request.GET.get('q', '').strip()
    
    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong')
    
    danh_sach_ton = []
    if kp_id:
        danh_sach_ton = TonKhoKhoaPhong.objects.filter(khoa_phong_id=kp_id).select_related('vat_tu').order_by('vat_tu__ten_vat_tu')

        if query:
            danh_sach_ton = danh_sach_ton.filter(vat_tu__ten_vat_tu__unaccent__icontains=query)
        
        # Xử lý Lọc theo Trạng Thái
        if trang_thai == 'hoat_dong':
            danh_sach_ton = danh_sach_ton.filter(so_luong__gt=0)
        elif trang_thai == 'het_ton':
            danh_sach_ton = danh_sach_ton.filter(so_luong=0)
        elif trang_thai == 'hu_hong':
            danh_sach_ton = danh_sach_ton.filter(so_luong_hong__gt=0)

    return render(request, 'tonkho_khoaphong.html', {
        'khoa_phongs': khoa_phongs,
        'kp_value': kp_id,
        'trang_thai_value': trang_thai, # Trả về cho UI
        'q_value': query,
        'danh_sach_ton': danh_sach_ton
    })



def lay_ton_kho_theo_khoa_api(request, khoa_id):
    if not request.session.get('is_login'): 
        return JsonResponse({'status': 'error', 'msg': 'Chưa đăng nhập'})

    # Lấy các vật tư có số lượng lớn hơn 0 thuộc riêng khoa phòng này
    ton_khos = TonKhoKhoaPhong.objects.filter(khoa_phong_id=khoa_id, so_luong__gt=0).select_related('vat_tu')

    data = []
    for tk in ton_khos:
        data.append({
            'id': tk.vat_tu.id,
            'ten_vat_tu': tk.vat_tu.ten_vat_tu,
            'so_luong': tk.so_luong
        })

    return JsonResponse({'status': 'success', 'data': data})

# --- API BÁO HỎNG VẬT TƯ (TỪ KHOA NÀY SANG KHOA KHÁC HOẶC TẠI CHỖ) ---
# --- API BÁO HỎNG VẬT TƯ (CÓ LƯU LỊCH SỬ) ---
def bao_hong_vat_tu_api(request):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error', 'msg': 'Chưa đăng nhập'})
        
    if request.method == 'POST':
        try:
            with transaction.atomic(): # Dùng transaction để đảm bảo dữ liệu an toàn
                data = json.loads(request.body)
                vt_id = data.get('vt_id')
                khoa_hien_tai_id = data.get('khoa_hien_tai_id')
                khoa_nhan_hong_id = data.get('khoa_nhan_hong_id')
                so_luong = int(data.get('so_luong', 0))

                if so_luong <= 0: return JsonResponse({'status': 'error', 'msg': 'Số lượng hỏng phải lớn > 0!'})

                ton_hien_tai = TonKhoKhoaPhong.objects.get(khoa_phong_id=khoa_hien_tai_id, vat_tu_id=vt_id)
                if ton_hien_tai.so_luong < so_luong: return JsonResponse({'status': 'error', 'msg': 'Vượt quá số lượng đang có!'})
                
                # 1. Trừ kho tốt, Cộng kho hỏng
                ton_hien_tai.so_luong -= so_luong
                ton_hien_tai.save()

                ton_hong, created = TonKhoKhoaPhong.objects.get_or_create(
                    khoa_phong_id=khoa_nhan_hong_id, vat_tu_id=vt_id,
                    defaults={'so_luong': 0, 'so_luong_hong': 0}
                )
                ton_hong.so_luong_hong += so_luong
                ton_hong.save()

                # 2. LƯU LỊCH SỬ ĐỂ SAU NÀY HOÀN TÁC
                LichSuBaoHong.objects.create(
                    vat_tu_id=vt_id, khoa_xuat_id=khoa_hien_tai_id, khoa_nhan_id=khoa_nhan_hong_id, so_luong=so_luong
                )

                return JsonResponse({'status': 'success', 'msg': 'Đã ghi nhận vật tư hư hỏng thành công!'})
        except Exception as e: return JsonResponse({'status': 'error', 'msg': str(e)})

# --- API LẤY CHI TIẾT LỊCH SỬ ĐỒ HỎNG ---
def chi_tiet_bao_hong_api(request):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error'})
    khoa_nhan_id = request.GET.get('khoa_nhan_id')
    vt_id = request.GET.get('vt_id')
    
    lich_su = LichSuBaoHong.objects.filter(khoa_nhan_id=khoa_nhan_id, vat_tu_id=vt_id).order_by('-id')
    data = []
    for ls in lich_su:
        data.append({
            'id': ls.id,
            'ngay': timezone.localtime(ls.ngay_bao_hong).strftime('%d/%m/%Y %H:%M'),
            'khoa_xuat': ls.khoa_xuat.ten_khoa_phong,
            'so_luong': ls.so_luong
        })
    return JsonResponse({'status': 'success', 'data': data})

# --- API HOÀN TÁC BÁO HỎNG ---
def hoan_tac_bao_hong_api(request, id):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error'})
    try:
        with transaction.atomic():
            ls = LichSuBaoHong.objects.get(id=id)
            
            # 1. Trả lại đồ tốt cho Khoa Xuất
            ton_xuat, _ = TonKhoKhoaPhong.objects.get_or_create(
                khoa_phong_id=ls.khoa_xuat_id, vat_tu_id=ls.vat_tu_id,
                defaults={'so_luong': 0, 'so_luong_hong': 0}
            )
            ton_xuat.so_luong += ls.so_luong
            ton_xuat.save()

            # 2. Trừ đồ hỏng của Khoa Nhận
            ton_nhan = TonKhoKhoaPhong.objects.get(khoa_phong_id=ls.khoa_nhan_id, vat_tu_id=ls.vat_tu_id)
            ton_nhan.so_luong_hong -= ls.so_luong
            if ton_nhan.so_luong_hong < 0: ton_nhan.so_luong_hong = 0
            ton_nhan.save()

            # 3. Xóa lịch sử
            ls.delete()
            
        return JsonResponse({'status': 'success', 'msg': 'Đã hoàn tác khôi phục lại kho thành công!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)})
    
# --- API XUẤT TIÊU HAO VẬT TƯ ---
# --- API XUẤT TIÊU HAO VẬT TƯ (HỖ TRỢ CẢ ĐỒ TỐT VÀ ĐỒ HỎNG) ---
def xuat_tieu_hao_api(request):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error', 'msg': 'Chưa đăng nhập'})
        
    if request.method == 'POST':
        try:
            with transaction.atomic():
                data = json.loads(request.body)
                vt_id = data.get('vt_id')
                khoa_hien_tai_id = data.get('khoa_hien_tai_id')
                khoa_nhan_id = data.get('khoa_nhan_id')
                so_luong = int(data.get('so_luong', 0))
                
                # THÊM: Lấy phân loại đang xuất đồ Tốt hay đồ Hỏng từ giao diện
                loai_xuat = data.get('loai_xuat', 'tot') 

                if so_luong <= 0: return JsonResponse({'status': 'error', 'msg': 'Số lượng phải lớn hơn 0!'})

                ton = TonKhoKhoaPhong.objects.get(khoa_phong_id=khoa_hien_tai_id, vat_tu_id=vt_id)
                
                # NẾU LÀ XUẤT ĐỒ HỎNG -> TRỪ CỘT HỎNG
                if loai_xuat == 'hong':
                    if ton.so_luong_hong < so_luong: 
                        return JsonResponse({'status': 'error', 'msg': 'Vượt quá số lượng hỏng đang có!'})
                    ton.so_luong_hong -= so_luong
                
                # NẾU LÀ XUẤT ĐỒ TỐT -> TRỪ CỘT TỐT
                else:
                    if ton.so_luong < so_luong: 
                        return JsonResponse({'status': 'error', 'msg': 'Vượt quá số lượng tồn kho đang có!'})
                    ton.so_luong -= so_luong
                    
                ton.save()

                # Lưu vào bảng lịch sử tiêu hao (Kèm theo trạng thái để sau này làm báo cáo)
                LichSuTieuHao.objects.create(
                    vat_tu_id=vt_id, 
                    khoa_xuat_id=khoa_hien_tai_id, 
                    khoa_nhan_id=khoa_nhan_id, 
                    so_luong=so_luong,
                    is_hong=(loai_xuat == 'hong') # Nếu là hong thì True, tot thì False
                )

                return JsonResponse({'status': 'success', 'msg': 'Đã xuất tiêu hao thành công!'})
        except Exception as e: 
            return JsonResponse({'status': 'error', 'msg': str(e)})

# ================= KHU VỰC BÁO CÁO TIÊU HAO VẬT TƯ =================

# ================= KHU VỰC BÁO CÁO TIÊU HAO VẬT TƯ =================

def bao_cao_tieu_hao_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')

    tu_ngay = request.GET.get('tu_ngay', '')
    den_ngay = request.GET.get('den_ngay', '')
    kp_id = request.GET.get('khoa_phong', '') # Lọc theo Khoa sử dụng (Khoa nhận)

    # 1. Lấy dữ liệu và lọc cơ bản
    ds_qs = LichSuTieuHao.objects.all()
    if tu_ngay: ds_qs = ds_qs.filter(ngay_tieu_hao__date__gte=tu_ngay)
    if den_ngay: ds_qs = ds_qs.filter(ngay_tieu_hao__date__lte=den_ngay)
    if kp_id: ds_qs = ds_qs.filter(khoa_nhan_id=kp_id)

    # 2. Gom nhóm theo Vật tư và tính Tổng cộng dồn
    ds_tieu_hao = ds_qs.values(
        'vat_tu__id', 
        'vat_tu__ma_vat_tu', 
        'vat_tu__ten_vat_tu'
    ).annotate(
        tong_sl=Sum('so_luong')
    ).order_by('vat_tu__ten_vat_tu')

    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong')

    return render(request, 'baocao_tieuhao.html', {
        'ds_tieu_hao': ds_tieu_hao,
        'tu_ngay': tu_ngay,
        'den_ngay': den_ngay,
        'kp_value': kp_id,
        'khoa_phongs': khoa_phongs,
        'tong_so': ds_tieu_hao.count()
    })

# --- API LẤY CHI TIẾT CÁC LẦN XUẤT CHO POPUP CON MẮT ---
def chi_tiet_tieu_hao_api(request):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error'})
    
    vt_id = request.GET.get('vt_id')
    tu_ngay = request.GET.get('tu_ngay', '')
    den_ngay = request.GET.get('den_ngay', '')
    kp_id = request.GET.get('khoa_phong', '')

    qs = LichSuTieuHao.objects.filter(vat_tu_id=vt_id).select_related('khoa_xuat', 'khoa_nhan').order_by('-ngay_tieu_hao', '-id')
    
    # Áp dụng lại bộ lọc để chi tiết trong popup khớp với bộ lọc bên ngoài
    if tu_ngay: qs = qs.filter(ngay_tieu_hao__date__gte=tu_ngay)
    if den_ngay: qs = qs.filter(ngay_tieu_hao__date__lte=den_ngay)
    if kp_id: qs = qs.filter(khoa_nhan_id=kp_id)

    data = []
    for ls in qs:
        data.append({
            'id': ls.id,
            'ngay': timezone.localtime(ls.ngay_tieu_hao).strftime('%d/%m/%Y %H:%M'),
            'khoa_xuat': ls.khoa_xuat.ten_khoa_phong if ls.khoa_xuat else '---',
            'khoa_nhan': ls.khoa_nhan.ten_khoa_phong if ls.khoa_nhan else '---',
            'is_hong': ls.is_hong,
            'so_luong': ls.so_luong
        })
    return JsonResponse({'status': 'success', 'data': data})

# API HOÀN TÁC TIÊU HAO (Giữ nguyên như cũ)
def hoan_tac_tieu_hao_api(request, id):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error'})
    try:
        with transaction.atomic():
            ls = LichSuTieuHao.objects.get(id=id)
            ton, created = TonKhoKhoaPhong.objects.get_or_create(
                khoa_phong_id=ls.khoa_xuat_id, vat_tu_id=ls.vat_tu_id,
                defaults={'so_luong': 0, 'so_luong_hong': 0}
            )
            if ls.is_hong: ton.so_luong_hong += ls.so_luong
            else: ton.so_luong += ls.so_luong
            ton.save()
            ls.delete()
        return JsonResponse({'status': 'success', 'msg': 'Đã hoàn tác và trả vật tư về kho thành công!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)})
# API HOÀN TÁC TIÊU HAO
def hoan_tac_tieu_hao_api(request, id):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error'})
    try:
        with transaction.atomic():
            ls = LichSuTieuHao.objects.get(id=id)
            
            # 1. Trả lại số lượng cho Khoa Xuất (Khoa gốc)
            ton, created = TonKhoKhoaPhong.objects.get_or_create(
                khoa_phong_id=ls.khoa_xuat_id, 
                vat_tu_id=ls.vat_tu_id,
                defaults={'so_luong': 0, 'so_luong_hong': 0}
            )
            
            # Kiểm tra xem lúc xuất là đồ tốt hay đồ hỏng để cộng trả lại cho đúng cột
            if ls.is_hong:
                ton.so_luong_hong += ls.so_luong
            else:
                ton.so_luong += ls.so_luong
                
            ton.save()

            # 2. Xóa bản ghi lịch sử
            ls.delete()
            
        return JsonResponse({'status': 'success', 'msg': 'Đã hoàn tác và trả vật tư về kho thành công!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)})


# ================= KHU VỰC BÁO CÁO CHI TIẾT NHẬP XUẤT VẬT TƯ =================

# ================= KHU VỰC BÁO CÁO TỔNG HỢP NHẬP XUẤT VẬT TƯ =================

# ================= KHU VỰC BÁO CÁO TỔNG HỢP NHẬP XUẤT VẬT TƯ =================

def bao_cao_chi_tiet_nhap_xuat_view(request):
    if not request.session.get('is_login'): return redirect('dang_nhap')

    tu_ngay = request.GET.get('tu_ngay', '')
    den_ngay = request.GET.get('den_ngay', '')
    kp_id = request.GET.get('khoa_phong', '')
    vt_id = request.GET.get('vat_tu', '')

    lich_su = []

    # 1. Lấy danh sách các vật tư (Nếu có chọn 1 vật tư cụ thể thì lọc luôn)
    danh_sach_vt = VatTu.objects.all().order_by('ten_vat_tu')
    if vt_id:
        danh_sach_vt = danh_sach_vt.filter(id=vt_id)

    # 2. Duyệt qua từng vật tư để tính tổng Nhập và tổng Xuất
    for vt in danh_sach_vt:
        tong_nhap = 0
        tong_xuat = 0

        # ----- A. TÍNH TỪ PHIẾU NHẬP KHO (Hàng mua mới từ ngoài vào) -----
        nhap_qs = ChiTietPhieuNhap.objects.filter(vat_tu=vt)
        if tu_ngay: nhap_qs = nhap_qs.filter(phieu_nhap__ngay_phieu__gte=tu_ngay)
        if den_ngay: nhap_qs = nhap_qs.filter(phieu_nhap__ngay_phieu__lte=den_ngay)
        if kp_id: 
            try: nhap_qs = nhap_qs.filter(phieu_nhap__khoa_phong_id=kp_id)
            except Exception: pass
        tong_nhap += nhap_qs.aggregate(tong=Sum('so_luong'))['tong'] or 0

        # ----- B. TÍNH TỪ PHIẾU XUẤT KHO (Hàng luân chuyển giữa các Khoa) -----
        xuat_qs = ChiTietPhieuXuat.objects.filter(vat_tu=vt)
        if tu_ngay: xuat_qs = xuat_qs.filter(phieu_xuat__ngay_phieu__gte=tu_ngay)
        if den_ngay: xuat_qs = xuat_qs.filter(phieu_xuat__ngay_phieu__lte=den_ngay)
        
        if kp_id: 
            # 1. Nếu Khoa này là KHOA XUẤT ĐI -> Cộng vào TỔNG XUẤT
            try:
                xuat_di = xuat_qs.filter(phieu_xuat__khoa_phong_id=kp_id).aggregate(tong=Sum('so_luong'))['tong'] or 0
                tong_xuat += xuat_di
            except Exception: pass
            
            # 2. Nếu Khoa này là KHOA ĐƯỢC NHẬN VỀ -> Cộng vào TỔNG NHẬP
            try:
                nhan_ve = xuat_qs.filter(phieu_xuat__khoa_nhan_id=kp_id).aggregate(tong=Sum('so_luong'))['tong'] or 0
                tong_nhap += nhan_ve
            except Exception: pass
        else:
            # Nếu lọc toàn viện (Tất cả khoa) -> Gộp chung là Xuất nội bộ
            tong_xuat += xuat_qs.aggregate(tong=Sum('so_luong'))['tong'] or 0

        # ----- C. TÍNH TỪ LỊCH SỬ TIÊU HAO (Hàng dùng mất đi/Hủy) -----
        try:
            tieu_hao_qs = LichSuTieuHao.objects.filter(vat_tu=vt)
            if tu_ngay: tieu_hao_qs = tieu_hao_qs.filter(ngay_tieu_hao__date__gte=tu_ngay)
            if den_ngay: tieu_hao_qs = tieu_hao_qs.filter(ngay_tieu_hao__date__lte=den_ngay)
            if kp_id:
                tieu_hao_qs = tieu_hao_qs.filter(khoa_xuat_id=kp_id)
            
            # Tiêu hao chắc chắn là Xuất (mất khỏi kho)
            tong_xuat += tieu_hao_qs.aggregate(tong=Sum('so_luong'))['tong'] or 0
        except Exception: 
            pass

        # ----- CHỈ ĐƯA VÀO BÁO CÁO NẾU CÓ PHÁT SINH GIAO DỊCH -----
        if tong_nhap > 0 or tong_xuat > 0:
            lich_su.append({
                'ma_vt': vt.ma_vat_tu or '---',
                'ten_vat_tu': vt.ten_vat_tu,
                'is_tieu_hao': vt.is_tieu_hao,
                'tong_nhap': tong_nhap,
                'tong_xuat': tong_xuat
            })

    # Đổ danh sách Khoa phòng và Vật tư ra dropdown để lọc
    khoa_phongs = KhoaPhong.objects.all().order_by('ten_khoa_phong')
    vat_tus = VatTu.objects.all().order_by('ten_vat_tu')

    return render(request, 'baocao_chitiet_nhapxuat.html', {
        'lich_su': lich_su,
        'tu_ngay': tu_ngay,
        'den_ngay': den_ngay,
        'kp_value': kp_id,
        'vt_value': vt_id,
        'khoa_phongs': khoa_phongs,
        'vat_tus': vat_tus,
        'tong_so': len(lich_su)
    })

# ================= KHU VỰC IN PHIẾU PDF =================
def in_phieu_nhap_pdf(request, phieu_id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    
    try:
        phieu = PhieuNhapKho.objects.get(id=phieu_id)
        chi_tiet = ChiTietPhieuNhap.objects.filter(phieu_nhap=phieu).select_related('vat_tu')
        
        # Tính tổng số lượng
        tong_sl = sum(ct.so_luong for ct in chi_tiet)
        
        # Tách ngày tháng năm để in dưới chữ ký
        ngay = phieu.ngay_phieu.day
        thang = phieu.ngay_phieu.month
        nam = phieu.ngay_phieu.year
        
        # Lấy tên khoa phòng (nếu phiếu có lưu khoa phòng)
        ten_khoa = phieu.khoa_phong.ten_khoa_phong if hasattr(phieu, 'khoa_phong') and phieu.khoa_phong else "........................"

        html_string = render_to_string('pdf_phieunhap.html', {
            'phieu': phieu,
            'chi_tiet': chi_tiet,
            'tong_sl': tong_sl,
            'ngay': f"{ngay:02d}", # Định dạng 01, 02...
            'thang': f"{thang:02d}",
            'nam': nam,
            'ten_khoa': ten_khoa
        })
        
        # Cấu hình PDFKit
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        
        options = {
            'page-size': 'A4',
            'margin-top': '15mm',
            'margin-right': '15mm',
            'margin-bottom': '15mm',
            'margin-left': '15mm',
            'encoding': "UTF-8",
        }
        
        pdf = pdfkit.from_string(html_string, False, configuration=config, options=options)
        
        # Dùng 'inline' để mở tab mới xem PDF thay vì tải xuống ép buộc
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="PhieuNhap_{phieu.ma_phieu}.pdf"' 
        return response

    except PhieuNhapKho.DoesNotExist:
        return HttpResponse("Không tìm thấy phiếu nhập này!", status=404)


# ================= KHU VỰC IN PHIẾU XUẤT KHO PDF =================
def in_phieu_xuat_pdf(request, phieu_id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    
    try:
        # Lấy thông tin phiếu xuất kèm theo thông tin liên kết khoa phòng xuất và khoa phòng nhận
        phieu = PhieuXuatKho.objects.select_related('khoa_phong', 'khoa_nhan').get(id=phieu_id)
        chi_tiet = ChiTietPhieuXuat.objects.filter(phieu_xuat=phieu).select_related('vat_tu')
        
        # Tính tổng số lượng xuất trong phiếu
        tong_sl = sum(ct.so_luong for ct in chi_tiet)
        
        # Tách ngày tháng năm để in
        ngay = phieu.ngay_phieu.day
        thang = phieu.ngay_phieu.month
        nam = phieu.ngay_phieu.year
        
        # Lấy tên khoa phòng xuất và nhận (bảo vệ an toàn dữ liệu nếu trống)
        kp_xuat = phieu.khoa_phong.ten_khoa_phong if hasattr(phieu, 'khoa_phong') and phieu.khoa_phong else "........................"
        kp_nhan = phieu.khoa_nhan.ten_khoa_phong if hasattr(phieu, 'khoa_nhan') and phieu.khoa_nhan else "........................"

        html_string = render_to_string('pdf_phieuxuat.html', {
            'phieu': phieu,
            'chi_tiet': chi_tiet,
            'tong_sl': tong_sl,
            'ngay': f"{ngay:02d}",
            'thang': f"{thang:02d}",
            'nam': nam,
            'kp_xuat': kp_xuat,
            'kp_nhan': kp_nhan
        })
        
        # Cấu hình PDFKit (Đường dẫn wkhtmltopdf mặc định trên Windows)
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        
        options = {
            'page-size': 'A4',
            'margin-top': '15mm',
            'margin-right': '15mm',
            'margin-bottom': '15mm',
            'margin-left': '15mm',
            'encoding': "UTF-8",
        }
        
        pdf = pdfkit.from_string(html_string, False, configuration=config, options=options)
        
        # Trả file PDF về trình duyệt dạng Tab mới để in trực tiếp
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="PhieuXuat_{phieu.ma_phieu}.pdf"' 
        return response

    except PhieuXuatKho.DoesNotExist:
        return HttpResponse("Không tìm thấy phiếu xuất kho này!", status=404)

# ================= KHU VỰC SỬA CHỮA VÀ IN PHIẾU PDF =================

# 1. API LƯU SỬA CHỮA KHÔNG LOAD TRANG (AJAX)
# 1. API LƯU SỬA CHỮA KHÔNG LOAD TRANG (AJAX) - ĐÃ FIX
def luu_sua_chua_ajax_api(request):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error', 'msg': 'Chưa đăng nhập'})
    if request.method == 'POST':
        try:
            with transaction.atomic():
                data = json.loads(request.body)
                tb_id = data.get('thiet_bi_id')
                ngay_sua = data.get('ngay_sua_chua')
                ghi_chu = data.get('ghi_chu')

                # 1. Lấy thiết bị ra
                tb = ThietBi.objects.get(id=tb_id)
                
                # 2. CHẶN: Nếu máy đang sửa rồi thì không cho báo sửa đè lên
                if tb.dang_sua_chua:
                    return JsonResponse({'status': 'error', 'msg': 'Thiết bị này đang trong quá trình sửa chữa rồi!'})

                # 3. Đổi trạng thái thiết bị thành Đang sửa (Bỏ qua so_lan_sua vì nó tự đếm)
                tb.dang_sua_chua = True
                tb.save()

                # 4. Lưu vào bảng Lịch Sử Sửa Chữa (Dùng đúng tên cột là ngay_sua_chua)
                ls = LichSuSuaChua.objects.create(
                    thiet_bi_id=tb_id,
                    ngay_sua_chua=ngay_sua,
                    ghi_chu=ghi_chu
                )

                return JsonResponse({
                    'status': 'success', 
                    'msg': 'Đã báo sửa chữa thành công! Bây giờ bạn có thể in phiếu.', 
                    'ls_id': ls.id 
                })
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})


# 2. HÀM TẠO FILE PDF SỬA CHỮA
def in_phieu_sua_chua_pdf(request, ls_id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    try:
        ls = LichSuSuaChua.objects.select_related('thiet_bi').get(id=ls_id)
        tb = ls.thiet_bi
        
        # Lấy ngày tháng năm hiện tại
        now = timezone.localtime(timezone.now())
        
        # Format ngày sử dụng
        ngay_su_dung = tb.ngay_su_dung.strftime('%d/%m/%Y') if tb.ngay_su_dung else "..................................................."

        html_string = render_to_string('pdf_phieusuachua.html', {
            'ls': ls,
            'tb': tb,
            'ngay_su_dung': ngay_su_dung,
            'ngay': f"{now.day:02d}",
            'thang': f"{now.month:02d}",
            'nam': now.year
        })
        
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        options = {
            'page-size': 'A4',
            'margin-top': '25mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
        }
        pdf = pdfkit.from_string(html_string, False, configuration=config, options=options)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="PhieuSuaChua_{tb.ma_thiet_bi}.pdf"'
        return response
    except LichSuSuaChua.DoesNotExist:
        return HttpResponse("Không tìm thấy thông tin sửa chữa!", status=404)


# ================= KHU VỰC HOÀN TẤT SỬA CHỮA VÀ IN PHIẾU PDF =================

# 1. API LƯU HOÀN TẤT SỬA CHỮA KHÔNG LOAD TRANG (AJAX)
def hoan_tat_sua_chua_ajax_api(request):
    if not request.session.get('is_login'): return JsonResponse({'status': 'error', 'msg': 'Chưa đăng nhập'})
    
    if request.method == "POST":
        try:
            with transaction.atomic():
                data = json.loads(request.body)
                tb_id = data.get('thiet_bi_id')
                ngay_xong = data.get('ngay_hoan_tat')
                ghi_chu_xong = data.get('ghi_chu_hoan_tat')
                check_hong = data.get('check_hong_han') # Nhận giá trị True/False từ JS
                
                tb = ThietBi.objects.get(id=tb_id)
                
                # 1. Trả thiết bị về trạng thái bình thường (Hết tô đỏ)
                tb.dang_sua_chua = False
                tb.is_hong_han = check_hong 
                tb.save()
                
                # 2. Tìm phiếu sửa chữa gần nhất của thiết bị này và điền ngày hoàn tất vào
                phieu_cuoi = LichSuSuaChua.objects.filter(thiet_bi_id=tb_id).order_by('-id').first()
                if phieu_cuoi:
                    phieu_cuoi.ngay_hoan_tat = ngay_xong
                    phieu_cuoi.ghi_chu_hoan_tat = ghi_chu_xong
                    phieu_cuoi.save()
                    ls_id = phieu_cuoi.id
                else:
                    return JsonResponse({'status': 'error', 'msg': 'Không tìm thấy lịch sử báo sửa trước đó!'})
                
                return JsonResponse({
                    'status': 'success', 
                    'msg': 'Đã xác nhận hoàn tất thành công! Bạn có thể in phiếu ngay.',
                    'ls_id': ls_id
                })
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)})


# 2. HÀM TẠO FILE PDF HOÀN TẤT SỬA CHỮA
def in_phieu_hoan_tat_pdf(request, ls_id):
    if not request.session.get('is_login'): return redirect('dang_nhap')
    try:
        ls = LichSuSuaChua.objects.select_related('thiet_bi').get(id=ls_id)
        tb = ls.thiet_bi
        
        now = timezone.localtime(timezone.now())
        
        # Format ngày tháng
        ngay_hoan_tat = ls.ngay_hoan_tat.strftime('%d/%m/%Y') if ls.ngay_hoan_tat else "....................................."

        html_string = render_to_string('pdf_phieuhoantat.html', {
            'ls': ls,
            'tb': tb,
            'ngay_hoan_tat': ngay_hoan_tat,
            'ngay': f"{now.day:02d}",
            'thang': f"{now.month:02d}",
            'nam': now.year
        })
        
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        options = {
            'page-size': 'A4',
            'margin-top': '25mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
        }
        pdf = pdfkit.from_string(html_string, False, configuration=config, options=options)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="PhieuHoanTat_{tb.ma_thiet_bi}.pdf"'
        return response
    except LichSuSuaChua.DoesNotExist:
        return HttpResponse("Không tìm thấy thông tin sửa chữa!", status=404)
