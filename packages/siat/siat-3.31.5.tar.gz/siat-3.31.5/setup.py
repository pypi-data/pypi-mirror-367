# -*- coding: utf-8 -*-
"""
@author: WANG Dehong (Peter), IBS BFSU
"""

from setuptools import setup, find_packages

# __file__变量是在模块作为脚本直接运行时才会被定义的特殊变量。
# 当你在交互式环境中运行代码时，__file__变量是未定义的。
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
# description does not support image, markdown text only


dependence_list=[
    'pandas_datareader',
    'yfinance',#暂时不可用
    'tqdm',
    'plotly_express',
    'akshare',
    'urllib3',
    'mplfinance',
    'statsmodels',
    'yahoo_earnings_calendar',
    'pypinyin',
    'seaborn',
    'scipy',
    'pandas',
    'scikit-learn',
    'baostock',
    'pyproject.toml',
    #'ta-lib',#ta-lib需要单独安装，并与Python版本配套
    'pathlib','ruamel-yaml','prettytable',
    'graphviz',#graphviz还需要额外安装程序
    'luddite',
    'pendulum','itables','py_trans','bottleneck',
    'translate','translators',
    #注意：translators 5.9.5要求lxml >=5.3.0，与yahooquery的要求矛盾
    'nbconvert',
    #'ipywidgets==8.1.6',#解决Error loading widgets
    'ipywidgets',
    #'ipywidgets',
    #'yahooquery==2.3.7',#解决数据获取失败crump限制
    'yahooquery',#解决数据获取失败crump限制
    #注意：临时措施，yahooquery 2.3.7要求lxml 4.9.4
    #'lxml==4.9.2',#避免兼容性问题
    'alpha_vantage',# max 25 requests per day
    'tiingo[pandas]',# max 1000 requests per day
    'numpy < 2',#保持兼容性
    'playwright',#需要python版本3.7及以上
    'pymupdf','pypandoc','python-docx','weasyprint',
    'pandas_market_calendars','pypdf','pdf2docx',
    ]


setup(
    name="siat",
    version="3.31.5",
    #author="Prof. WANG Dehong, Business School, BFSU (北京外国语大学 国际商学院 王德宏)",
    author="Prof. WANG Dehong, International Business School, Beijing Foreign Studies University",
    author_email="wdehong2000@163.com",
    description="Securities Investment Analysis Tools (siat)",
    url = "https://pypi.org/project/siat/",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="Copyright (C) WANG Dehong, 2025. For educational purpose only!",
    packages = find_packages(),
    install_requires=dependence_list,            
    #zip_sage=False,
    include_package_data=True, # 打包包含静态文件标识
    ) 