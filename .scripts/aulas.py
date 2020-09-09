from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
import json

# Opening JSON file
f = open('data.json',)

# returns JSON object as a dictionary
data = json.load(f)

# Iterating through the json list
for i in data['info']:
        email = i['email']
        user = i['user']
        password = i['password']
# Closing file
f.close()

driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())

driver.get("https://accounts.google.com/signin/v2/identifier?service=classroom&passive=1209600&continue=https%3A%2F%2Fclassroom.google.com%2F%3Femr%3D0&followup=https%3A%2F%2Fclassroom.google.com%2F%3Femr%3D0&flowName=GlifWebSignIn&flowEntry=ServiceLogin")

element = driver.find_element_by_id("identifierId")
element.send_keys(email)
driver.find_element_by_id("identifierNext").click()

element = driver.find_element_by_id("username")
element.send_keys(user)

element = driver.find_element_by_id("password")
element.send_keys(password)
