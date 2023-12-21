# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import jieba
import seaborn as sns
from streamlit_echarts import st_echarts
from streamlit.logger import get_logger
import urllib.request
from urllib.parse import urlparse
from typing import Dict, List, Tuple
from pyecharts.commons.utils import JsCode

LOGGER = get_logger(__name__)

st.write("# Welcome to Streamlit! ")
def get_web_content(url: str) -> Tuple[Dict[str, int], List[str], List[int]]:
    """
    获取网页中的内容，进行分词并统计词频。

    返回：
    - counts：单词计数字典。
    - top_words：Top 20 单词列表。
    - top_counts：Top 20 单词数量列表。
    """
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.get_text()
    pattern = re.compile(r'[^a-zA-Z0-9\u4e00-\u9fa5]')
    new_content = re.sub(pattern, '', content)
    words = jieba.lcut(new_content)
    counts = {}
    for word in words:
        if len(word) == 1:
            continue
        else:
            counts[word] = counts.get(word, 0) + 1
    items = list(counts.items())
    items.sort(key=lambda x: x[1], reverse=True)
    top_words = [items[i][0] for i in range(min(20, len(items)))]
    top_counts = [items[i][1] for i in range(min(20, len(items)))]
    return counts, top_words, top_counts


def get_top_counts(counts: Dict[str, int], num: int = 20) -> Dict[str, int]:
    """
    获取单词计数字典中 Top N 单词及其数量。

    参数：
    - counts：单词计数字典。
    - num：Top N 单词数量，默认为 20。

    返回：
    - top_counts：Top N 单词及其数量字典。
    """
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top_counts = dict(sorted_counts[:num])
    return top_counts


def display_bar_chart(words: List[str], counts: List[int]) -> None:
    """
    显示柱状图，展示 Top 20 单词及其数量。

    参数：
    - words：Top 20 单词列表。
    - counts：Top 20 单词数量列表。
    """
    options = {
        "xAxis": {
            "type": "category",
            "data": words,
            "axisLabel": {
                "rotate": 45
            }
        },
        "yAxis": {"type": "value"},
        "series": [{"data": counts, "type": "bar"}],
    }
    st_echarts(options=options, height="500px")


def display_word_cloud(top_counts: Dict[str, int]) -> None:
    """
    显示词云，展示 Top 20 单词及其数量。

    参数：
    - top_counts：Top 20 单词及其数量字典。
    """
    data = [{"name": word, "value": count} for word, count in top_counts.items()]
    wordcloud_option = {"series": [{"type": "wordCloud", "data": data}]}
    st_echarts(wordcloud_option)


def display_pie_chart(top_counts: Dict[str, int]) -> None:
    """
    显示饼图，展示 Top 20 单词及其数量。

    参数：
    - top_counts：Top 20 单词及其数量字典。
    """
    data = [{"name": word, "value": count} for word, count in top_counts.items()]
    options = {
        "title": {"text": "", "subtext": "", "left": "center"},
        "tooltip": {"trigger": "item"},
        "legend": {
            "orient": "vertical",
            "left": "left",
        },
        "series": [
            {
                "name": "访问来源",
                "type": "pie",
                "radius": "50%",
                "data": data,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    }
                },
            }
        ],
    }
    events = {
        "legendselectchanged": "function(params) { return params.selected }",
    }
    st_echarts(options=options, events=events, height="600px", key="render_pie_events")


def display_images(soup: BeautifulSoup) -> None:
    """
    下载并显示页面中的所有图片。

    参数：
    - soup：BeautifulSoup 对象。
    """
    images = soup.find_all('img')
    if len(images) > 0:
        st.write("页面中的图片：")
        for img in images:
            img_url = img['src']
            try:
                with urllib.request.urlopen(img_url) as url:
                    image = url.read()
                st.image(image, caption=img_url, use_column_width=True)
            except Exception as e:
                st.warning(f"无法下载或显示图片: {img_url}, 错误信息：{e}")
    else:
        st.write("页面中没有图片。")


def display_web_content(url: str) -> None:
    """
    获取网页中的内容，进行分词并统计词频，并展示柱状图、词云、饼图和图片等信息。

    参数：
    - url：网页地址。
    """
    try:
        counts, top_words, top_counts = get_web_content(url)
        top_20_counts = get_top_counts(counts, num=20)
        display_bar_chart(top_words, top_counts)
        display_word_cloud(top_20_counts)
        display_pie_chart(top_20_counts)
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        display_images(soup)
    except Exception as e:
        st.write(f"发生错误：{e}")


