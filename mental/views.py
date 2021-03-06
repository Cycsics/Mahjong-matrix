# 引入redirect重定向模块
from django.shortcuts import render, redirect, get_object_or_404
# 引入User模型
from django.contrib.auth.models import User
# 引入HttpResponse
from django.http import HttpResponse
# 导入数据模型MentalPost
from .models import MentalPost
# 引入刚才定义的MentalPostForm表单类
from .forms import MentalPostForm
# 引入markdown模块
import markdown
# 引入login装饰器
from django.contrib.auth.decorators import login_required
# 引入分页模块
from django.core.paginator import Paginator
# 引入搜索 Q 对象
from django.db.models import Q
# Comment_mental 模型
from comment_mental.models import Comment_mental

from comment_mental.forms import CommentForm_mental

# 通用类视图
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView

# from my_blog.settings import LOGGING
# import logging

# logging.config.dictConfig(LOGGING)
# logger = logging.getLogger('django.request')


# 文章列表
def mental_list(request):
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    tag = request.GET.get('tag')

    # 初始化查询集
    mental_list = MentalPost.objects.all()

    # 搜索查询集
    if search:
        mental_list = mental_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        # 将 search 参数重置为空
        search = ''


    # 标签查询集
    if tag and tag != 'None':
        mental_list = mental_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        # 按热度排序博文
        mental_list = mental_list.order_by('-total_views')

    # 每页显示 1 篇文章
    paginator = Paginator(mental_list, 3)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 mentals
    mentals = paginator.get_page(page)
    # 需要传递给模板（templates）的对象
    context = {
        'mentals': mentals,
        'order': order,
        'search': search,
        'tag': tag,
    }
    # render函数：载入模板，并返回context对象
    return render(request, 'mental/list.html', context)


# 文章详情
def mental_detail(request, id):
    # 取出相应的文章
    # mental = MentalPost.objects.get(id=id)
    # logger.warning('Something went wrong!')
    mental = get_object_or_404(MentalPost, id=id)
    
    # 取出文章评论
    comments = Comment_mental.objects.filter(mental=id)

    # 浏览量 +1
    mental.total_views += 1
    mental.save(update_fields=['total_views'])

    # 相邻发表文章的快捷导航
    pre_mental = MentalPost.objects.filter(id__lt=mental.id).order_by('-id')
    next_mental = MentalPost.objects.filter(id__gt=mental.id).order_by('id')
    if pre_mental.count() > 0:
        pre_mental = pre_mental[0]
    else:
        pre_mental = None

    if next_mental.count() > 0:
        next_mental = next_mental[0]
    else:
        next_mental = None


    # Markdown 语法渲染
    md = markdown.Markdown(
        extensions=[
        # 包含 缩写、表格等常用扩展
        'markdown.extensions.extra',
        # 语法高亮扩展
        'markdown.extensions.codehilite',
        # 目录扩展
        'markdown.extensions.toc',
        ]
    )
    mental.body = md.convert(mental.body)

    # 为评论引入表单
    comment_form = CommentForm_mental()

    # 需要传递给模板的对象
    context = { 
        'mental': mental,
        'toc': md.toc,
        'comments': comments,
        'pre_mental': pre_mental,
        'next_mental': next_mental,
        'comment_form': comment_form,
    }
    # 载入模板，并返回context对象
    return render(request, 'mental/detail.html', context)


# 写文章的视图
@login_required(login_url='/userprofile/login/')
def mental_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        mental_post_form = MentalPostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if mental_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_mental = mental_post_form.save(commit=False)
            # 指定登录的用户为作者
            new_mental.author = User.objects.get(id=request.user.id)
            # 将新文章保存到数据库中
            new_mental.save()
            # 保存 tags 的多对多关系
            mental_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("mental:mental_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        mental_post_form = MentalPostForm()
        # 赋值上下文
        context = { 'mental_post_form': mental_post_form }
        # 返回模板
        return render(request, 'mental/create.html', context)


# 删除文章，此方式有 csrf 攻击风险
@login_required(login_url='/userprofile/login/')
def mental_delete(request, id):
    # 根据 id 获取需要删除的文章
    mental = MentalPost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != mental.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    # 调用.delete()方法删除文章
    mental.delete()
    # 完成删除后返回文章列表
    return redirect("mental:mental_list")


# 安全删除文章
@login_required(login_url='/userprofile/login/')
def mental_safe_delete(request, id):
    if request.method == 'POST':
        mental = MentalPost.objects.get(id=id)
        if request.user != mental.author:
            return HttpResponse("抱歉，你无权修改这篇文章。")
        mental.delete()
        return redirect("mental:mental_list")
    else:
        return HttpResponse("仅允许post请求")


# 更新文章
@login_required(login_url='/userprofile/login/')
def mental_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """

    # 获取需要修改的具体文章对象
    mental = MentalPost.objects.get(id=id)

    # 过滤非作者的用户
    if request.user != mental.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        mental_post_form = MentalPostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if mental_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            mental.title = request.POST['title']
            mental.body = request.POST['body']


            if request.FILES.get('avatar'):
                mental.avatar = request.FILES.get('avatar')

            mental.tags.set(*request.POST.get('tags').split(','), clear=True)
            mental.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("mental:mental_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        mental_post_form = MentalPostForm()

        # 赋值上下文，将 mental 文章对象也传递进去，以便提取旧的内容
        context = { 
            'mental': mental, 
            'mental_post_form': mental_post_form,
            'tags': ','.join([x for x in mental.tags.names()]),
        }

        # 将响应返回到模板中
        return render(request, 'mental/update.html', context)


# 点赞数 +1
class IncreaseLikesView(View):
    def post(self, request, *args, **kwargs):
        mental = MentalPost.objects.get(id=kwargs.get('id'))
        mental.likes += 1
        mental.save()
        return HttpResponse('success')


def mental_list_example(request):
    """
    与下面的类视图做对比的函数
    简单的文章列表
    """
    if request.method == 'GET':
        mentals = MentalPost.objects.all()
        context = {'mentals': mentals}
        return render(request, 'mental/list.html', context)



class ContextMixin:
    """
    Mixin
    """
    def get_context_data(self, **kwargs):
        # 获取原有的上下文
        context = super().get_context_data(**kwargs)
        # 增加新上下文
        context['order'] = 'total_views'
        return context


class MentalListView(ContextMixin, ListView):
    """
    文章列表类视图
    """
    # 查询集的名称
    context_object_name = 'mentals'
    # 模板
    template_name = 'mental/list.html'

    def get_queryset(self):
        """
        查询集
        """
        queryset = MentalPost.objects.filter(title='Python')
        return queryset


class MentalDetailView(DetailView):
    """
    文章详情类视图
    """
    queryset = MentalPost.objects.all()
    context_object_name = 'mental'
    template_name = 'mental/detail.html'

    def get_object(self):
        """
        获取需要展示的对象
        """
        # 首先调用父类的方法
        obj = super(MentalDetailView, self).get_object()
        # 浏览量 +1
        obj.total_views += 1
        obj.save(update_fields=['total_views'])
        return obj


class MentalCreateView(CreateView):
    """
    创建文章的类视图
    """
    model = MentalPost
    fields = '__all__'
    # 或者有选择的提交字段，比如：
    # fields = ['title']
    template_name = 'mental/create_by_class_view.html'