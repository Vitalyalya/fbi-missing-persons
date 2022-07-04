import requests
import json
from bs4 import BeautifulSoup
import re
import urllib3
import json

headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
    }

all_data = []

def collect_data(page_number):
    s = requests.Session()
    
    r = s.get(url=f"https://www.fbi.gov/wanted/vicap/missing-persons/@@castle.cms.querylisting/querylisting-1?page={page_number}", headers=headers)    
    src = r.text
    soup = BeautifulSoup(src, "lxml")
    
    all_links = soup.find_all("li")

    for link in all_links:

        #Ссылки на страницы с пропавшими

        person_link = link.find("a").get("href")
        print(person_link)

        #Переходим по ссылкам        
        
        http = urllib3.PoolManager()
        response = http.request('GET', person_link)
        soup = BeautifulSoup(response.data.decode('utf-8'), "lxml")

        #Собираем имя
        page_title = soup.find('h1', class_="documentFirstHeading").get_text()

        #Место рождения + переделываем в читабельный формат
        location = soup.find("p", class_="summary")
        paragraphs = []
        for x in location:
            paragraphs.append(str(x))
        location_birthdate = ' '.join([str(elem) for elem in paragraphs if elem != '<br/>'])

        #Ссылка на картинку
        img_link = soup.find("div", class_="col-md-4 wanted-person-mug").find("img").get("src")

        #Особые приметы
        special_signs = []
        try:

            table = soup.find("table", class_="table table-striped wanted-person-description")
            table_body = table.find("tbody")
            rows = table_body.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                special_signs.append([ele for ele in cols if ele])
            if len(special_signs) < 8:
                for _ in range(0, 8):
                    special_signs.append([None, None])

        except:
            for i in range (1, 9):
                special_signs.append([None, None])

        #Подробности
        details = soup.find("div", class_="wanted-person-details").find("p").get_text()

        #Доп инфа
        remarks_buffer = []
        try:
            remarks = soup.find("div", class_="wanted-person-remarks").find_all("p")
            if remarks is not None:

                for i in remarks:
                    
                    person_info = i.get_text()
                    remarks_buffer.append(person_info)
                remarks_buffer.append(details)
                remarks_final = '. '.join(remarks_buffer)
                    
        except:
            remarks_final = "No remarks specified"
        
        print("___________________________"*4)
        all_data.append(
            {
                "Name": page_title,
                "Image_link": img_link,
                "Location": location_birthdate,
                "Age": special_signs[0][1],
                "Hair": special_signs[1][1],
                "Eyes": special_signs[2][1],
                "Height": special_signs[3][1],
                "Weight": special_signs[4][1],
                "Sex": special_signs[5][1],
                "Race": special_signs[6][1],
                "Scrars_and_marks": special_signs[7][1],
                "Remarks": remarks_final,
            }
        )

    return all_data
          



def main():

    s = requests.Session()    
    r = s.get(url="https://www.fbi.gov/wanted/vicap/missing-persons/@@castle.cms.querylisting/querylisting-1?page=1", headers=headers)    
    src = r.text
    soup = BeautifulSoup(src, "lxml")
    pagination = soup.find("p", class_="right").get_text()
    pagination = int(re.sub('[^0-9]', '', pagination))

    if pagination % 15 == 0:
        pagination = pagination // 15
    else: 
        pagination = pagination // 15 + 1

    for page_number in range(1, pagination + 1):
        final_data = collect_data(page_number)    
        print(f"Collected {page_number} / {pagination}")
    
    with open("results.json", "w", encoding="utf-8") as file:
        json.dump(final_data, file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()                