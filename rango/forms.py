from django import forms
from rango.models import Page, Category, UserProfile, User

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    # 嵌套的类，为表单提供格外信息
    class Meta:
        # 把这个ModelForm与一个模型连接起来
        model = Category
        fields = ('name',)

class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    class Meta:
        # 把这个ModelForm与一个模型连接起来
        model = Page
        # 想在表单中放那些字段？
        # 有时不需要全部字段
        # 有些字段接受空值，因此可能无显示
        # 这里我们想隐藏外键字段
        # 为此，可以排除category字段
        exclude = ("category",)
        # 也可以直接指定想显示的字段(不含category字段)
        # fields = ('title', 'url', 'views')
    # 清理表单数据
    def clean(self):
        cleaed_data = self.cleaned_data
        url = cleaed_data.get('url')
        # 如果url字段不为空，而且以"http://"开头
        # 在前面加上"http：//"
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaed_data['url'] = url
        return cleaed_data

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')