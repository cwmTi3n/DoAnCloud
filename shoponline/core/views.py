from django.shortcuts import render, redirect
from .models import sanpham, danhmuc, giohang, donhang, user
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views import View
from django.contrib.auth import authenticate, login, logout, decorators
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
import random
# Create your views here.
def get_contact(request):
    return render(request, 'contact.html')
def get_index(request):
    spmoi = sanpham.objects.filter().order_by('-id')[:4]
    sphot = sanpham.objects.filter().order_by('id')[:4]
    return render(request, 'index.html', {'spmoi' : spmoi, 'sphot' : sphot, 'trangchu' : 'active'})

def get_sanpham(request, id):
    sp = sanpham.objects.get(id = id)
    return render(request, 'product.html', {'sp' : sp})

def get_danhmuc(request):
    if request.method == 'GET':
        id = request.GET.get('id', 0)
        keyword = ''
    else:
        id = 0
        keyword = request.POST['keyword']
    try:
        if id == 0:
            sanphams = sanpham.objects.filter(Q(ten__icontains = keyword) | Q(mota__icontains = keyword)).order_by('ten')
        else:
            sanphams = sanpham.objects.filter(Q(danhmuc = id), (Q(ten__icontains = keyword) | Q(mota__icontains = keyword))).order_by('ten')
    except:
        sanphams = sanpham.objects.filter(Q(ten__icontains = keyword) | Q(mota__icontains = keyword)).order_by('ten')
    context = paging_sanpham(request, sanphams, 1, id, keyword)
    return render(request, 'category.html', context)

def deleteDh(request, id):
    dh = donhang.objects.get(id = id)
    dh.delete()
    return redirect('/giohang')

def get_all_gh(request):
    giohangs = giohang.objects.filter(trangthai=True, user=request.user)
    return render(request, 'person.html', {'giohangs' : giohangs, 'person' : 'active'})

def get_detail_gh(request, id):
    gh = giohang.objects.get(user= request.user, trangthai=True, id = id)
    donhangs = gh.donhangs.all()
    return render(request, 'detail-giohang.html', {'donhangs' : donhangs, 'person' : 'active'})

def paging_sanpham(request, sanphams, page_num, danhmuc_id, keyword):
    p = Paginator(sanphams, 3)
    categories = danhmuc.objects.filter()
    try:
        dm = danhmuc.objects.get(id = danhmuc_id)
    except:
        dm = None
    page = p.page(page_num)
    return {
            'paginator' : p,
            'sanphams' : page,
            'categories' : categories,
            'dm' : dm,
            'keyword' : keyword,
            'danhmuc' : 'active'
        }
@csrf_exempt
def ajax_load(request):
    keyword = request.POST['keyword']
    danhmuc_id = request.POST['danhmuc_id']
    page_num = request.POST['page']
    orby = request.POST['orby']
    if str(danhmuc_id) == '':
        sanphams = sanpham.objects.filter(Q(ten__icontains = keyword) | Q(mota__icontains = keyword)).order_by(orby)
    else:
        sanphams = sanpham.objects.filter(Q(danhmuc = danhmuc_id), (Q(ten__icontains = keyword) | Q(mota__icontains = keyword))).order_by(orby)
    p = Paginator(sanphams, 3)
    page = p.page(page_num)
    content = ""
    for sp in page:
        content += str("                <div class=\"col-12 col-md-6 col-lg-4\">\r\n"
					+ "                    <div class=\"card\">\r\n"
					+ "                        <img class=\"card-img-top\" src=\"/core/static/" + str(sp.hinhanh) + "\" alt=\"Card image cap\">\r\n"
					+ "                        <div class=\"card-body\">\r\n"
					+ "                            <h4 class=\"card-title\"><a href=\"/sanpham/" + str(sp.id) + "\" title=\"View Product\">" + str(sp.ten) + "</a></h4>\r\n"
					+ "                            <div class=\"row\">\r\n"
					+ "                                <div class=\"col\">\r\n"
					+ "                                    <p class=\"btn btn-danger btn-block\">"+ str(sp.gia) +"</p>\r\n"
					+ "                                </div>\r\n"
					+ "                                <div class=\"col\">\r\n"
					+ "                                    <a href=\"/sanpham/" + str(sp.id) + "\" class=\"btn btn-success btn-block\">Add to cart</a>\r\n"
					+ "                                </div>\r\n"
					+ "                            </div>\r\n"
					+ "                        </div>\r\n"
					+ "                    </div>\r\n"
					+ "                </div>")
    return HttpResponse(content)

