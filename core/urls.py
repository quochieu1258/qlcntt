"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hethong import views # Import file views của app hethong
from django.conf import settings # THÊM DÒNG NÀY
from django.conf.urls.static import static # THÊM DÒNG NÀ
urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', views.login_view, name='dang_nhap'), # Đường dẫn web của bạn
    path('dashboard/', views.dashboard_view, name='dashboard'), # Thêm dòng này
    path('logout/', views.logout_view, name='logout'),
    path('them-khoa-phong/', views.them_khoa_phong_view, name='them_khoa_phong'),
    path('xoa-khoa-phong/<int:id>/', views.xoa_khoa_phong_view, name='xoa_khoa_phong'),
    path('sua-khoa-phong/<int:id>/', views.sua_khoa_phong_view, name='sua_khoa_phong'),
    path('them-thiet-bi/', views.them_thiet_bi_view, name='them_thiet_bi'),
    path('tai-san-cntt/', views.danh_sach_tai_san_view, name='danh_sach_tai_san'),
    path('xoa-thiet-bi/<int:id>/', views.xoa_thiet_bi_view, name='xoa_thiet_bi'),
    path('sua-thiet-bi/<int:id>/', views.sua_thiet_bi_view, name='sua_thiet_bi'),
    path('luu-sua-chua/', views.luu_sua_chua_view, name='luu_sua_chua'),
    path('hoan-tat-sua-chua/', views.hoan_tat_sua_chua_view, name='hoan_tat_sua_chua'),
    path('api/lich-su-sua-chua/<int:tb_id>/', views.lay_lich_su_sua_chua_api, name='api_lich_su'),
    path('bao-cao-sua-chua/', views.bao_cao_sua_chua_view, name='bao_cao_sua_chua'),
    path('bao-cao/xuat-excel/', views.xuat_excel_sua_chua, name='xuat_excel_sua_chua'),
    path('bao-cao/xuat-pdf/', views.xuat_pdf_sua_chua, name='xuat_pdf_sua_chua'),
    path('them-vat-tu/', views.them_vat_tu_view, name='them_vat_tu'),
    path('vat-tu-cntt/', views.danh_sach_vat_tu_view, name='danh_sach_vat_tu'),
    path('xoa-vat-tu/<int:id>/', views.xoa_vat_tu_view, name='xoa_vat_tu'),
    path('sua-vat-tu/<int:id>/', views.sua_vat_tu_view, name='sua_vat_tu'),
    path('api/luu-phieu-nhap/', views.luu_phieu_nhap_kho_api, name='api_luu_phieu_nhap'),
    path('quan-ly-phieu-nhap/', views.danh_sach_phieu_nhap_view, name='danh_sach_phieu_nhap'),
    path('api/chi-tiet-phieu-nhap/<int:phieu_id>/', views.chi_tiet_phieu_nhap_api, name='api_chi_tiet_phieu'),
    path('xoa-phieu-nhap/<int:id>/', views.xoa_phieu_nhap_view, name='xoa_phieu_nhap'),
    path('sua-phieu-nhap/<int:id>/', views.sua_phieu_nhap_view, name='sua_phieu_nhap'),
    path('api/cap-nhat-phieu-nhap/<int:id>/', views.cap_nhat_phieu_nhap_api, name='api_cap_nhat_phieu'),
    path('api/luu-phieu-xuat/', views.luu_phieu_xuat_kho_api, name='api_luu_phieu_xuat'),
    path('quan-ly-phieu-xuat/', views.danh_sach_phieu_xuat_view, name='danh_sach_phieu_xuat'),
    path('api/chi-tiet-phieu-xuat/<int:phieu_id>/', views.chi_tiet_phieu_xuat_api, name='api_chi_tiet_phieu_xuat'),
    path('xoa-phieu-xuat/<int:id>/', views.xoa_phieu_xuat_view, name='xoa_phieu_xuat'),
    path('sua-phieu-xuat/<int:id>/', views.sua_phieu_xuat_view, name='sua_phieu_xuat'),
    path('api/cap-nhat-phieu-xuat/<int:id>/', views.cap_nhat_phieu_xuat_api, name='api_cap_nhat_phieu_xuat'),
    path('bao-cao/nhap-xuat/', views.bao_cao_nhap_xuat_view, name='bao_cao_nhap_xuat'),
    path('api/ton-kho-khoa/<int:khoa_id>/', views.lay_ton_kho_theo_khoa_api, name='api_ton_kho_khoa'),
    path('bao-cao/nhap-xuat/', views.bao_cao_nhap_xuat_view, name='bao_cao_nhap_xuat'),
    path('bao-cao/nhap-xuat/excel/', views.xuat_excel_nhap_xuat, name='xuat_excel_nhap_xuat'),
    path('bao-cao/nhap-xuat/pdf/', views.xuat_pdf_nhap_xuat, name='xuat_pdf_nhap_xuat'),
    path('bao-cao/thiet-bi-hong/', views.bao_cao_thiet_bi_hong_view, name='bao_cao_thiet_bi_hong'),
    path('thanh-ly-tai-san/', views.thanh_ly_tai_san_view, name='thanh_ly_tai_san'),
    path('bao-cao/thanh-ly/', views.bao_cao_thanh_ly_view, name='bao_cao_thanh_ly'),
    path('huy-thanh-ly/<int:id>/', views.huy_thanh_ly_view, name='huy_thanh_ly'),
    path('sua-thanh-ly/<int:id>/', views.sua_thanh_ly_view, name='sua_thanh_ly'),
    path('huy-hong-han/<int:id>/', views.huy_hong_han_view, name='huy_hong_han'),
    path('sua-loi-hu-hong/<int:id>/', views.sua_loi_hu_hong_view, name='sua_loi_hu_hong'),
    path('danh-muc/nhan-vien/', views.them_nhan_vien_view, name='them_nhan_vien'),
    path('danh-muc/nhan-vien/xoa/<int:id>/', views.xoa_nhan_vien_view, name='xoa_nhan_vien'),
    path('danh-muc/nhan-vien/sua/<int:id>/', views.sua_nhan_vien_view, name='sua_nhan_vien'),
    path('giao-ban-cntt/', views.giao_ban_cntt_view, name='giao_ban_cntt'),
    path('giao-ban-cntt/luu/', views.luu_giao_ban_view, name='luu_giao_ban'),
    path('giao-ban-cntt/xoa/<int:id>/', views.xoa_giao_ban_view, name='xoa_giao_ban'),
    path('giao-ban-cntt/sua/<int:id>/', views.sua_giao_ban_view, name='sua_giao_ban'),
    path('ton-kho-khoa-phong/', views.ton_kho_khoa_phong_view, name='ton_kho_khoa_phong'),
    path('api/bao-hong-vat-tu/', views.bao_hong_vat_tu_api, name='api_bao_hong_vat_tu'), # THÊM DÒNG NÀY
    path('api/chi-tiet-bao-hong/', views.chi_tiet_bao_hong_api, name='api_chi_tiet_bao_hong'),
    path('api/hoan-tac-bao-hong/<int:id>/', views.hoan_tac_bao_hong_api, name='api_hoan_tac_bao_hong'),
    path('api/xuat-tieu-hao/', views.xuat_tieu_hao_api, name='api_xuat_tieu_hao'),
    # ĐƯỜNG DẪN BÁO CÁO TIÊU HAO
    path('bao-cao/tieu-hao/', views.bao_cao_tieu_hao_view, name='bao_cao_tieu_hao'),
    path('api/hoan-tac-tieu-hao/<int:id>/', views.hoan_tac_tieu_hao_api, name='api_hoan_tac_tieu_hao'),
    # THÊM DÒNG NÀY ĐỂ JAVASCRIPT LẤY DỮ LIỆU ĐỔ VÀO POPUP:
    path('api/chi-tiet-tieu-hao/', views.chi_tiet_tieu_hao_api, name='api_chi_tiet_tieu_hao'),
    
    path('api/hoan-tac-tieu-hao/<int:id>/', views.hoan_tac_tieu_hao_api, name='api_hoan_tac_tieu_hao'),
    # ĐƯỜNG DẪN BÁO CÁO CHI TIẾT NHẬP XUẤT VẬT TƯ
    path('bao-cao/chi-tiet-nhap-xuat/', views.bao_cao_chi_tiet_nhap_xuat_view, name='bao_cao_chi_tiet_nhap_xuat'),
    path('api/in-phieu-nhap/<int:phieu_id>/', views.in_phieu_nhap_pdf, name='in_phieu_nhap_pdf'),
    path('api/in-phieu-xuat/<int:phieu_id>/', views.in_phieu_xuat_pdf, name='in_phieu_xuat_pdf'),
    # API lưu sửa chữa ngầm
    path('api/luu-sua-chua-ajax/', views.luu_sua_chua_ajax_api, name='luu_sua_chua_ajax'),
    
    # API xuất phôi PDF sửa chữa
    path('api/in-phieu-sua-chua/<int:ls_id>/', views.in_phieu_sua_chua_pdf, name='in_phieu_sua_chua_pdf'),
    # API hoàn tất sửa chữa
    path('api/hoan-tat-sua-chua-ajax/', views.hoan_tat_sua_chua_ajax_api, name='hoan_tat_sua_chua_ajax'),
    path('api/in-phieu-hoan-tat/<int:ls_id>/', views.in_phieu_hoan_tat_pdf, name='in_phieu_hoan_tat_pdf'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
