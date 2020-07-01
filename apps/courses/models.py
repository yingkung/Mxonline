from django.db import models
from apps.users.models import BaseModel
from apps.organizations.models import Teacher, CourseOrg


# 1. 确定实体有： 课程，章节，视频，课程资源
# 2. 确定实体的具体字段：
# 3. 每个字段的类型，是否必填

# 课程的机构和老师都是实体，不能放入下面的字段中，需要和另外的表格关联 #


class Course(BaseModel):
    # 课程
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='讲师')
    course_org = models.ForeignKey(CourseOrg, null=True, blank=True, on_delete=models.CASCADE, verbose_name='课程机构')
    name = models.CharField(max_length=50, verbose_name='课程名')
    desc = models.CharField(max_length=300, verbose_name='课程描述')
    degree = models.CharField(verbose_name='难度', choices=(('cj', '初级'), ('zj', '中级'), ('gj', '高级')), max_length=2)
    learn_times = models.IntegerField(default=0, verbose_name='学习时长（分钟数）')
    students = models.IntegerField(default=0, verbose_name='学习人数')
    fav_nums = models.IntegerField(default=0, verbose_name='收藏人数')
    click_nums = models.IntegerField(default=0, verbose_name='点击数')
    category = models.CharField(default=u'后端开发', max_length=20, verbose_name='课程类别')
    tag = models.CharField(default='', verbose_name='课程标签', max_length=10)   # 为了推荐相似内容的课程而设置，比如都是django的课程
    youneed_know = models.CharField(default='', max_length=300, verbose_name='课程须知')
    teacher_tell = models.CharField(default='', max_length=300, verbose_name='老师告诉你')

    detail = models.TextField(verbose_name='课程详情')
    img = models.ImageField(verbose_name='封面图', upload_to='courses/%Y/%m', max_length=100)
    is_classics = models.BooleanField(verbose_name='是否经典', default=False)
    class Meta:
        verbose_name = '课程信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Lesson(BaseModel): # 章节信息
    # 设置外键，关联课程和章节两个实体
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  #on_delete表示对应的外键数据被删除后，当前的数据应该怎么办
    # CASCADE表示，如果对应外键课程信息被删除，则此课程下的章节信息也一并被删除
    # course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank = True) #
    # 有时是不删除的，直接设置为空，但要求这个列的参数本身有null, blank
    name = models.CharField(verbose_name=u'章节名', max_length=100)
    learn_times = models.IntegerField(default=0, verbose_name='学习时长（分钟数）')

    class Meta:
        verbose_name = '课程章节'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Video(BaseModel):
    lesson = models.ForeignKey(Lesson, verbose_name='章节' , on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='视频名')
    learn_times = models.IntegerField(default=0, verbose_name='学习时长（分钟数）')
    url = models.CharField(max_length=200, verbose_name='访问地址')

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseResource(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')
    name = models.CharField(max_length=100, verbose_name='名称')
    file = models.FileField(upload_to='course/resource/%Y/%m', verbose_name='下载地址', max_length=200)

    class Meta:
        verbose_name = '课程资源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name