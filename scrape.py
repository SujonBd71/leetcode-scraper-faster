import pandas as pd
import time,csv,sys,pytz,os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.chrome.options import Options

import numpy as np
from datetime import date,datetime,timedelta

driver = None

def logTime(startTime, currentTime):
    endTime = time.time()
    currentTime = currentTime or endTime
    hours, rem = divmod(endTime-currentTime, 3600)
    minutes, seconds = divmod(rem, 60)
    print("[Duration:{:0>2}:{:0>2}:{:05.2f}, ".format(int(hours),int(minutes),int(seconds)), end='')
    hours, rem = divmod(endTime-startTime, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Total:{:0>2}:{:0>2}:{:05.2f}] ".format(int(hours),int(minutes),seconds), end='')
    return endTime


def export(df, name, path = ''):
    now = lambda: datetime.now().astimezone().isoformat(timespec='seconds').replace('-','').replace(':','')
    fullPath = 'Scraped-Data/' + path
    Path(fullPath).mkdir(parents=True, exist_ok=True)
    df.to_csv(fullPath + '/' + name + '-' + now() + '.csv')



def login2():
    username = "sujon.sarkar31@gmail.com"
    passwd = "#Sujon3402"
    time.sleep(2)
    while True:
        try:
            driver.find_element_by_id("id_login").send_keys(username)
            time.sleep(5)
            driver.find_element_by_id("id_password").send_keys(passwd)
            time.sleep(5)
            driver.find_element_by_id("signin_btn").click()
            break
        except:
            time.sleep(3)


def login():
    url = 'https://leetcode.com/accounts/login'
    driver.get(url)
    WebDriverWait(driver, timeout=15).until_not(lambda x: x.find_element_by_class_name("spinner").is_displayed())
    try:
        emailInput = driver.find_element_by_id('id_login')
        passwordInput = driver.find_element_by_id('id_password')
        loginButton = driver.find_element_by_id('signin_btn')
        # emailInput.send_keys(os.getenv('LEETCODE_USERNAME'))
        # passwordInput.send_keys(os.getenv('LEETCODE_PASSWORD'))
        emailInput.send_keys("sujon.sarkar31@gmail.com")
        passwordInput.send_keys("#Sujon3402")
        loginButton.click()
    except:
        pass
    finally:
        WebDriverWait(driver, timeout=5).until(lambda x: x.find_element_by_class_name("trending-topic-container").is_displayed())


def openAndExportAllProblems():
    url = 'https://leetcode.com/problemset/all/'
    driver.get(url)
    WebDriverWait(driver, timeout=5).until(lambda x: x.find_element_by_tag_name("select").is_displayed())
    select = Select(driver.find_element_by_tag_name("select"))
    selectLen = len(select.options)
    select.select_by_index(selectLen-1)
    script = '''
const rows = document.getElementsByClassName('reactable-data')[0].children;
const problems = [];
for (const row of rows) {
  const problem = [], cols = row.children;
  const frequency = parseFloat(row.getElementsByClassName('progress-bar')[0].style.width);
  const link = cols[2].querySelector('a').href;
  problem.push(cols[1].innerText.trim());
  problem.push(cols[2].innerText.trim());
  problem.push(cols[4].innerText.trim());
  problem.push(cols[5].innerText.trim());
  problem.push(frequency);
  problem.push(link);
  problems.push(problem);
}
return problems
    '''
    problemsData = driver.execute_script(script)
    problems = pd.DataFrame(problemsData, columns = ['Id','Title','Acceptance','Difficulty','Frequency','Link'])
    problems = problems.set_index('Id')
    export(problems, 'Problems')
    print("Exported %d Problems (100%%)" % len(problems))
    return problems


def getProblemsByTitle():
    return allProblems.reset_index().set_index('Title')


def openAndExportAllCompanies():
    url = 'https://leetcode.com/problemset/all/'
    driver.get(url)
    WebDriverWait(driver, timeout=5).until(lambda x: x.find_element_by_tag_name("select").is_displayed())
    driver.find_element_by_css_selector('#expand-company .btn').click()
    script = '''
const buttons = document.getElementById('current-company-tags').children;
const companies = [];
for (const button of buttons) {
  const company = [];
  company.push(button.firstElementChild.innerText.trim());
  company.push(button.firstElementChild.nextElementSibling.innerText.trim());
  company.push(button.href);
  companies.push(company);
}
return companies
    '''
    companiesData = driver.execute_script(script)
    companies = pd.DataFrame(companiesData, columns = ['Name','Count','Link'])
    companies.index = companies.index + 1
    companies.index.name = 'Serial'
    export(companies, 'Companies')
    print("Exported %d Companies (100%%)" % len(companies))
    return companies



