from django.shortcuts import render
# 从django.http模块中导入HttpResponse对象
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from datetime import datetime
from registration.backends.simple.views import RegistrationView

# def index(request):
#     # return HttpResponse("Rango says hey there partner！")
#     # 构建一个字典，作为上下文传给模版引擎
#     # 注意，boldmessage键对应于模版中的{{ boldmessage }}
#     context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
#     # 返回一个渲染后的响应发给客户端
#     # 为了方便，我们使用的是 render 函数的简短形式
#     # 注意，第二个参数是我们想使用的模板
#     return render(request, 'rango/index.html', context=context_dict)
def index(request):
    # 测试是否支持cookie
    request.session.set_test_cookie()
    # 查询数据库，获取目前存储的所有分类
    # 按点赞次数倒序排列分类
    # 获取前5个分类(如果少于5个那就获取全部)
    # 把分类列表嵌入context_dict字典
    # 传给模版引擎
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}
    # 渲染响应，发给客户端
    return render(request, 'rango/imageIndex.html', context_dict)

def imageIndex(request):
    # 测试是否支持cookie
    request.session.set_test_cookie()
    # contex_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'page': page_list}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    # 返回response对象，更新目标cookie
    response = render(request, 'rango/imageIndex.html', context_dict)
    return response

def about(request):
    if request.session.test_cookie_worked():
        print('TEST COOKIE WORKED!')
        request.session.delete_test_cookie()
    return render(request, 'rango/about.html', {})

def show_category(request, category_name_slug):
    # 创建上下文字典，稍后传给模版渲染引擎
    print('category_name_sulg的值为：' + category_name_slug)
    context_dict = {}
    try:
        # 能通过传入的分类别名找到对应的分类吗？
        # 如果找不到，.get()方法抛出DoesNoExist异常
        # 因此.get()方法返回一个模型实例或抛出异常
        category = Category.objects.get(slug=category_name_slug)
        # 检索关联的所有网页
        # 注意，filter()返回一个网页对象列表或空列表
        pages = Page.objects.filter(category=category)
        # 把得到的列表赋值给模版上下文中名为page的键
        context_dict['page'] = pages
        # 也把从数据库中获取的category对象添加到上下文字典中
        # 我们将在模版中通过这个变量确认分类是否存在
        context_dict['category'] = category
    except:
        # 没有找到指定的分类时执行这里
        # 什么也不做
        # 模版会显示消息，指明分类不存在
        context_dict['category'] = None
        context_dict['pages'] = None
    # 渲染响应，返回给客户端
    return render(request, 'rango/category.html', context_dict)

def add_category(request):
    form = CategoryForm()
    # 是HTTP POST 请求吗？
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        # 表单数据有效吗
        if form.is_valid():
            # 把新分类存入数据库
            form.save(commit=True)
            # 保存新分类后可以显示一个确认消息
            # 不过最受欢迎的分类在首页
            # 那就把用户带到首页把
            return index(request)
        else:
            # 表单数据有错误
            # 直接在终端里打印出来
            print(form.errors)
    # 处理有效数据和无效数据之后
    # 渲染表单，并显示可能出现的错误消息
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    form = PageForm()
    if form.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    # 一个布尔值，告诉模版注册是否成功
    # 一个开始设为False，注册成功后改为True
    registered = False
    # 如果是HTTP POST请求，处理表单数据
    if request.method == 'POST':
        # 尝试获取原始表单数据
        # 注意，UserForm和UserProfileForm中的数据都需要
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        # 如果两个表单中的数据是有效的
        if user_form.is_valid() and profile_form.is_valid():
            # 把UserForm中的数据存入数据库
            user = user_form.save()
            # 使用set_password方法计算密码哈希值
            # 然后更新user对象
            user.set_password(user.password)
            user.save()
            # 现在处理UserProfile实例
            # 因为要自行处理user属性，所以设定commit=False
            # 延迟保存模型，以防止出现完整性问题
            profile = profile_form.save(commit=False)
            profile.user = user

            # 用户提供头像了吗？
            # 如果提供了，从表单数据库中提取出来，赋给UserProfile模型
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            # 保存UserProfile模型实例
            profile.save()
            # 更新变量的值，告诉模版成功注册了
            registered = True
        else:
            # 表单数据无效，出错了？
            # 在终端打印问题
            print(user_form.errors, profile_form.errors)
    else:
        # 不是HTTP POST请求，渲染两个ModelForm实例
        # 表单为空，待用户填写
        user_form = UserForm()
        profile_form = UserProfileForm()

    # 根据上下文渲染模版
    return render(request, 'rango/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):
    # 如果是HTTP POST请求，尝试获取相关信息
    if request.method == 'POST':
        # 获取用户在登录表单中输入的用户名和密码
        # 我们使用的是 request.POST.get('<variable>')
        # 而不是 request.POST['<variable>']
        # 这是因为对应的值不存在时，前者返回 None，
        # 而后者抛出 KeyError 异常
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 使用Django提供的函数检查username/password是否有效
        # 如果有效，返回一个User对象
        user = authenticate(username=username, password=password)
        # 如果得到了User对象，说明用户输入的凭据是对的
        # 如果是None(python表示没有值的方式)，说明没找到与凭据匹配的用户
        if user:
            # 账户激活了吗？可能被禁了
            if user.is_active:
                # 登入有效且已激活的账户
                # 然后重定向首页
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # 账户未激活，禁止登录
                return HttpResponse('Your Rango account is disabled.')
        else:
            # 提供的登录凭据有问题，不能登录
            print('Invalid login details:{0}, {1}'.format(username, password))
            return HttpResponse("Invalid login details supplied.")
    # 不是HTTP POST请求，显示登录表单
    # 极有可能是HTTP GET请求
    else:
        # 没什么上下文变量要传给模版系统
        # 因此传入一个空字典
        return render(request, 'rango/login.html', {})

# 辅助函数
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

# def visitor_cookie_handler(request, response):
#     # 获取网站的访问次数
#     # 使用COOKIES.get()函数读取"visits"cookie
#     # 如果目标cookie存在，把值转换为整数
#     # 如果目标cookie不存在，返回默认值1
#     visits = int(request.COOKIES.get('visits', '1'))
#     last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
#     last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
#     # 如果距上次访问超过一天
#     if (datetime.now() - last_visit_time).days > 0:
#         visits = visits + 1
#         # 增加访问次数后更新"last_visit"cookie
#         response.set_cookie('last_visit', str(datetime.now()))
#     else:
#         # 设定"last_visit"cookie
#         response.set_cookie('last_visit', last_visit_cookie)
#     # 更新或设定"visits"cookie
#     response.set_cookie('visits', visits)
# 更新后的函数定义
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    # 如果距上次访问超过一天
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # 增加访问次数后更新"last_visit"cookie
        request.session['last_visit'] = str(datetime.now())
    else:
        # 设定"last_visit"cookie
        request.session['last_visit'] = last_visit_cookie
    # 更新或设定"visits"cookie
    request.session['visits'] = visits

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

# 使用login_required()装饰器限制
# 只有已登录的用户才能访问这个视图
@login_required
def user_logout(request):
    # 可以确定用户已登录，因此直接退出
    logout(request)
    # 把用户带回首页
    return HttpResponseRedirect(reverse('index'))

class RangoRegistrationView(RegistrationView):
    def get_success_url(self, user):
        return reverse('register_profile')