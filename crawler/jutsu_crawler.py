import scrapy
from bs4 import BeautifulSoup

class BlogSpider(scrapy.Spider):
    name = 'narutospider'
    # Url of the website from where we are extracting the data 
    start_urls = ['https://naruto.fandom.com/wiki/Special:BrowseData/Jutsu?limit=250&offset=0&_cat=Jutsu']

    def parse(self, response):
        # The below loop is too go over each link and open it and extract the title in dictionary format
        for href in response.css('.smw-columnlist-container')[0].css("a::attr(href)").extract():
            extracted_data = scrapy.Request("https://naruto.fandom.com/"+ href, callback=self.parse_jutsu)
            # it will save the file in jsonl format  (List of json Object)
            yield extracted_data

        # The below function is to navigate to next page 
        for next_page in response.css('a.mw-nextlink'):
            yield response.follow(next_page, self.parse)

    def parse_jutsu(self, response):
        #1. Extracting the Title(Name) text using the class
        jutsu_name = response.css("span.mw-page-title-main::text").extract()[0]
        # Inorder to remove the trailing spacing of the title jutsu_name 
        jutsu_name = jutsu_name.strip()

        # Now let try to extract the description of the title and classification 
        # The problem here is both are in same common div, [0] means first element of the div
        div_selector = response.css("div.mw-parser-output")[0]
        # As both are in same div so its a html page so we cant directly route and extract for we need extract the html for that we can use soup 
        # Now extract the html of the div_selector
        div_html = div_selector.extract()

        # In order to filter out html we have library called beautiful soup 
        # Initialize beautiful object 
        # find div will find the first in the html 
        soup = BeautifulSoup(div_html).find('div')

        #2. To get the Classification Type 
        # Now we have loop over the html to get the classification type value 
        # Step 1. As in html we can see its under aside so will first find aside section
        # If there is aside we will process other wise skip it 
        jutsu_type = ""
        if soup.find('aside'):
            # Now extract the aside section 
            aside = soup.find('aside')
            # Step 2. Now loop over each row and each row is div and class name is pi-data
            for cell in aside.find_all('div', {'class':'pi-data'}):
                # Steps 3. Now we want to extract the div which have h3 and text whose value is Classification 
                if cell.find('h3'):
                    # We are storing the h3 value 
                    cell_name = cell.find('h3').text.strip()
                    # if the h3 value is classification then we are taking the text i.e classification 
                    if cell_name == "Classification":
                        # Now we want to extract the value of next div beacuse there would be the classification value 
                        jutsu_type =  cell.find('div').text.strip()

        #3. Description Content 
        # Now we dont need any content from aside we are just removing the aside content 
        soup.find('aside').decompose()

        # Now we also have to remove the Trivia Section and there is no div section so we will try to remove everything before Trivia word
        jutsu_description = soup.text.strip()
        # We store eveyrthing before trivia word [0] means 
        jutsu_description = jutsu_description.split('Trivia')[0].strip()

        return dict (jutsu_name = jutsu_name,
                jutsu_type = jutsu_type,
                jutsu_description = jutsu_description )


        