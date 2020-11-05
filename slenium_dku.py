from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup 
import json
from key_encrypt import dynamicPwd
import time
import os


class dku_scraper(object):
    """ A scraper made out of selenium to scrape website that requires netid and password to log in """
    def __init__(self, netid, pwd, driver):
        """ Sets the password, netid and pass in the webdriver used """
        self.netid = netid
        self.pwd = pwd
        self.driver = driver

    def login_DKU_hub(self,url):
        """ log into the url given using the netid and pwd in the object dku_scraper """
        self.driver.get(url)
        assert "Duke | Log In" in driver.title
        # Find an expand
        print(driver.title)
        if ( EC.visibility_of_element_located((By.ID,"expand-netid")) ):

            netid_expand = driver.find_element_by_id("expand-netid")
            netid_expand.click()

            wait = WebDriverWait(driver,10)
            # username = driver.find_element_by_id("j_username")
            # password = driver.find_element_by_id("j_password")

            wait.until(EC.visibility_of_element_located( (By.ID,"netid-option") ))
            username = wait.until(EC.visibility_of_element_located( (By.ID,"j_username") ))
            password = wait.until(EC.visibility_of_element_located( (By.ID,"j_password") ))

        else:
            username = driver.find_element_by_id("j_username")
            password = driver.find_element_by_id("j_password")


    
        username.clear()
        username.send_keys(self.netid)
        password.clear()
        password.send_keys(self.pwd)
        password.send_keys(Keys.RETURN)

        print("You are currently logged in on page title: \n ", driver.title)

        return driver

    def auto_fill_in_health_report(self):
        health_report_url = "https://dukekunshan.formstack.com/forms/student_daily_health_report"
        self.login_DKU_hub(health_report_url)

        wait = WebDriverWait(driver,10)

        lower_temp = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#field96310051_1")))
        no_sympton = wait.until(EC.visibility_of_element_located( (By.CSS_SELECTOR,"#field96310053_2") ))
        not_in_high_risk = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#field96310883_2")) )

        current_location = driver.find_element_by_css_selector("#field96310885")
        current_location.send_keys("Kunshan")

        have_not_been_contacted = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#field96310886_2")) )

        option_list = [lower_temp,no_sympton,not_in_high_risk,have_not_been_contacted]
        # option_list = wait.until(EC.visibility_of_all_elements_located( (By.CSS_SELECTOR,"#field96310051_1, \n #field96310053_2, \n #field96310883_2, \n #field96310886_2") ))
        for option in option_list:
            option.click()
            time.sleep(1)

        
        
        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#fsSubmitButton3988487"))) #driver.find_element_by_css_selector("#fsSubmitButton3988487")
        time.sleep(1)
        submit_button.click()

    def scraping_course_schedule_from_search_by_cat(self):
        

        wait = WebDriverWait(driver,10)
        # username = driver.find_element_by_id("j_username")
        # password = driver.find_element_by_id("j_password")
        url = "https://dkuhub.dku.edu.cn/psc/ps/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?Page=SSR_CLSRCH_ENTRY&Action=U"
        self.login_DKU_hub(url)

        # options = wait.until(EC.visibility_of_element_located( (By.ID,r"CLASS_SRCH_WRK2_STRM\$35\$") ))
        # options.click()
        wait.until(EC.visibility_of_element_located( (By.ID,r"CLASS_SRCH_WRK2_STRM\$35\$") )).click()
        
        select_term = wait.until(EC.visibility_of_element_located( (By.CSS_SELECTOR,r"#CLASS_SRCH_WRK2_STRM\$35\$ > option:nth-child(9)") ))
        select_term.click()

        time.sleep(1)
        select_career = wait.until(EC.visibility_of_element_located( (By.ID,r"SSR_CLSRCH_WRK_ACAD_CAREER\$2") ))
        select_career.click()
        select_undergrad = wait.until(EC.visibility_of_element_located( (By.CSS_SELECTOR, r"#SSR_CLSRCH_WRK_ACAD_CAREER\$2 > option:nth-child(3) ") ))
        select_undergrad.click()

        time.sleep(1)
        subjest_select = wait.until(EC.visibility_of_element_located( (By.XPATH, r'''//*[@id="SSR_CLSRCH_WRK_SUBJECT_SRCH$0"]''') ))
        # subjest_select.click()
        dic = {}
        option_lst = subjest_select.find_elements_by_tag_name('option')
        val_lst = [ o.get_attribute('value') for o in option_lst ]
        for val in val_lst:
            option = subjest_select.find_element_by_css_selector('option[value=%s]'%('\'' + val + '\''))
            print(option.get_attribute('selected'))
            if option.get_attribute('selected') == 'true' :
                continue

            option.click()
            
            search_button = wait.until(EC.visibility_of_element_located( (By.ID, "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH") ))
            search_button.click()

            clas_dic = dku_scraper.scrape_class_search_results( val + '.json')
            dic[val] = clas_dic

            #get back to the search option page
            wait.until(EC.visibility_of_element_located( (By.ID, 'CLASS_SRCH_WRK2_SSR_PB_MODIFY') )).click()
            
            result = None
            while result is None:
                try:
                    result = driver.find_element_by_css_selector( r"#SSR_CLSRCH_WRK_ACAD_CAREER\$2 > option:nth-child(3) " )
                except:
                    pass

            subjest_select = wait.until(EC.visibility_of_element_located( (By.XPATH, r'''//*[@id="SSR_CLSRCH_WRK_SUBJECT_SRCH$0"]''') ))
            



        # time.sleep(1)
        

        # select_okay_for_50_classes = wait.until(EC.visibility_of_element_located( (By.CSS_SELECTOR, r"#\#ICSave") ))
        # select_okay_for_50_classes.click()

        # time.sleep(30)

        

            

        
        return dic

    def scrape_shopping_cart(self, write = True, json_filename = '2021_spring_cart.json', cart_url = 'https://dkuhub.dku.edu.cn/psc/ps/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL?Page=SSR_SSENRL_CART&Action=A'):
        self.login_DKU_hub(cart_url)
        wait = WebDriverWait(driver,10)

        # Select the 2021 term
        wait.until(
            EC.visibility_of_element_located( (By.CSS_SELECTOR, r'#SSR_DUMMY_RECV1\$sels\$3\$\$0') )
        ).click()
        
        wait.until(
            EC.visibility_of_element_located( (By.CSS_SELECTOR, r'#DERIVED_SSS_SCT_SSR_PB_GO') )
        ).click()

        table = wait.until(
            EC.visibility_of_element_located( (By.CSS_SELECTOR, r'#SSR_REGFORM_VW\$scroll\$0 > tbody > tr:nth-child(2) > td > table' ) )
        )

        keys = [th.text for th in table.find_elements_by_tag_name('th')]
        c_dic = {}

        for tr in table.find_elements_by_css_selector(r'''tr[id^='trSSR_REGFORM_VW\$0_row']'''):
            values = [td.text for td in tr.find_elements_by_tag_name('td')]
            d = dict(zip(keys, values))
            status= tr.find_element_by_tag_name('img').get_attribute('alt')
            d['Status'] = status
            c_dic[d.pop('Class')] = d

        

        dic = {'2021_Spring_cart' : c_dic}
        if(write):
            path = 'shopping_cart'
            with open(os.path.join(path,json_filename), 'w') as json_file:
                json.dump(dic,
                          json_file,
                          indent=4,
                          separators=(',', ': '))
        
        return dic

    @staticmethod 
    def scrape_class_search_results( json_filename, write = True ):
        wait = WebDriverWait(driver,10)
        presenting_table = wait.until(EC.visibility_of_element_located( (By.ID, r"ACE_\$ICField\$4\$\$0") ))
        search_result = wait.until(EC.visibility_of_element_located( (By.CSS_SELECTOR, '#win0divSSR_CLSRSLT_WRK_GROUPBOX1 > table > tbody > tr:nth-child(1) > td') )).text
        search_number = int(search_result.partition(' ')[0])

        print(search_number)

        clas_dic = {}
        div_lst = presenting_table.find_elements_by_css_selector(r'''div[id^="win0divSSR_CLSRSLT_WRK_GROUPBOX2\$"]''')

        for div in div_lst :
            clas_name = div.find_element_by_tag_name('div').text
            # print(clas_name)
            # large_table = div.find_element_by_css_selector(r'''table[id^="\$ICField48\$scroll\$"]''')
            clas_dic[clas_name] = {}

            for table in div.find_elements_by_css_selector(r'''table[id^=SSR_CLSRCH_MTG1\$scroll\$]'''):


                keys = [th.text for th in table.find_elements_by_tag_name('th')]
                values = [td.text for td in table.find_elements_by_tag_name('td')]
                d = dict(zip(keys, values))
                sec_name = d.pop('Class')
                d.pop(" ")

                # Get the class status:
                status= table.find_element_by_tag_name('img').get_attribute('alt')
                d['Status'] = status
                clas_dic[clas_name][sec_name] = d


        if(write):
            path = 'jsons'
            with open(os.path.join(path,json_filename), 'w') as json_file:
                json.dump(clas_dic,
                          json_file,
                          indent=4,
                          separators=(',', ': '))

        return clas_dic


    


# assert "No results found." not in driver.page_source
netid = "zj61"
pwd = dynamicPwd()
# input("pwd= ")
shopping_cart_url = "https://dkuhub.dku.edu.cn/psp/ps/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL?Page=SSR_SSENRL_CART"
search_URL = "https://dkuhub.dku.edu.cn/psc/ps/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?Page=SSR_CLSRCH_ENTRY&amp;Action=U"
health_report_url = "https://dukekunshan.formstack.com/forms/student_daily_health_report"
driver = webdriver.Chrome()
test_scraper = dku_scraper(netid,pwd,driver)


## scrape all the categories category by category 
# dic = test_scraper.scraping_course_schedule_from_search_by_cat()

# with open(r'all.json', 'w') as json_file:
#   json.dump(dic,
#             json_file,
#             indent=4,
#             separators=(',', ': '))

test_scraper.scrape_shopping_cart()
