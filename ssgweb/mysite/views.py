
from blog.models import ISBN
from blog.models import IDF

from django.views.generic.edit import FormView
from mysite.forms import PostSearchForm
from django.db.models import Q
from django.shortcuts import render

from django.views.generic.base import TemplateView

import urllib.request
import json
import math
import operator
import sys
print(sys.stdin.encoding)

# Create your views here.

import random
#--- TemplateView

def findrandom(request):

    random_list = IDF.objects.all()
    rnum = random.randrange(1,len(random_list.values()))
    keyword = random_list.values()[rnum]['tag']

    words = keyword.split(' ')
    trfs_dict = {}
    post_list1 = ISBN.objects.filter(tag__icontains=words[0])
    post_list2 = IDF.objects.filter(tag__icontains=words[0]).distinct()
    lists = post_list1.values()
    lists2 = post_list2.values()

    for i in range(len(lists)):
        TRFS = round(math.sqrt(post_list1.values()[i]['RFS']) * (post_list1.values()[i]['TF'] * post_list2.values()[0]['IDF']),2)
        #TRFS = round(lists[i]['RFS'] * math.sqrt(lists[i]['TF'] * lists2[0]['IDF']), 2)
        trfs_dict[lists[i]['ISBN']] = TRFS


    sorted_trfs = sorted(trfs_dict.items(), key=operator.itemgetter(1), reverse=True)

    context = {}

    if (len(sorted_trfs) < 5):
        list_len = len(sorted_trfs)
    else:
        list_len = 5

    for i in range(list_len):
        key = 'items' + str(i)
        trfs = 'trfs' + str(i)
        context[key] = naverAPI(sorted_trfs[i][0])
        context[trfs] = sorted_trfs[i][1]
        context['tag'] = '#' + words[0]

    return render(request, 'home.html', context=context)

    # RFS상위
    # rfs_list = ISBN.objects.values_list('ISBN', 'RFS').distinct()[:5]
    # print(len(rfs_list))
    # lists = rfs_list.values()
    # print(lists)
    #
    # context={}
    # for i in range(len(lists)):
    #     key = 'items' + str(i)
    #     rfs = 'rfs' + str(i)
    #     context[key] = naverAPI(lists[i]['ISBN'])
    #     context[rfs] = lists[i]['RFS']
    #
    # return render(request, 'home.html', context=context)


def naverAPI(ISBN):

    encText = str(ISBN)

    client_id = "fjQfNc78k7s6QIaF0zYB"  # 애플리케이션 등록시 발급 받은 값 입력
    client_secret = "V4SUfjYhXW"  # 애플리케이션 등록시 발급 받은 값 입력

    url = "https://openapi.naver.com/v1/search/book?query=" + encText + "&display=3&sort=count"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if (rescode == 200):
        response_body = response.read()
        result = json.loads(response_body.decode('utf-8'))
        items = result.get('items')
        title = items[0]['title']
        title_split = title.split('(')
        if (len(title_split) >= 2):
            items[0]['title'] = title_split[0]
            items[0]['subtitle'] = title_split[1][:-1]
        else:
            items[0]['subtitle'] = ''

        img = items[0]['image']
        #print(type(img))
        img = img.replace('m1', 'm5')
        #print(img)
        items[0]['image'] = img
        # pprint(result)


        # json_rt = response.read().decode('utf-8')
        # py_rt = json.loads(json_rt)

        # print(response_body.decode('utf-8'))
    else:
        print("Error Code:" + rescode)

    return items



class EconView(FormView):
    form_class = PostSearchForm
    template_name = 'econ.html'

    def form_valid(self, form):

        schWord = '%s' % self.request.POST['search_word']

        keyword_list = schWord.split('#')
        recommend_dict = {}
        for i in range(len(keyword_list) - 1):
            trfs_dict = self.merge_trfs(recommend_dict, self.make_trfs(keyword_list[i + 1]))


        sorted_trfs = sorted(trfs_dict.items(), key=operator.itemgetter(1), reverse=True)


        context = {}

        if (len(sorted_trfs) < 20):
            list_len = len(sorted_trfs)
        else:
            list_len = 20

        for i in range(list_len):
            rank = 'rank' + str(i)
            items = 'items' + str(i)
            trfs = 'trfs' + str(i)
            tag = 'tag' + str(i)
            context[items] = self.naverAPI(sorted_trfs[i][0])
            context[trfs] = sorted_trfs[i][1][0]
            context[tag] = sorted_trfs[i][1][1]
            context[rank] = i+1

        return render(self.request, self.template_name, context=context)

    def make_trfs(self, keyword):
        trfs_dict = {}
        post_list1 = ISBN.objects.filter(Q(tag__icontains=keyword) & Q(CATE__icontains='1'))
        post_list2 = IDF.objects.filter(Q(tag__icontains=keyword) & Q(CATE__icontains='1')).distinct()



        ISBN_lists = post_list1.values()
        IDF_lists = post_list2.values()

        for i in range(len(ISBN_lists)):
            TRFS = round(math.sqrt(post_list1.values()[i]['RFS']) * (post_list1.values()[i]['TF'] * post_list2.values()[0]['IDF']),2)
            #TRFS = round(ISBN_lists[i]['RFS'] * math.sqrt(ISBN_lists[i]['TF'] * IDF_lists[0]['IDF']), 2)

            value_list = [TRFS,'#'+keyword]
            trfs_dict[ISBN_lists[i]['ISBN']] = value_list

        return trfs_dict

    def merge_trfs(self, trfs1, trfs2):
        key_trfs2 = trfs2.keys()  # 추가 태그어의 ISBN을 뽑음

        for key in key_trfs2:
            if (key in trfs1):  # 새로운 리스트의 ISBN이 기존 리스트에 있으면
                trfs1[key][0] = trfs1[key][0] + trfs2[key][0]
                trfs1[key][1] = trfs1[key][1] + trfs2[key][1]
            else:  # 없으면 기존 리스트에 새롭게 추가
                trfs1[key] = trfs2[key]

        return trfs1  # 합쳐진 딕셔너리 반환

    def naverAPI(self, ISBN):

        encText = str(ISBN)

        client_id = "fjQfNc78k7s6QIaF0zYB"  # 애플리케이션 등록시 발급 받은 값 입력
        client_secret = "V4SUfjYhXW"  # 애플리케이션 등록시 발급 받은 값 입력

        url = "https://openapi.naver.com/v1/search/book?query=" + encText + "&display=3&sort=count"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            result = json.loads(response_body.decode('utf-8'))
            items = result.get('items')
            title = items[0]['title']
            title_split = title.split('(')
            if (len(title_split) >= 2):
                items[0]['title'] = title_split[0]
                items[0]['subtitle'] = title_split[1][:-1]
            else:
                items[0]['subtitle'] = ''

            img = items[0]['image']
            print(type(img))
            img = img.replace('m1', 'm5')
            print(img)
            items[0]['image'] = img
            # pprint(result)


            # json_rt = response.read().decode('utf-8')
            # py_rt = json.loads(json_rt)

            # print(response_body.decode('utf-8'))
        else:
            print("Error Code:" + rescode)

        return items

