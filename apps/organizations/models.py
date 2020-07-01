from django.db import models
from apps.users.models import BaseModel
# 有两个实体， 课程机构 和 课程讲师
# 城市这个class是为了方便后续添加所以单独设置的类


class City(BaseModel):   # 单独创建一个城市类，因为城市可能会增加，方便后台进行添加
    name = models.CharField(max_length=20, verbose_name='城市名')
    desc = models.TextField(max_length=200, verbose_name='描述')

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseOrg(BaseModel):
    name = models.CharField(max_length=100, verbose_name='机构名称')
    desc = models.TextField(max_length=200, verbose_name='描述')  # 后面会用富文本代替
    tag = models.CharField(verbose_name='机构标签', default='全国知名', max_length=10 )
    category = models.CharField(default='pxjg', verbose_name='培训机构', max_length=4,
                                choices=(('pxjg', '培训机构'), ('gr', '个人'), ('gx', '高校')))
    click_num = models.IntegerField(default=0, verbose_name='点击数')
    fav_num = models.IntegerField(default=0, verbose_name='收藏数')
    image = models.ImageField(verbose_name='logo', max_length=100, upload_to='org/%Y%m')
    address = models.CharField(verbose_name='机构地址', max_length=150)
    student = models.IntegerField(default=0, verbose_name='学习人数')  # 用于排序
    course_nums = models.IntegerField(default=0, verbose_name='课程数')  # 用于排序
    city = models.ForeignKey(City, verbose_name='所在城市', on_delete=models.CASCADE)

    is_auth = models.BooleanField(default=False, verbose_name='是否认证')
    is_gold = models.BooleanField(default=False, verbose_name='是否金牌')

    # 取得每个课程机构对应的课程， 已经在课程modules中添加外键课程机构
    def courses(self):
        # 添加外键的第一种方式
        # from apps.courses.models import Course
        # courses = Course.objects.filter(course_org=self)

        # 添加外键的第二种方式，不用import，[:3]表示只取3个经典课程
        courses = self.course_set.filter(is_classics=True)[:3]

        return courses

    class Meta:
        verbose_name = '课程机构'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Teacher(BaseModel):
    org = models.ForeignKey(CourseOrg, on_delete= models.CASCADE, verbose_name='教师所属机构')
    name = models.CharField(max_length=50, verbose_name='教师名')
    work_years = models.IntegerField(default=0, verbose_name='工作年限')
    work_position = models.CharField(max_length=50, verbose_name='公司职位')
    work_company = models.CharField(max_length=50, verbose_name='就职公司')
    points = models.CharField(max_length=200, verbose_name='教学特点')
    age = models.IntegerField(default=18, verbose_name='年龄')
    click_num = models.IntegerField(default=0, verbose_name='点击数')  # 对应讲师的人气
    fav_num = models.IntegerField(default=0, verbose_name='收藏数')
    image = models.ImageField(default='', upload_to='teacher/%Y/%m', verbose_name='头像', max_length=100)

    class Meta:
        verbose_name = '教师'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name