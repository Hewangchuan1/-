# -图片云加密系统
使用Apache+Flask+mod_wsgi搭建的图片云加密系统，创新性地使用正交拉丁方矩阵对图像进行加密，主要的功能有：图片上传加密、图片下载解密，还有基础的社交功能：发布帖子，评论帖子等。
### 运行环境
Windows 7 64位  
Python 3.6.4  
Flask  
MySQL  
### 配置Apache+Flask+mod_wsgi的步骤
#### 1、下载Apache
1）进入Apache官网http://httpd.apache.org/download.cgi
如下图所示，点击“Files for Microsoft Windows”
![image](https://github.com/Hewangchuan1/-/blob/master/static/说明图片/Apache官网主页_2.png)  
2）点击ApacheHaus进入版本选择页面https://www.apachehaus.com/cgi-bin/download.plx  
![image](https://github.com/Hewangchuan1/-/blob/master/static/说明图片/Apache_windows下载页面_2.png)  
3)选择版本，根据机子的不同，选择不同的版本，我选择的是Apache 2.4.39 X64，https://www.apachehaus.com/cgi-bin/download.plx  
![image](https://github.com/Hewangchuan1/-/blob/master/static/说明图片/版本选择_2.png)  
4)将文件解压到目录C:\下，得到Apache24文件夹
#### 2、下载mod_wsgi
1)打开网址http://www.lfd.uci.edu/~gohlke/pythonlibs/#pil  
选择对应版本的mod_wsgi下载，如图所示，根据个人的环境不同，选择不同的版本  
![image](https://github.com/Hewangchuan1/-/blob/master/static/说明图片/mod_wsgi下载页面.png)
2）去到下载好的mod_wsgi文件目录里，使用python的pip安装命令  
```
pip install mod_wsgi‑4.5.24+ap24vc14‑cp36‑cp36m‑win_amd64.whl
```
3)安装好之后，找到mod_wsgi文件夹, 运行下面的命令  
```
mod_wsgi-express module-config
```
4）命令成功运行后，可以得到如下图所示的三条信息  
![image](https://github.com/Hewangchuan1/-/blob/master/static/说明图片/三条信息.png)  
5）打开Apache24\conf\httpd.conf文件，将这三条信息加入到apache的配置文件中，同时，需要把LoadModule vhost_alias_module modules/mod_vhost_alias.so前面的#去掉 
![image](https://github.com/Hewangchuan1/-/blob/master/static/说明图片/增加三条信息.png)   
6）在Apache24\conf\httpd.conf文件中，更改<Directory />的内容  
![image](https://github.com/Hewangchuan1/-/blob/master/static/说明图片/更改Directory内容.png)  
7）在项目文件夹下新增wsgi文件，我新增的文件名是test.wsgi，在其中写下如下内容：  
```
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,'C:/yunjiami/')
from zlktqa import app as application
```  
注明：C:/yunjiami/为项目文件夹  
8）配置站点（重要）  
![image](https://github.com/Hewangchuan1/-/blob/master/static/说明图片/配置站点.png)    
注明：4241为端口号，C:/yunjiami/test.wsgi为wsgi文件路径  
#### 更改Flask文件内容
1）在项目的主文件中，我的主项目文件为zlktqa.py，删除或注释以下内容：  
```
# if __name__ == '__main__':
#     app.run(port=4241, debug=True)
```
### 项目运行
1）新建数据库  
```
create database zlktqa_demo;
```  
2)在项目文件夹下初始化数据库（建立表单），即执行以下代码  
```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```  
3)找到Apache24\bin目录下的ApacheMonitor.exe可执行文件并执行，如下图所示：  
![image](https://github.com/Hewangchuan1/-/blob/master/static/说明图片/可执行文件.png)   
点击start,开始运行  
4）找到自己机子的ip地址，打开浏览器，在地址框输入“ip地址:4241\”，即可查看网页是否可以运行  
注明：4241为端口号  


