from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re
from webdriver_manager.chrome import ChromeDriverManager

#driver_path = r"src/chromedriver.exe"

def scraping_job_descriptions(profile, location, max_n):
    #try: 
    profile = re.sub(" ", '-', profile)
    location = re.sub(" ", '-', location)

    url = "https://www.linkedin.com/jobs/search?keywords=" + profile + "&location=" + location + "&geoId=92000000"
    print(url)
    options = Options()
    options.add_argument("--headless") # utilizar un navegador sin cabeza
    options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)

    driver.get(url)
    time.sleep(3)
    previous_height = driver.execute_script('return document.body.scrollHeight')

    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

        time.sleep(3)

        new_height = driver.execute_script('return document.body.scrollHeight')

        l=[]
        for a in driver.find_elements(By.CLASS_NAME, "base-card__full-link.absolute.top-0.right-0.bottom-0.left-0.p-0.z-\\[2\\]"):
            link = a.get_attribute('href')
            l.append(link)
            if len(l) >= max_n:
                #print("The maximum number of job posts were collected")
                break

        # break when we get to the end of the page
        if new_height == previous_height:
            while len(l) < max_n:
                boton_sesion = driver.find_element(By.CLASS_NAME, "infinite-scroller__show-more-button.infinite-scroller__show-more-button--visible")
                boton_sesion.click()
                
                l=[]
                for a in driver.find_elements(By.CLASS_NAME, "base-card__full-link.absolute.top-0.right-0.bottom-0.left-0.p-0.z-\\[2\\]"):
                    link = a.get_attribute('href')
                    l.append(link)
                print(len(l))    
            print("The maximum number of job posts were collected")
            break

        previous_height = new_height
        print(len(l))
        #break #ESTO ES PARA PRUEBAS SOLAMENTE

    job_titles = []
    company_names = []
    company_locations = []
    job_descriptions = []
    j = 1

    for b in range(len(l)):
        try: 
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[b+1]) 
            driver.get(l[b])
            job_titles.append(driver.find_element(By.CLASS_NAME, "top-card-layout__title.font-sans.text-lg.papabear\\:text-xl.font-bold.leading-open.text-color-text.mb-0.topcard__title").text)
            company_names.append(driver.find_element(By.CLASS_NAME, "topcard__org-name-link.topcard__flavor--black-link").text)
            locations = driver.find_element(By.CLASS_NAME, "topcard__flavor.topcard__flavor--bullet").text
            locations = re.sub(",","",locations)
            company_locations.append(locations)
            description = driver.find_element(By.CLASS_NAME, 'show-more-less-html__markup').text
            description = re.sub(",","",description)
            job_descriptions.append(description)
            print(f'Scraping the Job Offer {j} DONE.')
            j+= 1
            time.sleep(2)
        except:
            pass
        
        time.sleep(3)


    # Creating the dataframe 
    df = pd.DataFrame(list(zip(job_titles,job_descriptions)),
    columns =['job_title','Description'])

    df["Query"]= profile

    print(df.Description)
    return(df)
    # except:
    #     print("It's not possible to do the scraping process")
    #     return None
   