class SciView(FormView):
    form_class = PostSearchForm
    template_name = 'sci.html'

    def form_valid(self, form):

        schWord = '%s' % self.request.POST['search_word']

        keyword_list = schWord.split('#')
        recommend_dict = {}
        for i in range(len(keyword_list) - 1):
            trfs_dict = self.merge_trfs(recommend_dict, self.make_trfs(keyword_list[i + 1]))


        sorted_trfs = sorted(trfs_dict.items(), key=operator.itemgetter(1), reverse=True)


        context = {}

        if (len(sorted_trfs) < 20):
            list_len = len(sorted_trfs)
        else:
            list_len = 20

        for i in range(list_len):
            rank = 'rank' + str(i)
            items = 'items' + str(i)
            trfs = 'trfs' + str(i)
            tag = 'tag' + str(i)
            context[items] = self.naverAPI(sorted_trfs[i][0])
            context[trfs] = sorted_trfs[i][1][0]
            context[tag] = sorted_trfs[i][1][1]
            context[rank] = i+1

        return render(self.request, self.template_name, context=context)

    def make_trfs(self, keyword):
        trfs_dict = {}
        post_list1 = ISBN.objects.filter(Q(tag__icontains=keyword) & Q(CATE__icontains='2'))
        post_list2 = IDF.objects.filter(Q(tag__icontains=keyword) & Q(CATE__icontains='2')).distinct()



        ISBN_lists = post_list1.values()
        IDF_lists = post_list2.values()

        for i in range(len(ISBN_lists)):
            #TRFS = round(math.sqrt(post_list1.values()[i]['RFS']) * (post_list1.values()[i]['TF'] * post_list2.values()[0]['IDF']),1)
            TRFS = round(ISBN_lists[i]['RFS'] * math.sqrt(ISBN_lists[i]['TF'] * IDF_lists[0]['IDF']), 0)
            value_list = [TRFS,'#'+keyword]
            trfs_dict[ISBN_lists[i]['ISBN']] = value_list



        return trfs_dict

    def merge_trfs(self, trfs1, trfs2):
        key_trfs2 = trfs2.keys()  # 추가 태그어의 ISBN을 뽑음

        for key in key_trfs2:
            if (key in trfs1):  # 새로운 리스트의 ISBN이 기존 리스트에 있으면
                trfs1[key][0] = trfs1[key][0] + trfs2[key][0]
                trfs1[key][1] = trfs1[key][1] + trfs2[key][1]
            else:  # 없으면 기존 리스트에 새롭게 추가
                trfs1[key] = trfs2[key]

        return trfs1  # 합쳐진 딕셔너리 반환

    def naverAPI(self, ISBN):

        encText = str(ISBN)

        client_id = "fjQfNc78k7s6QIaF0zYB"  # 애플리케이션 등록시 발급 받은 값 입력
        client_secret = "V4SUfjYhXW"  # 애플리케이션 등록시 발급 받은 값 입력

        url = "https://openapi.naver.com/v1/search/book?query=" + encText + "&display=3&sort=count"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if (rescode == 200):
            response_body = response.read()
            result = json.loads(response_body.decode('utf-8'))
            items = result.get('items')
            title = items[0]['title']
            title_split = title.split('(')
            if (len(title_split) >= 2):
                items[0]['title'] = title_split[0]
                items[0]['subtitle'] = title_split[1][:-1]
            else:
                items[0]['subtitle'] = ''

            img = items[0]['image']
            print(type(img))
            img = img.replace('m1', 'm5')
            print(img)
            items[0]['image'] = img
            # pprint(result)


            # json_rt = response.read().decode('utf-8')
            # py_rt = json.loads(json_rt)

            # print(response_body.decode('utf-8'))
        else:
            print("Error Code:" + rescode)

        return items


class AboutView(TemplateView):
    template_name = 'about.html'