@decorators.login_required(login_url='/login')
def get_cart(request):
    gh, created= giohang.objects.get_or_create(user= request.user, trangthai=False)
    donhangs = gh.donhangs.all()
    return render(request, 'cart.html', {'donhangs' : donhangs})

@decorators.login_required(login_url='/login')
@csrf_exempt
def add_donhang(request):
    id_sp = request.POST['id_sp']
    soluong = request.POST['soluong']
    sp = sanpham.objects.get(id = id_sp)
    gh, created = giohang.objects.get_or_create(user= request.user, trangthai=False)
    obj, created = donhang.objects.get_or_create(sanpham=sp, giohang=gh)
    if created == True:
        obj.soluong = soluong
    else:
        obj.soluong += int(soluong)
    obj.save()
    return HttpResponse('???? th??m v??o gi??? h??ng')

@csrf_exempt
def thanhtoan(request):
    gh = giohang.objects.get(user= request.user, trangthai=False)
    gh.diachi = request.POST['diachi']
    gh.trangthai = True
    donhangs = gh.donhangs.all()
    tongtien = 0
    for dh in donhangs:
        tongtien += int(dh.sanpham.gia)
    gh.save()

    text = 'C?? ng?????i v???a m???i ?????t h??ng\n' + '?????a ch???: ' + str(gh.diachi) + '\n' + 'T???ng ti???n: ' + str(tongtien)
    send_mail('????n h??ng m???i', text, 'hokimtien0202@gmail.com', ['hokimtien2002@gmail.com'])

    return redirect('/giohang')

class Login(View):
    def get(self, request):
        return render(request, 'login.html', {'dangnhap' : 'active'})

    def post(self, request):
        us = request.POST['username']
        ps = request.POST['password']
        check = authenticate(username=us, password=ps)
        if check is None:
            return render(request, 'login.html', {'mess' : 'T??n ????ng nh???p ho???c m???t kh???u kh??ng ch??nh x??c'})
        login(request, check)
        return redirect('/')

class Logout(LoginRequiredMixin, View):
    login_url = '/login'
    def get(self, request):
        logout(request)
        return redirect('/')

class Register(View):
    def get(self, request):
        return render(request, 'register.html')
    def post(self, request):
        username = request.POST['username']
        ps = request.POST['password']
        email = request.POST['email']
        ho = request.POST['ho']
        ten = request.POST['ten']
        us = user.objects.create(username = username)
        us.email = email
        us.first_name = ho
        us.last_name = ten
        us.set_password(ps)
        us.save()
        return redirect('/login')

class ChangePw(LoginRequiredMixin, View):
    login_url = '/login'
    def get(self, request):
        return render(request, 'changepw.html')
    def post(self, request):
        us = request.POST['username']
        old_ps = request.POST['old-pw']
        new_ps = request.POST['password']
        check = authenticate(username=us, password=old_ps)
        if check is None:
            return render(request, 'changepw.html', {'mess' : 'M???t kh???u kh??ng ch??nh x??c'})
        else:
            u = user.objects.get(username = us)
            u.set_password(new_ps)
            u.save()
            return redirect('/login')

class ForgotPw(View):
    def get(self, request):
        return render(request, 'forgotpw.html')
    def post(self, request):
        code = random.randint(1000, 9999)
        request.session['code'] = code
        request.session.set_expiry(60)
        us = request.POST['username']
        try:
            u = user.objects.get(username=us)
        except:
            u = None
        if u is None:
            return render(request, 'forgotpw.html', {'mess' : 'T??n ????ng nh???p kh??ng ????ng'})
        else:
            text = 'B???n v???a c?? y??u c???u ?????i m???t kh???u, m?? x??c nh???n l??: ' + str(code)
            send_mail('Y??u c???u ?????i m???t kh???u', text, 'hokimtien0202@gmail.com', [u.email])
            return render(request, 'verify-forgotpw.html', {'username' : us})

def verify_forgetpw(request):
    code = request.POST['verify']
    us = request.POST['username']
    pw = request.POST['password']
    u = user.objects.get(username=us)
    try:
        vf = request.session['code']
    except:
        vf = ''
        return render(request, 'forgotpw.html', {'username' : us, 'mess' : 'M?? x??c nh???n ???? h???t h???n'})
    if str(code) == str(vf):
        u.set_password(pw)
        del request.session['code']
        u.save()
        return redirect('/login')
    else:
        return render(request, 'verify-forgotpw.html', {'username' : us, 'mess' : 'M?? x??c nh???n kh??ng ????ng'})
