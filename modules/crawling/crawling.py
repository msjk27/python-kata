import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm.notebook import tqdm
from datetime import datetime, timedelta

# artdic = crawling("2023-10-13", "2023-10-18", [POLITICAL_SEED2])
# to_csv(artdic, path)


POLITICS_CATEGORY_SEED = 100

POLITICAL_SEED1 = "대통령실"
POLITICAL_SEED2 = "북한"
POLITICAL_SEED3 = "국방/외교"
__POLITICAL_CATEGORIES = {
      POLITICAL_SEED2: 268,
      POLITICAL_SEED3: 267
  }


def __date_producer(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    date_list = []
    delta = timedelta(days=1)
    while start_date <= end_date:
        date_list.append(start_date.strftime("%Y%m%d"))
        start_date += delta
    return date_list


def __ex_tag(sid1, sid2, page, date):
    url = f"https://news.naver.com/main/list.naver?mode=LS2D&sid2={sid2}&mid=shm&sid1={sid1}&date={date}&page={page}"
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"\
    "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "\
    "Chrome/110.0.0.0 Safari/537.36"})
    soup = BeautifulSoup(html.text, "lxml")
    a_tag = soup.find_all("a")
    tag_lst = []
    for a in a_tag:
        if "href" in a.attrs:
            if (f"sid=100" in a["href"]) and ("article" in a["href"]):
                tag_lst.append(a["href"])
    return tag_lst


def __re_tag(sid1, sid2, pages, date_list):
    re_lst = []
    for date in date_list:
        for i in range(pages):
            lst = __ex_tag(sid1, sid2, i+1, date)
            re_lst.extend(lst)
    return list(set(re_lst))


def __make_hrefs(sids, pages, date_list):
    hrefs = {}
    for sid2 in sids:
        hrefs[sid2] = __re_tag(POLITICS_CATEGORY_SEED, sid2, pages, date_list)
    return hrefs


def __art_crawl(hrefs, sid, index):
    art_dic = {}
    title_selector = "#title_area > span"
    date_selector = "#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans"\
    "> div.media_end_head_info_datestamp > div:nth-child(1) > span"
    main_selector = "#dic_area"
    author_selector = ".media_end_head_journalist_name"
    url = hrefs[sid][index]
    html = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 "\
    "(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"\
    "Chrome/110.0.0.0 Safari/537.36"})
    media_company_selector = ".media_end_head_top_logo > img"
    soup = BeautifulSoup(html.text, "lxml")
    title = soup.select(title_selector)
    title_lst = [t.text for t in title]
    title_str = "".join(title_lst)

    date = soup.select(date_selector)
    date_lst = [d.text for d in date]
    date_str = "".join(date_lst)

    author = soup.select(author_selector)
    author_lst = [a.text for a in author]
    author_str = "".join(author_lst)

    media_company = soup.select(media_company_selector)[0].get('title')
    
    main = soup.select(main_selector)
    main_lst = []
    for m in main:
        m_text = m.text
        m_text = m_text.strip()
        main_lst.append(m_text)
    main_str = "".join(main_lst)
    art_dic["title"] = title_str
    art_dic["date"] = date_str
    art_dic["main"] = main_str
    art_dic["author"] = author_str
    art_dic["media_company"] = media_company
    return art_dic


def __solution(sids, pages, date_list):
    hrefs = __make_hrefs(sids, pages, date_list)
    artdic_lst = []
    for section in sids:
        for i in range(len(hrefs[section])):
            art_dic = __art_crawl(hrefs, section, i)
            art_dic["section"] = section
            art_dic["url"] = hrefs[section][i]
            artdic_lst.append(art_dic)
    return artdic_lst


def to_csv(artdic: list, path="ar.csv"):
    art_df = pd.DataFrame(artdic)
    art_df.to_csv(path)

    
def crawling(start_date: str, end_date:str , categories=list(__POLITICAL_CATEGORIES.keys())) -> list:
    categories_seeds = list(map(lambda x: __POLITICAL_CATEGORIES[x], 
        filter(lambda x: x in __POLITICAL_CATEGORIES.keys(), list(set(categories)))))
    date_list = __date_producer(start_date, end_date)
    return __solution(categories_seeds, 1, date_list)
