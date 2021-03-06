import time
import pandas as pd
import math
from tabulate import tabulate
import os

from selenium import webdriver      # 웹 화면 제어용
from bs4 import BeautifulSoup       # 웹 코드 추출

driver = webdriver.Chrome('chromedriver_win32/chromedriver.exe')
driver.get('http://www.encar.com/pr/pr_index.do?WT.hit=index_gnb')
time.sleep(1.5)

#팝업창 닫기
driver.find_element_by_css_selector('#depth_main > div.layer_mdl.layer_guide.ui_guide.on > div.layer_container.ui_start > div > a.btn_mdl.btn_close_cookie.ui_close_cookie').click()

#메뉴 선택
    #DropDown open
driver.find_element_by_xpath('//*[@id="depth_main"]/div[2]/div/div[1]/div[1]/div[2]/ul/li[1]/div/a').click()

for i in range(2, 72):
    #실제 메뉴 선택
    driver.find_element_by_xpath('//*[@id="depth_main"]/div[2]/div/div[1]/div[1]/div[2]/ul/li[1]/div/div/div[1]/ul/li[%d]/a' % i).click()
    s_name = driver.find_element_by_xpath('//*[@id="depth_main"]/div[2]/div/div[1]/div[1]/div[2]/ul/li[1]/div/div/div[1]/ul/li[%d]/a/span[1]' % i).text
    time.sleep(1.5)

    #페이지 소스코드 로드
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    #csv파일에 저장해 나갈 배열 생성
    car_info = []   # 제조사 / 모델 / 등급/ 연식 / 주행거리 / 가격

    #페이지 수 구하기
        # 1.검색 된 전체 차량 수를 출력하는 태그 부분 변수로 저장.
    tag_cnt_searchResult = soup.select('#resultWrap > div.ui_tab_container > div.result_buy.ui_tab_content.on > div.buy_title > span')
    print(tag_cnt_searchResult)

        # 2. str로 변경 후, 필요한 숫자 부분만 추출하여 int로 저장.
    #tag_cnt_searchResult = str(tag_cnt_searchResult)
    tag_cnt_searchResult = str(tag_cnt_searchResult)
    cnt_searchResult = int(tag_cnt_searchResult[24:-9].replace(",",""))
    print(cnt_searchResult)

        # 3. 페이지 당 5개의 검색 결과를 보여주므로 cnt_searchResult/5 = '전체 페이지 수'
    pageNum = math.trunc(cnt_searchResult/5)
    print(pageNum)
    pageNum += 2

    for j in range(1, pageNum):
        if j > 10 and (j%10)-1 == 0:
            driver.find_element_by_xpath('//*[@id="resultWrap"]/div[2]/div[1]/div[2]/span[3]/a').click()
            time.sleep(1.5)
        elif j == 1:
            #driver.find_element_by_link_text(str(i)).click()
            time.sleep(1.5)
        else:
            driver.find_element_by_link_text(str(j)).click()
            time.sleep(1.5)

        company = soup.select(
            '#resultWrap > div.ui_tab_container > div.result_buy.ui_tab_content.on > table > tbody > tr > td > a > span.inf > span.cls > strong'
            )
        model = soup.select(
            '#resultWrap > div.ui_tab_container > div.result_buy.ui_tab_content.on > table > tbody > tr > td > a > span.inf > span.cls > em'
        )
        rating = soup.select(
            '#resultWrap > div.ui_tab_container > div.result_buy.ui_tab_content.on > table > tbody > tr > td > a > span.inf > span.dtl > strong'
        )
        year = soup.select(
            '#resultWrap > div.ui_tab_container > div.result_buy.ui_tab_content.on > table > tbody > tr > td > a > span.detail > span.yer'
        )
        mileage = soup.select(
            '#resultWrap > div.ui_tab_container > div.result_buy.ui_tab_content.on > table > tbody > tr > td > a > span.detail > span.km'
        )
        price = soup.select(
            '#resultWrap > div.ui_tab_container > div.result_buy.ui_tab_content.on > table > tbody > tr > td > a > span.val > span > strong'
            )

        for item in zip(company, model, rating, year, mileage, price):
            car_info.append(
                {'company' : item[0].text,
                'model' : item[1].text,
                'rating' : item[2].text,
                'year' : item[3].text,
                'mileage' : item[4].text,
                'price' : item[5].text + "(만원)"
                }
            )

        print(j)

    data = pd.DataFrame(car_info)
    print(tabulate(data, headers='keys', tablefmt='psql', showindex=False))

    try:
        if not os.path.exists('output_car_info.csv'):
            data.to_csv('output_car_info.csv', index = False,  encoding = 'utf-8-sig', sheet_name = s_name, mode = 'w')   #   utf-8-sig OR cp949
            print("csv 생성 완료.")
        else:
            data.to_csv('output_car_info.csv', index = False,  encoding = 'utf-8-sig', sheet_name = s_name, mode = 'a')   #   utf-8-sig OR cp949
            print("csv 생성 완료.")
    except Exception as e:
        print(e)

