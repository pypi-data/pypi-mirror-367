# django-gbase8s

#### 介绍
GBase 8s数据库的Django方言，支持GBase 8s V8.8_3.6.2版本及以上。

#### 依赖
- gbase8sdb
- django>=4.0.0


#### 安装教程

```python
pip install django-gbase8s
```

#### 使用说明

1.  方言使用python-gbase8sdb驱动连接数据库，安装django-gbase8s时会作为依赖进行安装，您也可以手动安装：
```python
pip install gbase8sdb
```
2.  python-gbase8sdb驱动连接数据库依赖GSDK 1.1版本，所以您需要联系GBase 8s技术支持或通过官方渠道获取相应版本的GSDK，并安装到您的机器上， 并设置如下环境变量：
```bash
GSDK_PATH=/path/to/gsdk
export LD_LIBRARY_PATH=${GSDK_PATH}/lib:$LD_LIBRARY_PATH
export GBASEDBTDIR=${GSDK_PATH}/lib
```


3. 在Django项目的`settings.py`文件中进行如下配置：
```python
DATABASES = {
    "default": {
        "ENGINE": "django_gbase8s",
        'SERVER_NAME': 'ol_gbasedbt1210_1',     # 实例的名称
        'NAME': 'testdb',                     # 数据库的名称
        'HOST': '192.168.xxx.xxx',              # 数据库IP
        'PORT': 9088,                          # 实例端口号
        'DB_LOCALE': 'zh_CN.utf8',              # 数据库字符集
        'USER': 'gbasedbt',                     # 用户名
        'PASSWORD': 'xxxxxxx'                   # 密码
    }
}
```

