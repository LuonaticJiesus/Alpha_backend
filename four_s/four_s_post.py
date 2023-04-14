import json
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from four_s.models import Block, Permission, Post, UserInfo, PostLike, Comment


def wrap_posts(post_query_set, user_id):
    posts = []
    for p in post_query_set:
        p_dict = p.to_dict()
        p_dict['user_name'] = UserInfo.objects.get(user_id=p.user_id)
        p_dict['block_name'] = Block.objects.get(block_id=p.block_id)
        p_dict['like_cnt'] = PostLike.objects.filter(post_id=p.post_id).count()
        p_dict['comment_cnt'] = Comment.objects.filter(post_id=p.post_id).count()
        p_dict['like_state'] = 1 if PostLike.objects.filter(user_id=user_id).filter(post_id=p.post_id).exists() else 0
        comment_query_set = Comment.objects.filter(post_id=p.post_id).order_by('-time')
        if comment_query_set is None:
            p_dict['latest_update_user'] = p_dict['user_name']
            p_dict['latest_time'] = p.time
        else:
            comment_user_id = comment_query_set[0].user_id
            p_dict['latest_update_user'] = UserInfo.objects.get(user_id=comment_user_id).name
            p_dict['latest_time'] = comment_query_set[0].time
        posts.append(p_dict)
    return posts


@csrf_exempt
def post_query_title(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        post_name = request.GET.get('post_name')
        post_query_set = Post.objects.filter(title__contains=post_name)
        posts = wrap_posts(post_query_set, user_id)
        return JsonResponse({'status': 0, 'info': '查询成功', 'data': posts})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def post_query_block(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        block_id = request.GET.get('block_id')
        if block_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        block_id = int(block_id)
        if not Block.objects.filter(block_id=block_id).exists():
            return JsonResponse({'status': -1, 'info': '约束错误'})
        post_query_set = Post.objects.filter(block_id=block_id).order_by('-time')
        posts = wrap_posts(post_query_set, user_id)
        return JsonResponse({'status': 0, 'info': '查询成功', 'data': posts})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def post_query_user(request):
    if request.method != 'GET':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        userid = int(request.META.get('HTTP_USERID'))
        user_id = request.GET.get('user_id')
        if user_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        user_id = int(user_id)
        if not UserInfo.objects.filter(user_id=user_id).exists():
            return JsonResponse({'status': -1, 'info': '约束错误'})
        post_query_set = Post.objects.filter(user_id=user_id).order_by('-time')
        posts = wrap_posts(post_query_set, userid)
        return JsonResponse({'status': 0, 'info': '查询成功', 'data': posts})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def post_publish(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        title = data.get('title')
        txt = data.get('txt')
        block_id = data.get('block_id')
        if title is None or txt is None or block_id is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        block_id = int(block_id)
        if not Block.objects.filter(block_id=block_id).exists():
            return JsonResponse({'status': -1, 'info': '约束错误'})
        if not Permission.objects.filter(user_id=user_id).filter(block_id=block_id).filter(permission__gte=1).exists():
            return JsonResponse({'status': -1, 'info': '权限不足'})
        post = Post(title=title, user_id=user_id, txt=txt, block_id=block_id, time=datetime.now())
        post.save()
        return JsonResponse({'status': 0, 'info': '已发布'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})


@csrf_exempt
def post_like(request):
    if request.method != 'POST':
        return JsonResponse({'status': -1, 'info': '请求方式错误'})
    try:
        user_id = int(request.META.get('HTTP_USERID'))
        data = json.loads(request.body)
        post_id = data.get('post_id')
        like = data.get('like')
        if post_id is None or like is None:
            return JsonResponse({'status': -1, 'info': '缺少参数'})
        post_id = int(post_id)
        post_query_set = Post.objects.filter(post_id=post_id)
        if post_query_set is None:
            return JsonResponse({'status': -1, 'info': '约束错误'})
        if like == 0:
            PostLike.objects.filter(post_id=post_id).filter(user_id=user_id).delete()
        elif not PostLike.objects.filter(post_id=post_id).filter(user_id=user_id).exists():
            new_like = PostLike(post_id=post_id, user_id=user_id)
            new_like.save()
        return JsonResponse({'status': 0, 'info': '操作成功'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': -1, 'info': '操作错误，查询失败'})
