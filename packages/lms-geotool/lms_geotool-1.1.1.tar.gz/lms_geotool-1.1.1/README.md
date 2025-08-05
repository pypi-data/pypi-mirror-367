# 一、安装

```shell
pip install lms_geotool
pip install django_object_actions
```

# 二、配置

```python
# settings.py
INSTALLED_APPS = [
    # 其他
    "django_object_actions",
    "lms_geotool",
]
```

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path("geotool/", include("lms_geotool.urls")),
]
```

# 三、页面

注意前缀斜杠

- /geotool/convert/
- geotool/affinematrix/
- /geotool/dimsum/
- /geotool/translation/
- geotool/linearregression/
