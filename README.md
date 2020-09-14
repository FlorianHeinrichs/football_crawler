# football_crawler
Simple web crawler that crawl basic data of professional German football players

The crawler *football* crawls basic data of professional German football players (1. Bundesliga) from the website www.fussballdaten.de and returns them in a JSON file with the following variables:
* Player name
* Nationality
* Current club
* Year (of joining current club)
* Date of birth
* Age
* Height
* Weight
* Position
* Best foot

The data is crawled in three steps:

1. The *parse* method crawls the start url for links to the teams. 

        start_urls = ['https://www.fussballdaten.de/bundesliga/tabelle/',]
     
        def parse(self, response):
            clubs = response.xpath("//div[@id='w2']/table[@class='table lh2']/tbody/tr")
            for club in clubs:
                name = club.xpath(".//td/a/text()").get()[1:]
                link = club.xpath(".//td/a/@href").get() + "/kader/"

                yield response.follow(url=link, 
                                      callback=self.parse_club, 
                                      meta = {'club_name': name})
            
   1. Note that the crawler can be extended to the 2. Bundesliga and 3. Liga by setting:
      
          start_urls = [
		          'https://www.fussballdaten.de/bundesliga/tabelle/',
          		'https://www.fussballdaten.de/2liga/tabelle/',
          		'https://www.fussballdaten.de/3liga/tabelle/',
        	]
    
2. The *parse_club* method crawls the teams for links to the players.
    
        def parse_club(self, response):
            club_name = response.request.meta['club_name']
            players = response.xpath("//div[@id='kaderTabellen']/div[@class='content-tabelle']/div[@id='grid-spieler']/table[@class='table table-statistik']/tbody/tr/td[@class='vam img-abstand pr']/div[@class='dib']//a[@class='table-link hidden-xs']")
        
            for player in players:
                name = player.xpath(".//text()").get()
                link = player.xpath(".//@href").get()

                yield response.follow(url=link, callback=self.parse_player,
                                      meta = {'club_name': club_name, 
                                              'player_name': name})
            
3. The *parse_player* method crawls the players' profiles and yields the final data.
    
        def parse_player(self, response):
            player_name = response.request.meta['player_name']
            player_info = response.xpath("//dl[@class='dl-horizontal']")
            categories = player_info.xpath(".//dt/text()").getall()
            personal_data = player_info.xpath(".//dd/text()").getall()
            categories.append('player_name')
            personal_data.append(player_name)
            yield dict(zip(categories, personal_data))
