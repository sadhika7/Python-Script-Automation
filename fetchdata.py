from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

#setting the number of pages in the website for pagination scraping
MAX_PAGE_NUM = 59

binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe')
caps = DesiredCapabilities().FIREFOX
caps["marionette"] = True
driver = webdriver.Firefox(capabilities=caps, firefox_binary=binary, executable_path="C:\\Users\\edhkswt\\Downloads\\geckodriver-v0.24.0-win64\\geckodriver.exe")
url = "https://access.redhat.com/errata/#/?q=&p=1&sort=portal_publication_date%20desc&rows=10&portal_advisory_type=Security%20Advisory&portal_product=Red%20Hat%20Enterprise%20Linux&portal_product_version=7.4&portal_architecture=x86_64"
driver.maximize_window()
driver.get(url)

pages_remaining = True

while pages_remaining:
    for i in range(1,MAX_PAGE_NUM+1):
        advisory_element = WebDriverWait(driver,10).\
            until(lambda driver: driver.find_elements_by_xpath("//*[contains(@id,'th-RHSA-')]/span/a"))

        adv_len = len(advisory_element)
      
    #scrolling down to get the respective advisory link each time the page navigates back
    def scroll_shim(passed_in_driver, object):
        x = object.location['x']
        y = object.location['y']
        scroll_by_coord = 'window.scrollTo(%s,%s);' % (
            x,
            y
        )
        scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
        passed_in_driver.execute_script(scroll_by_coord)
        passed_in_driver.execute_script(scroll_nav_out_of_way) 


    for i in range(adv_len):

        adv = WebDriverWait(driver,10).\
            until(lambda driver: driver.find_elements_by_xpath("//*[contains(@id,'th-RHSA-')]/span/a"))
        published_date = WebDriverWait(driver,10).\
            until(lambda driver: driver.find_elements_by_tag_name('time'))
        if 'firefox' in driver.capabilities['browserName']:
            scroll_shim(driver, adv[i])
        actions = ActionChains(driver)
        actions.move_to_element(adv[i])
        actions.click()
        actions.perform()
    
        advisory = [x.text for x in adv]
        date = [x.text for x in published_date]

        updated_packages = WebDriverWait(driver,10).\
            until(lambda driver: driver.find_elements_by_xpath("//a[@href = '#packages']"))
    
        pkg_len = len(updated_packages)
    
        for i in range(pkg_len):
            actions1 = ActionChains(driver)
            actions1.move_to_element(updated_packages[i])
            actions1.perform()
            updated_packages[i].click()

        #only retrieve the data under version 7.4
        version = WebDriverWait(driver,10).\
            until(lambda driver: driver.find_elements_by_xpath("//h2[contains(text(),'7.4')]"))
    
        for pkg in version:
            #only retrieve the rpms under architecture x86_64
            rpm= WebDriverWait(pkg,10).\
                until(lambda driver: pkg.find_elements_by_xpath("//td[contains(text(),'x86_64.rpm') or contains(text(),'i686.rpm')]"))

        rpm = [x.text for x in rpm] 
        rpm_len = len(rpm)

        with open('results.txt','w+') as f:
            for i in range(adv_len):
                f.write("\n"+advisory[i]+"\t")
                f.write(date[i]+"\t")

                for j in range(rpm_len):
                    f.write("\n"+rpm[j]+"\t\n")
        f.close()
     
        #goes back to the homepage to get information about another advisory
        driver.execute_script("window.history.go(-1)")
        driver.implicitly_wait(30)

    try:
        #keeps on clicking the next button until the last page
        next_link = WebDriverWait(driver,10).\
            until(lambda driver: driver.find_element_by_link_text("›")) 
        if 'firefox' in driver.capabilities['browserName']:
            scroll_shim(driver, next_link)
        actions = ActionChains(driver)
        actions.move_to_element(next_link)
        actions.click()
        actions.perform()
        driver.implicitly_wait(10)

        advisory_element = WebDriverWait(driver,10).\
            until(lambda driver: driver.find_elements_by_xpath("//*[contains(@id,'th-RHSA-')]/span/a"))

    except NoSuchElementException:
        pages_remaining = False
 
driver.close()