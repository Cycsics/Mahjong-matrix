from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse

from .forms import CommentForm_mental
from mental.models import MentalPost
from .models import Comment_mental

from notifications.signals import notify
from django.contrib.auth.models import User


# 文章评论
@login_required(login_url='/userprofile/login/')
def post_comment(request, mental_id, parent_comment_id=None):
    mental = get_object_or_404(MentalPost, id=mental_id)

    # 处理 POST 请求
    if request.method == 'POST':
        comment_form = CommentForm_mental(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.mental = mental
            new_comment.user = request.user

            # 二级回复
            if parent_comment_id:
                parent_comment = Comment_mental.objects.get(id=parent_comment_id)
                # 若回复层级超过二级，则转换为二级
                new_comment.parent_id = parent_comment.get_root().id
                # 被回复人
                new_comment.reply_to = parent_comment.user
                new_comment.save()

                # 给其他用户发送通知
                if not parent_comment.user.is_superuser and not parent_comment.user == request.user:
                    notify.send(
                        request.user,
                        recipient=parent_comment.user,
                        verb='回复了你',
                        target=mental,
                        action_object=new_comment,
                    )

                # return HttpResponse("200 OK")
                return JsonResponse({"code": "200 OK", "new_comment_id": new_comment.id})

            new_comment.save()
            
            # 给管理员发送通知
            if not request.user.is_superuser:
                notify.send(
                        request.user,
                        recipient=User.objects.filter(is_superuser=1),
                        verb='回复了你',
                        target=mental,
                        action_object=new_comment,
                    )

            # 添加锚点
            redirect_url = mental.get_absolute_url() + '#comment_elem_' + str(new_comment.id)
            return redirect(redirect_url)
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 处理 GET 请求
    elif request.method == 'GET':
        comment_form = CommentForm_mental()()
        context = {
            'comment_form': comment_form,
            'mental_id': mental_id,
            'parent_comment_id': parent_comment_id
        }
        return render(request, 'comment_mental/reply.html', context)
    # 处理其他请求
    else:
        return HttpResponse("仅接受GET/POST请求。")