def getFirstOption():
    driver.find_element_by_id('react-select-2--value-item').click()
    firstOption = driver.execute_script("return (4-document.querySelectorAll('#react-select-2--list div[role=option]').length);")
    driver.find_element_by_id('react-select-2--value-item').click()
    return firstOption



def selectOption(n):
    driver.find_element_by_id('react-select-2--value-item').click()
    driver.find_element_by_id('react-select-2--option-' + str(n)).click()



def getCompanyProblems():
    script = '''
const rows = document.getElementsByClassName('reactable-data')[0].children;
const problems = [];
for (const row of rows) {
    const problem = [], cols = row.children;
    const tags = Array.from(cols[3].querySelectorAll('a')).map(t => t.innerText.trim()).join(', ');
    const frequency = parseFloat(row.getElementsByClassName('progress-bar')[0].style.width);
    const link = cols[2].querySelector('a').href;
    problem.push(cols[1].innerText.trim());
    problem.push(cols[2].innerText.trim());
    problem.push(tags);
    problem.push(cols[4].innerText.trim());
    problem.push(cols[5].innerText.trim());
    problem.push(frequency);
    problem.push(link);
    problems.push(problem);
}
return problems
    '''
    companyProblemsData = driver.execute_script(script)
    companyProblems = pd.DataFrame(companyProblemsData, columns = ['Id','Title','Tags','Acceptance','Difficulty','Frequency','Link'])
    companyProblems = companyProblems.set_index('Id')
    return companyProblems


def openAndExportAllCompanyProblems():
    startTime = time.time()
    currentTime = startTime
    optionNames = ['6_months', '1_year', '2_years', 'All_time']
    optionTotalCount = len(optionNames)
    companiesCount = len(allCompanies)
    currentTime = logTime(startTime, currentTime); print("Total Companies: %d" % companiesCount)
    for i in range(companiesCount):
        company = allCompanies.iloc[i]
        companyName = company['Name'].replace(' ','_')
        currentTime = logTime(startTime, currentTime); print("Processing %s (%d/%d) (%d%%)" % (companyName, i+1,companiesCount,((i+1)*100/companiesCount)))
        driver.get(company['Link'])
        WebDriverWait(driver, timeout=30).until(lambda x: x.find_element_by_id('react-select-2--value-item').is_displayed())
        driver.find_element_by_css_selector('input[type=checkbox]').click()
        driver.find_element_by_css_selector('.reactable-column-header th:nth-child(2)').click()
        firstOption = getFirstOption()
        currentTime = logTime(startTime, currentTime); print("Periods available: %d" % (optionTotalCount- firstOption))
        currentTime = logTime(startTime, currentTime); 
        for currentOption in range(firstOption, optionTotalCount):
            optionName = optionNames[currentOption]
            selectOption(currentOption)
            companyProblems = getCompanyProblems()
            print("%s: %d | " % (optionName, len(companyProblems)), end='')
            export(companyProblems, companyName + '-' + optionName, 'Company_Problems/Period-wise/' + optionName)
            export(companyProblems, companyName + '-' + optionName, 'Company_Problems/Name-wise/' + companyName)
        print()
    currentTime = logTime(startTime, currentTime); print("Exported Problems of %d Companies (100%%)" % companiesCount)



def openAndExportAllInterviews():
    url = 'https://leetcode.com/explore/interview/'
    driver.get(url)
    WebDriverWait(driver, timeout=5).until(lambda x: x.find_element_by_class_name('explore-card').is_displayed())
    script = '''
const cards = Array.from(document.querySelectorAll('.explore-card .premium')).map(e => e.closest('.explore-card'))
const interviews = [];
for (const card of cards) {
  const interview = [];
  interview.push(card.querySelector('.title').innerText.trim());
  interview.push(card.querySelector('.chapter').innerText.trim());
  interview.push(card.querySelector('.item').innerText.trim());
  interview.push(card.querySelector('a').href);
  interviews.push(interview);
}
return interviews;
    '''
    interviewsData = driver.execute_script(script)
    interviews = pd.DataFrame(interviewsData, columns = ['Title','Chapters','Problems','Link'])
    interviews.index = interviews.index + 1
    interviews.index.name = 'Serial'
    export(interviews, 'Interviews')
    print("Exported %d Interviews (100%%)" % len(interviews))
    return interviews