def display_line_chart(words: List[str], counts: List[int]) -> None:
    """
    显示折线图，展示 Top 20 单词及其数量。

    参数：
    - words：Top 20 单词列表。
    - counts：Top 20 单词数量列表。
    """
    option = {
        "xAxis": {
            "type": "category",
            "data": words,
            "axisLabel": {
                "rotate": 45
            }
        },
        "yAxis": {"type": "value"},
        "series": [{"data": counts, "type": "line"}],
    }
    st_echarts(
        options=option, height="400px",
    )

def display_scatter_chart(top_counts: Dict[str, int],words: List[str], counts: List[int]) -> None:
    """
    显示散点图，展示 Top 20 单词及其数量。

    参数：
    - top_counts：Top 20 单词及其数量字典。
    - words：Top 20 单词列表。
    - counts：Top 20 单词数量列表。
    """
    data = [{"name": word, "value": count} for word, count in top_counts.items()]
    options = {
        "xAxis": {
            "type": "category",
            "data": words,
            "axisLabel": {
                "rotate": 45
            }
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "symbolSize": 20,
                "data": data,
                "type": "scatter",
            }
        ],
    }
    st_echarts(options=options, height="500px")

def display_customized_chart(top_counts: Dict[str, int], words: List[str], counts: List[int]) -> None:
    """
    显示漏斗图

    参数：
    - top_counts：Top 20 单词及其数量字典。
    - words：Top 20 单词列表。
    - counts：Top 20 单词数量列表。
    """
    total_count = sum(counts)
    data = [{"name": word, "value": round(count / total_count * 100, 2)} for word, count in top_counts.items()]
    option = {
        "title": {"text": "", "subtext": ""},
        "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b} : {c}%"},
        "toolbox": {
            "feature": {
                
            }
        },
        "legend": {"data": words},
        "series": [
            {
                "name": "词语比例",
                "type": "funnel",
                "left": "10%",
                "width": "80%",
                "label": {"formatter": "{b}"},
                "labelLine": {"show": False},
                "itemStyle": {"opacity": 0.7},
                "emphasis": {
                    "label": {"position": "inside", "formatter": "{b} : {c}%"}
                },
                "data": data,
            }
        ],
    }
    st_echarts(option, height="500px")

def display_area_chart(words: List[str], counts: List[int]) -> None:
    """
    显示面积图，展示 Top 20 单词及其数量。

    参数：
    - words：Top 20 单词列表。
    - counts：Top 20 单词数量列表。
    """
    options = {
        "xAxis": {
            "type": "category",
            "boundaryGap": False,
            "data": words,
                "axisLabel": {
                    "rotate": 45
                }
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "data": counts,
                "type": "line",
                "areaStyle": {},
            }
        ],
    }
    st_echarts(options=options)

def display_sidebar_options():
    selected_option = st.sidebar.selectbox("选择一个功能", ["显示柱状图", "显示词云", "显示饼图","显示折线图","显示散点图","显示漏斗图","显示面积图", "显示图片"])
    return selected_option

def run() -> None:
    """
    Streamlit 应用主函数。
    """
    st.title("获取页面内容并显示")
    url = st.text_input("请输入网址")

    # 添加侧边栏
    selected_option = display_sidebar_options()

    if st.button("获取内容"):
        if url:
            counts, top_words, top_counts = get_web_content(url)
            top_20_counts = get_top_counts(counts, num=20)
            if selected_option:
                if selected_option == "显示柱状图":
                    display_bar_chart(top_words, top_counts)
                elif selected_option == "显示词云":
                    display_word_cloud(top_20_counts)
                elif selected_option == "显示饼图":
                    display_pie_chart(top_20_counts)
                elif selected_option == "显示折线图":
                    display_line_chart(top_words, top_counts)
                elif selected_option == "显示散点图":
                    display_scatter_chart(top_20_counts,top_words, top_counts) 
                elif selected_option == "显示漏斗图":
                    display_customized_chart(top_20_counts,top_words, top_counts)    
                elif selected_option == "显示面积图":
                    display_area_chart(top_words, top_counts)                  
                elif selected_option == "显示图片":
                    try:
                        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
                        display_images(soup)
                    except Exception as e:
                        st.write(f"发生错误：{e}")
            else:
                st.write("请选择一个功能")
        # st.write(top_20_counts)


if __name__ == "__main__":
    run()

