from django.shortcuts import render
from block.models import Block
from .models import Article
from django.shortcuts import redirect
from .forms import ArticleForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from comment.models import Comment

def paginate_queryset(objs,page_no,cnt_per_page=10,half_show_length=5):
    p = Paginator(objs,cnt_per_page)
    if page_no > p.num_pages:
        page_no = p.num_pages
    if page_no <= 0:
        page_no = 1
    page_links = [i for i in range(page_no - half_show_length,page_no + half_show_length + 1)
                  if i > 0 and i <=p.num_pages]
    page = p.page(page_no)
    previous_link = page_links[0] - 1
    next_link = page_links[-1] + 1
    pagination_date = {"has_previous":previous_link > 0,
                       "has_next":next_link <= p.num_pages,
                       "previous_link":previous_link,
                       "next_link":next_link,
                       "page_cnt":p.num_pages,
                       "current_no":page_no,
                       "page_links":page_links}
    return(page.object_list,pagination_date)


def article_list(request,block_id):
    block_id=int(block_id)
    block = Block.objects.get(id=block_id)
    all_articles = Article.objects.filter(block=block,status=0).order_by("-id")
    page_no = int(request.GET.get("page_no","1"))
    page_articles,pagination_date = paginate_queryset(all_articles,page_no)
    return render(request,'article_list.html',{"articles":page_articles,"b":block,"pagination_date":pagination_date})

@login_required
def create_page(request,block_id):
    block_id = int(block_id)
    block = Block.objects.get(id=block_id)
    form = ArticleForm(request.POST)
    if form.is_valid():
        article = form.save(commit=False)
        article.block =block
        article.owner=request.user
        article.status=0
        article.save()
        return redirect("/article/list/%s" % block_id)
    else:
        return render(request,"create_page.html",
                    {"b":block,"form":form})

def article_detail(request,article_id):
    article_id = int(article_id)
    article = Article.objects.get(id=article_id)
    block = Block.objects.get(name=article.block)
    all_comments = Comment.objects.filter(article=article_id).order_by("id")
    page_no = int(request.GET.get("page_no","1"))
    page_comments,pagination_date = paginate_queryset(all_comments,page_no,10)
    return render(request,'article_detail.html',{"a":article,"b":block,"comments":page_comments,"pagination_date":pagination_date})
