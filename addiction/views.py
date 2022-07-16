# 引入redirect重定向模块
from django.shortcuts import render, redirect, get_object_or_404
# 引入User模型
from django.contrib.auth.models import User
# 引入HttpResponse
from django.http import HttpResponse
# 导入数据模型AddictionPost, AddictionColumn
from .models import AddictionPost, AddictionColumn
# 引入刚才定义的AddictionPostForm表单类
from .forms import AddictionPostForm
# 引入markdown模块
import markdown
# 引入login装饰器
from django.contrib.auth.decorators import login_required
# 引入分页模块
from django.core.paginator import Paginator
# 引入搜索 Q 对象
from django.db.models import Q
# Comment_addiction 模型
from comment_addiction.models import Comment_addiction

from comment_addiction.forms import CommentForm_addiction

# 通用类视图
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView

# from my_blog.settings import LOGGING
# import logging

# logging.config.dictConfig(LOGGING)
# logger = logging.getLogger('django.request')


# 文章列表
def addiction_list(request):
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    # 初始化查询集
    addiction_list = AddictionPost.objects.all()

    # 搜索查询集
    if search:
        addiction_list = addiction_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        # 将 search 参数重置为空
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        addiction_list = addiction_list.filter(column=column)

    # 标签查询集
    if tag and tag != 'None':
        addiction_list = addiction_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        # 按热度排序博文
        addiction_list = addiction_list.order_by('-total_views')

    # 每页显示 1 篇文章
    paginator = Paginator(addiction_list, 3)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 addictions
    addictions = paginator.get_page(page)
    # 需要传递给模板（templates）的对象
    context = {
        'addictions': addictions,
        'order': order,
        'search': search,
        'column': column,
        'tag': tag,
    }
    # render函数：载入模板，并返回context对象
    return render(request, 'addiction/list.html', context)


# 文章详情
def addiction_detail(request, id):
    # 取出相应的文章
    # addiction = AddictionPost.objects.get(id=id)
    # logger.warning('Something went wrong!')
    addiction = get_object_or_404(AddictionPost, id=id)
    
    # 取出文章评论
    comments = Comment_addiction.objects.filter(addiction=id)

    # 浏览量 +1
    addiction.total_views += 1
    addiction.save(update_fields=['total_views'])

    # 相邻发表文章的快捷导航
    pre_addiction = AddictionPost.objects.filter(id__lt=addiction.id).order_by('-id')
    next_addiction = AddictionPost.objects.filter(id__gt=addiction.id).order_by('id')
    if pre_addiction.count() > 0:
        pre_addiction = pre_addiction[0]
    else:
        pre_addiction = None

    if next_addiction.count() > 0:
        next_addiction = next_addiction[0]
    else:
        next_addiction = None


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
    addiction.body = md.convert(addiction.body)

    # 为评论引入表单
    comment_form = CommentForm()

    # 需要传递给模板的对象
    context = { 
        'addiction': addiction,
        'toc': md.toc,
        'comments': comments,
        'pre_addiction': pre_addiction,
        'next_addiction': next_addiction,
        'comment_form': comment_form,
    }
    # 载入模板，并返回context对象
    return render(request, 'addiction/detail.html', context)


# 写文章的视图
@login_required(login_url='/userprofile/login/')
def addiction_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        addiction_post_form = AddictionPostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if addiction_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_addiction = addiction_post_form.save(commit=False)
            # 指定登录的用户为作者
            new_addiction.author = User.objects.get(id=request.user.id)
            if request.POST['column'] != 'none':
                # 保存文章栏目
                new_addiction.column = AddictionColumn.objects.get(id=request.POST['column'])
            # 将新文章保存到数据库中
            new_addiction.save()
            # 保存 tags 的多对多关系
            addiction_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("addiction:addiction_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        addiction_post_form = AddictionPostForm()
        # 文章栏目
        columns = AddictionColumn.objects.all()
        # 赋值上下文
        context = { 'addiction_post_form': addiction_post_form, 'columns': columns }
        # 返回模板
        return render(request, 'addiction/create.html', context)


# 删除文章，此方式有 csrf 攻击风险
@login_required(login_url='/userprofile/login/')
def addiction_delete(request, id):
    # 根据 id 获取需要删除的文章
    addiction = AddictionPost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != addiction.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    # 调用.delete()方法删除文章
    addiction.delete()
    # 完成删除后返回文章列表
    return redirect("addiction:addiction_list")


# 安全删除文章
@login_required(login_url='/userprofile/login/')
def addiction_safe_delete(request, id):
    if request.method == 'POST':
        addiction = AddictionPost.objects.get(id=id)
        if request.user != addiction.author:
            return HttpResponse("抱歉，你无权修改这篇文章。")
        addiction.delete()
        return redirect("addiction:addiction_list")
    else:
        return HttpResponse("仅允许post请求")


# 更新文章
@login_required(login_url='/userprofile/login/')
def addiction_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """

    # 获取需要修改的具体文章对象
    addiction = AddictionPost.objects.get(id=id)

    # 过滤非作者的用户
    if request.user != addiction.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        addiction_post_form = AddictionPostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if addiction_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            addiction.title = request.POST['title']
            addiction.body = request.POST['body']

            if request.POST['column'] != 'none':
                # 保存文章栏目
                addiction.column = AddictionColumn.objects.get(id=request.POST['column'])
            else:
                addiction.column = None

            if request.FILES.get('avatar'):
                addiction.avatar = request.FILES.get('avatar')

            addiction.tags.set(*request.POST.get('tags').split(','), clear=True)
            addiction.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("addiction:addiction_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        addiction_post_form = AddictionPostForm()

        # 文章栏目
        columns = AddictionColumn.objects.all()
        # 赋值上下文，将 addiction 文章对象也传递进去，以便提取旧的内容
        context = { 
            'addiction': addiction, 
            'addiction_post_form': addiction_post_form,
            'columns': columns,
            'tags': ','.join([x for x in addiction.tags.names()]),
        }

        # 将响应返回到模板中
        return render(request, 'addiction/update.html', context)


# 点赞数 +1
class IncreaseLikesView(View):
    def post(self, request, *args, **kwargs):
        addiction = AddictionPost.objects.get(id=kwargs.get('id'))
        addiction.likes += 1
        addiction.save()
        return HttpResponse('success')


def addiction_list_example(request):
    """
    与下面的类视图做对比的函数
    简单的文章列表
    """
    if request.method == 'GET':
        addictions = AddictionPost.objects.all()
        context = {'addictions': addictions}
        return render(request, 'addiction/list.html', context)



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


class AddictionListView(ContextMixin, ListView):
    """
    文章列表类视图
    """
    # 查询集的名称
    context_object_name = 'addictions'
    # 模板
    template_name = 'addiction/list.html'

    def get_queryset(self):
        """
        查询集
        """
        queryset = AddictionPost.objects.filter(title='Python')
        return queryset


class AddictionDetailView(DetailView):
    """
    文章详情类视图
    """
    queryset = AddictionPost.objects.all()
    context_object_name = 'addiction'
    template_name = 'addiction/detail.html'

    def get_object(self):
        """
        获取需要展示的对象
        """
        # 首先调用父类的方法
        obj = super(AddictionDetailView, self).get_object()
        # 浏览量 +1
        obj.total_views += 1
        obj.save(update_fields=['total_views'])
        return obj


class AddictionCreateView(CreateView):
    """
    创建文章的类视图
    """
    model = AddictionPost
    fields = '__all__'
    # 或者有选择的提交字段，比如：
    # fields = ['title']
    template_name = 'addiction/create_by_class_view.html'