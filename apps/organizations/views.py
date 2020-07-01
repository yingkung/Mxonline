from django.shortcuts import render
from django.views.generic.base import View
from apps.organizations.models import City, CourseOrg, Teacher
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from apps.organizations.forms import AddAskForm
from django.http import HttpResponseRedirect, JsonResponse


class AddAskView(View):
    """

    """
    def post(self, request, *args, **kwargs):
        userask_form = AddAskForm(request.POST)
        if userask_form.is_valid():
            userask_form.save(commit=True)  # 保存到数据库中
            return JsonResponse({
                "status": "success"
            })
        else:
            return JsonResponse({
                "status": "fail",
                "msg": '添加出错'
            })



class OrgView(View):
    def get(self, request, *args, **kwargs):
        # 从数据库中获取数据，并显示在前端页面上
        all_orgs = CourseOrg.objects.all()
        all_citys = City.objects.all()

        # 授课机构排名
        hot_orgs = all_orgs.order_by('-course_nums')[:3]  # 加减号表示倒序排列



        # 通过机构类别对课程机构进行筛选
        category = request.GET.get('ct', '')
        if category:  # 如果获得了课程机构，category非空, 对机构进行筛选
            all_orgs = all_orgs.filter(category=category)

        # 通过所在城市对课程机构进行筛选
        city_id = request.GET.get('city', '')
        if city_id:
            if city_id.isdigit():
                all_orgs = all_orgs.filter(city_id=int(city_id))

        # 对机构进行排序
        sort = request.GET.get('sort', '')
        if sort == 'student':
            all_orgs = all_orgs.order_by('-student')
        elif sort == 'courses':
            all_orgs = all_orgs.order_by('-course_nums')

        org_nums = all_orgs.count()  # 获取机构个数

        # 对课程机构数据进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # Provide Paginator with the request object for complete querystring generation
        p = Paginator(all_orgs, per_page=10, request=request)
        orgs = p.page(page)

        return render(request, 'org-list.html', {
            'all_orgs': orgs,
            'org_nums': org_nums,
            'all_citys': all_citys,
            'category': category,
            'city_id': city_id,
            'sort': sort,
            'hot_orgs': hot_orgs,
        })
