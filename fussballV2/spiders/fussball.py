# -*- coding: utf-8 -*-
import scrapy


class FussballSpider(scrapy.Spider):
    name = 'fussball'
    allowed_domains = ['www.fussballdaten.de']
    start_urls = [
		'https://www.fussballdaten.de/bundesliga/tabelle/',
		'https://www.fussballdaten.de/2liga/tabelle/',
		'https://www.fussballdaten.de/3liga/tabelle/',
	]

    def parse(self, response):
        clubs = response.xpath("//div[@id='w2']/table[@class='table lh2']/tbody/tr")
        for club in clubs:
            name = club.xpath(".//td/a/text()").get()[1:]
            link = club.xpath(".//td/a/@href").get() + "/kader/"

            yield response.follow(url=link, 
            callback=self.parse_club, 
            meta = {'club_name': name})

    def parse_club(self, response):
        club_name = response.request.meta['club_name']

        players = response.xpath("//div[@id='kaderTabellen']/div[@class='content-tabelle']/div[@id='grid-spieler']/table[@class='table table-statistik']/tbody/tr/td[@class='vam img-abstand pr']/div[@class='dib']//a[@class='table-link hidden-xs']")
        for player in players:
            name = player.xpath(".//text()").get()
            link = player.xpath(".//@href").get()

            yield response.follow(url=link, callback=self.parse_player,
            meta = {'club_name': club_name, 'player_name': name})

    def parse_player(self, response):
        club_name = response.request.meta['club_name']
        player_name = response.request.meta['player_name']
        player_info = response.xpath("//dl[@class='dl-horizontal']")
        categories = player_info.xpath(".//dt/text()").getall()
        personal_data = player_info.xpath(".//dd/text()").getall()
        categories.append('club_name')
        categories.append('player_name')
        personal_data.append(club_name)
        personal_data.append(player_name)
        yield dict(zip(categories, personal_data))