def joinProblemDetails(problem):
    problem['Id'] = None
    cols = ['Acceptance','Difficulty','Frequency','Link']
    for col in cols:
        problem[col] = None
    try:
        problem['Id'] = allProblemsByTitle.loc[problem['Problem']]['Id']
        for col in cols:
            problem[col] = allProblems.loc[problem['Id']][col]
    except:
        pass
    return problem



def getInterviewProblems():
    script = '''
const tables = document.getElementsByClassName('table-base');
const problems = [];
for (let i = 1; i <= tables.length; i++) {
  const table = tables[i-1];
  const chapterTitle = table.querySelector('.chapter-title').innerText.trim();
  const items = table.querySelectorAll('*[title="Coding Question"] ~ span');
  for (let j = 1; j <= items.length; j++) {
  const item = items[j-1];
    const itemTitle = item.innerText.trim();
    problems.push([i, chapterTitle, j, itemTitle]);
  }
}
return problems
    '''
    interviewProblemsData = driver.execute_script(script)
    interviewProblems = pd.DataFrame(interviewProblemsData, columns = ['ChapterSerial','Chapter','ProblemSerial','Problem'])
    interviewProblems = interviewProblems.apply(joinProblemDetails, axis=1)
    interviewProblems = interviewProblems.set_index('ChapterSerial')
    return interviewProblems



def openAndExportAllInterviewProblems():
    startTime = time.time()
    currentTime = startTime
    interviewsCount = len(allInterviews)
    currentTime = logTime(startTime, currentTime); print("Total interviews: %d" % interviewsCount)
    for i in range(interviewsCount):
        interview = allInterviews.iloc[i]
        interviewTitle = interview['Title'].replace(' ','_')
        currentTime = logTime(startTime, currentTime); print("Processing %s (%d/%d) (%d%%)" % (interviewTitle, i+1,interviewsCount,((i+1)*100/interviewsCount)))
        driver.get(interview['Link'])
        WebDriverWait(driver, timeout=10).until(lambda x: str(len(x.find_elements_by_css_selector('.table-base .table-item'))) == interview['Problems'])
        interviewProblems = getInterviewProblems()
        currentTime = logTime(startTime, currentTime); print("Chapters: %s | Problems: %d" % (interview['Chapters'], len(interviewProblems)))
        export(interviewProblems, interviewTitle, 'Interview_Problems')
        currentTime = logTime(startTime, currentTime); print("Exported Problems of %d Interviews (100%%)" % interviewsCount)


# print("loaded")
# options = Options()
# options.binary_location=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
# driver = webdriver.Chrome(options=options, executable_path='./chromedriver_win32/chromedriver.exe')

# login2()
# # allProblems = openAndExportAllProblems()

# print("all problem")


def logintest():
    global driver
    login_url = "https://leetcode.com/accounts/login/"
    chrome_opts = webdriver.ChromeOptions()
    opts = FirefoxOptions()
    options = Options()
    options.binary_location=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    driver = webdriver.Chrome(executable_path='./chromedriver_win32/chromedriver.exe')
    
    allprblm = "https://leetcode.com/problemset/all/"

    # driver.get("https://leetcode.com/company/zoho/")
    driver.maximize_window()
    driver.get(login_url)

    # username = input("Enter username/email: ")
    # passwd = input("Enter password: ")
    username = "sujon.sarkar31@gmail.com"
    passwd = "#Sujon3402"

    time.sleep(5)

    while True:
        try:
            driver.find_element_by_id("id_login").send_keys(username)
            time.sleep(5)
            driver.find_element_by_id("id_password").send_keys(passwd)
            time.sleep(5)
            driver.find_element_by_id("signin_btn").click()
            break
        except:
            time.sleep(3)
    time.sleep(5)

logintest()
print("loaded")
allProblems = openAndExportAllProblems()
allProblemsByTitle = getProblemsByTitle()
allCompanies = openAndExportAllCompanies()

start_time = time.time()
# openAndExportAllCompanyProblems()
# print("--- %s seconds ---" % (time.time() - start_time))


allInterviews = openAndExportAllInterviews()
openAndExportAllInterviewProblems()
print("--- %s seconds ---" % (time.time() - start_time))


driver.quit()







