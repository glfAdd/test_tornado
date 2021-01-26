FROM python:3.7.6

MAINTAINER glfAdd

WORKDIR /source/test_tornado
ADD . /source
RUN pip install - r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
CMD pyhton base.py
