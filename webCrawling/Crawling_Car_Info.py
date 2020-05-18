import time
import pandas as pd
import math
from tabulate import tabulate
import os

from selenium import webdriver      # 웹 화면 제어용
from bs4 import BeautifulSoup       # 웹 코드 추출

pageControl = 2                     # 페이지 버튼 누를 때, 제어에 필요

driver = webdriver.Chrome('webCrawling\chromedriver_win32\chromedriver.exe')
driver.get('http://www.encar.com/pr/pr_index.do?WT.hit=index_gnb')
time.sleep(0.5)

#팝업창 닫기
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
        # 검색 된 전체 차량 수를 출력하는 태그 부분의 실제 text 부분만 추출하여 변수로 저장.
    searchResult = str(driver.find_element_by_xpath('//*[@id="resultWrap"]/div[2]/div[1]/div[1]/span').text)
    print(searchResult)

    if searchResult == "검색결과 없음":     # 검색결과가 존재하지 않을 경우,
        print("매물이 없습니다. 건너띕니다.")
        continue
    else:                                   # 검색 결과가 존재할 경우, replace()로 쉼표까지 제거하여 숫자만 추출하여 변수 저장.
        cnt_searchResult = int(searchResult[5:-1].replace(",",""))
        print(cnt_searchResult)

        #페이지 당 5개의 검색 결과를 보여주므로 cnt_searchResult/5 = '전체 페이지 수'
        if cnt_searchResult < 6:                                # 검색결과가 6개 미만일 경우, 페이지 수 = 1
            pageNum = 1
        else:
            if (cnt_searchResult%5) == 0:                       # 검색결과가 6개 이상이고, 5로 나눴을 때 나머지가 없을 경우, 
                pageNum = int(cnt_searchResult/5)               # 페이지 수 = 검색결과/5
            else:                                               # 검색결과가 6개 이상이고, 5로 나눳을 때 나머지가 있을 경우,
                pageNum = math.trunc(cnt_searchResult/5) + 1    # 페이지 수 = 검색결과/5를 trunc()로 반내림하고 거기에 +1 증가.
        print(pageNum)
        pageNum += 1                                            # for i in range(1, x)는 x-1까지 반복문을 돌기 때문에 x까지 하기 위해서 +1을 해준다.

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
        
        except:                             #selenium Exception : NoSuchElementException
            print("%s 의 페이지 수에 변동이 생겼습니다. 현재 마지막 페이지입니다." % cName)
            
            data = pd.DataFrame(car_info)
            print(tabulate(data, headers='keys', tablefmt='psql', showindex=False))
            print("%s 완료" % cName)

            if not os.path.exists('output_car_info.xlsx'):
                with pd.ExcelWriter('output_car_info.xlsx', mode='w', engine='openpyxl', ) as writer:
                    data.to_excel(writer, index=False, encoding = 'utf-8-sig', sheet_name = cName)
            else:
                with pd.ExcelWriter('output_car_info.xlsx', mode='a', engine='openpyxl') as writer:
                    data.to_excel(writer, index=False, encoding = 'utf-8-sig', sheet_name = cName)
            
            print("다음 회사로 넘어갑니다.")
            continue

        data = pd.DataFrame(car_info)
        print(tabulate(data, headers='keys', tablefmt='psql', showindex=False))
        print("%s 완료" % cName)

        if not os.path.exists('output_car_info.xlsx'):
            with pd.ExcelWriter('output_car_info.xlsx', mode='w', engine='openpyxl', ) as writer:
                data.to_excel(writer, index=False, encoding = 'utf-8-sig', sheet_name = cName)
        else:
            with pd.ExcelWriter('output_car_info.xlsx', mode='a', engine='openpyxl') as writer:
                data.to_excel(writer, index=False, encoding = 'utf-8-sig', sheet_name = cName)
        print("다음 회사로 넘어갑니다.")
        
        # try:
        #     if not os.path.exists('output_car_info.csv'):
        #         data.to_excel('output_car_info.xlsx', index = False,  encoding = 'utf-8-sig', sheet_name = cName, mode = 'w')   #   utf-8-sig OR cp949
        #         print("csv 생성 완료.")
        #     else:
        #         data.to_excel('output_car_info.xlsx', index = False,  encoding = 'utf-8-sig', sheet_name = cName, mode = 'a')   #   utf-8-sig OR cp949
        #         print("csv 생성 완료.")
        # except Exception as e:
        #     print(e)

