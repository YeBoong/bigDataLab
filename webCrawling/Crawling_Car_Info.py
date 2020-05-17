import time
import pandas as pd
import math
from tabulate import tabulate
import os

from selenium import webdriver      # 웹 화면 제어용
from bs4 import BeautifulSoup       # 웹 코드 추출

pageControl = 2

driver = webdriver.Chrome('webCrawling\chromedriver_win32\chromedriver.exe')
driver.get('http://www.encar.com/pr/pr_index.do?WT.hit=index_gnb')
time.sleep(0.5)

#팝업창 닫기1
driver.find_element_by_css_selector('#depth_main > div.layer_mdl.layer_guide.ui_guide.on > div.layer_container.ui_start > div > a.btn_mdl.btn_close_cookie.ui_close_cookie').click()

for i in range(2, 72):
    #메뉴 선택
        #DropDown open
    driver.find_element_by_xpath('//*[@id="depth_main"]/div[2]/div/div[1]/div[1]/div[2]/ul/li[1]/div/a').click()
        #실제 메뉴 선택
    element = driver.find_element_by_xpath('//*[@id="depth_main"]/div[2]/div/div[1]/div[1]/div[2]/ul/li[1]/div/div/div[1]/ul/li[%d]/a' % i)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(0.5)

    #제조회사 이름
    cName = str(driver.find_element_by_xpath('//*[@id="depth_main"]/div[2]/div/div[1]/div[1]/div[2]/ul/li[1]/div/a/span[1]').text)
    print(cName)
    time.sleep(0.5)

    #페이지 소스코드 로드
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # #csv파일에 저장해 나갈 배열 생성
    car_info = []   # 제조사 / 모델 / 등급/ 연식 / 주행거리 / 가격

    #페이지 수 구하기
        # 1.검색 된 전체 차량 수를 출력하는 태그 부분 변수로 저장.
    searchResult = str(driver.find_element_by_xpath('//*[@id="resultWrap"]/div[2]/div[1]/div[1]/span').text)
    print(searchResult)

        # 2. str로 변경 후, 필요한 숫자 부분만 추출하여 int로 저장.
    if searchResult == "검색결과 없음":
        print("매물이 없습니다. 건너띕니다.")
        continue
    else:
        cnt_searchResult = int(searchResult[5:-1].replace(",",""))
        print(cnt_searchResult)

        # 3. 페이지 당 5개의 검색 결과를 보여주므로 cnt_searchResult/5 = '전체 페이지 수'
        if cnt_searchResult < 6:
            pageNum = 1
        else:
            if (cnt_searchResult%5) == 0:
                pageNum = int(cnt_searchResult/5)
            else:
                pageNum = math.trunc(cnt_searchResult/5) + 1
        print(pageNum)
        pageNum += 1

        try:
            for j in range(1, pageNum):
                if j > 10 and (j%10)-1 == 0:
                    # driver.find_element_by_xpath('//*[@id="resultWrap"]/div[2]/div[1]/div[2]/span[3]/a').click()
                    element = driver.find_element_by_xpath('//*[@id="resultWrap"]/div[2]/div[1]/div[2]/span[3]/a')
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(0.8)
                elif j == 1:
                    #driver.find_element_by_link_text(str(i)).click()
                    time.sleep(0.8)
                else:
                    element = driver.find_element_by_xpath('//*[@id="resultWrap"]/div[2]/div[1]/div[2]/span[2]/a[%d]' % pageControl)
                    driver.execute_script("arguments[0].click();", element)
                    pageControl += 1
                    if pageControl > 10:
                        pageControl = 2
                    time.sleep(0.8)

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

                print("%d page 완료" % j)
        
        except:
            print("%s 의 페이지 수에 변동이 생겼습니다. 현재 마지막 페이지입니다." % cName)
            print("다음 회사로 넘어갑니다.")
            break

        data = pd.DataFrame(car_info)
        print(tabulate(data, headers='keys', tablefmt='psql', showindex=False))
        print("%s 완료" % cName)

        if not os.path.exists('output_car_info.xlsx'):
            with pd.ExcelWriter('output_car_info.xlsx', mode='w', engine='openpyxl', ) as writer:
                data.to_excel(writer, index=False, encoding = 'utf-8-sig', sheet_name = cName)
        else:
            with pd.ExcelWriter('output_car_info.xlsx', mode='a', engine='openpyxl') as writer:
                data.to_excel(writer, index=False, encoding = 'utf-8-sig', sheet_name = cName)
        # try:
        #     if not os.path.exists('output_car_info.csv'):
        #         data.to_excel('output_car_info.xlsx', index = False,  encoding = 'utf-8-sig', sheet_name = cName, mode = 'w')   #   utf-8-sig OR cp949
        #         print("csv 생성 완료.")
        #     else:
        #         data.to_excel('output_car_info.xlsx', index = False,  encoding = 'utf-8-sig', sheet_name = cName, mode = 'a')   #   utf-8-sig OR cp949
        #         print("csv 생성 완료.")
        # except Exception as e:
        #     print(e)

