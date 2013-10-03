#
# http://iphone.cdn.viasat.tv/iphone/008/00866/S86666_premonition_oxsfoewz60oneyvj_iphone.m3u8

# TV3
# http://viastream.viasat.tv/MobileStream/319793
# http://iphone.cdn.viasat.tv/iphone/009/00916/S91659_djurakuten_jhtrvgxbmmxsz44a_iphone.m3u8'
####################################################################################################
import re
VIDEO_PREFIX = "/video/viaplay"

ART = 'art-default.jpg'
ICON = 'icon-default.jpg'
ICON_PREFS = 'icon-prefs.png'

IPAD_UA = 'Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X; en-us) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B176 Safari/7534.48.3'


####################################################################################################

# This function is initially called by the PMS framework to initialize the plugin. This includes
# setting up the Plugin static instance along with the displayed artwork.
def Start():
    
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
    Plugin.AddViewGroup('List', viewMode = 'List', mediaType = 'items')
    
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = L('Title')
    ObjectContainer.view_group = 'List'
    
    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)

    HTTP.Headers['User-Agent'] = IPAD_UA

# This main function will setup the displayed items.
@handler(VIDEO_PREFIX, L('Title'), ICON, ART)
def MainMenu():

    oc = ObjectContainer()
    
    oc.add(DirectoryObject(key=Callback(TvShowsList), title=L('TV Menu Title'), thumb = R('icon-tv.png')))
    oc.add(DirectoryObject(key=Callback(MoviesList), title=L('Movies Menu Title'), thumb = R('icon-movie.png')))
    oc.add(DirectoryObject(key=Callback(Sport,title2=L('Sport Menu Title')), title = L('Sport Menu Title')))
    oc.add(DirectoryObject(key=Callback(Kids,title2=L('Kids Menu Title')), title = L('Kids Menu Title'), thumb = R('icon-kids.png')))
    oc.add(InputDirectoryObject(key = Callback(Search), title  = u"Search", prompt = u"Search", thumb = R('icon-search.png')))
    oc.add(PrefsObject(title = L('Preferences Menu Title'), thumb = R(ICON_PREFS)))

    return oc

def Search (query):
    query = String.Quote(query)

    TvQuery    = baseUrl() + '/ahah/block?contentType=tv&title=TV&perpage=100&type=search&query=' + query
    MovieQuery = baseUrl() + '/ahah/block?contentType=movies&title=Filmer&perpage=100&type=search&query=' + query

    if 'iosweb'in HTTP.Request(TvQuery).content:
        TvHits = True
    else:
        TvHits = False

    if 'iosweb'in HTTP.Request(MovieQuery).content:
        MovieHits = True
    else:
        MovieHits = False
    
    if not(TvHits) and not(MovieHits):
        return MessageContainer(
            "Search results",
            "Did not find any result for '%s'" % query
            )
    elif TvHits and MovieHits:
        result = ObjectContainer(title2=u"Search")
        result.add(CreateDirObject("TV Search Hits", 
                                   Callback(BrowseTvHits,url=TvQuery, title2="TV Search Hits")
                                   )
                   )
        result.add(CreateDirObject("Movie Search Hits", 
                                   Callback(BrowseMovies,url=MovieQuery,title2="Movie Search Hits")
                                   )
                   )
        return result
    elif TvHits:
        return BrowseTvHits(TvQuery, title2="TV Search Hits")
    else:
        return BrowseMovies(MovieQuery, title2="Movie Search Hits")

def CreateDirObject(name, key):
    myDir         = DirectoryObject()
    myDir.title   = name
    myDir.key     = key
    myDir.summary = None
    myDir.thumb   = R(ICON)
    myDir.art     = R(ART)
    return myDir


################################################################
# TV
################################################################
def TvShowsList():
    oc = ObjectContainer(title2=L('TV Menu Title'))
    oc.add(DirectoryObject(key=Callback(MostPopularTV,title2=L('Most Popular Menu Title')), title = L('Most Popular Menu Title'), thumb = R('icon-popular.png')))
    oc.add(DirectoryObject(key=Callback(NewTV,title2=L('New Menu Title')), title = L('New Menu Title'), thumb = R('icon-flaged.png')))
    oc.add(DirectoryObject(key=Callback(LastChanceTV,title2=L('Last Chance Menu Title')), title = L('Last Chance Menu Title'), thumb = R('icon-last.png')))
    oc.add(DirectoryObject(key=Callback(ComedyTV,title2=L('Comedy Menu Title')), title = L('Comedy Menu Title'), thumb = R('icon-comedy.png')))
    oc.add(DirectoryObject(key=Callback(RealityTV,title2=L('Reality Menu Title')), title = L('Reality Menu Title'), thumb = R('icon-romance.png')))
    oc.add(DirectoryObject(key=Callback(DocumentaryTV,title2=L('Documentary Menu Title')), title = L('Documentary Menu Title'), thumb = R('icon-bookmark.png')))
    oc.add(DirectoryObject(key=Callback(DramaTV,title2=L('Drama Menu Title')), title = L('Drama Menu Title'), thumb = R('icon-menu.png')))
    oc.add(DirectoryObject(key=Callback(KidsTv,title2=L('Kids Tv Menu Title')), title = L('Kids Tv Menu Title'), thumb = R('icon-kids.png')))
    oc.add(DirectoryObject(key=Callback(SportTv,title2=L('Sport Tv Menu Title')), title = L('Sport Tv Menu Title')))
    if Prefs['site'] == 'SE':
        oc.add(DirectoryObject(key=Callback(Tv3,title2=L('TV3 Menu Title')), title = L('TV3 Menu Title'), thumb = R('icon-tv3.png')))
        oc.add(DirectoryObject(key=Callback(Tv6,title2=L('TV6 Menu Title')), title = L('TV6 Menu Title'), thumb = R('icon-tv6.png')))
        oc.add(DirectoryObject(key=Callback(Tv8,title2=L('TV8 Menu Title')), title = L('TV8 Menu Title'), thumb = R('icon-tv8.png')))
    oc.add(DirectoryObject(key=Callback(AllTv,title2=L('All Tv Menu Title')), title = L('All Tv Menu Title')))
    return oc

def MostPopularTV(title2):
    return BrowseShows(baseUrl() + '/ahah/block/id/17235/title/TV/categoryLevels/2/cacheLifetime/300/group/format/contentType/tv/sorting/most_popular/type/featured', title2)

def AllTv(title2):
    return BrowseShows(baseUrl() + '/ahah/block/id/17235/title/TV/categoryLevels/2/cacheLifetime/300/group/format/contentType/tv/sorting/last_change/type/featured?perpage=1000', title2, True)

def NewTV(title2):
    return BrowseShows(baseUrl() + '/ahah/block/id/17235/title/TV/categoryLevels/2/cacheLifetime/300/group//contentType/tv/sorting/recently_added/type/featured', title2)

def LastChanceTV(title2):
    return BrowseShows(baseUrl() + '/ahah/block/id/17235/title/TV/categoryLevels/2/cacheLifetime/300/group//contentType/tv/sorting/last_change/type/featured', title2)

def ComedyTV(title2):
    return BrowseShows(baseUrl() + '/ahah/block/id/2791/title/TV/categoryLevels/2/cacheLifetime/300/group/format/weight/1/contentType/tv/sorting/most_popular/type/featured?perpage=1000', title2)

def RealityTV(title2):
    return BrowseShows(baseUrl() + '/ahah/block/id/1804/title/TV/categoryLevels/2/cacheLifetime/300/group/format/weight/1/contentType/tv/sorting/most_popular/type/featured?perpage=1000', title2)

def DocumentaryTV(title2):
    return BrowseShows(baseUrl() + '/ahah/block/id/2286/title/TV/categoryLevels/2/cacheLifetime/300/group/format/weight/1/contentType/tv/sorting/most_popular/type/featured?perpage=1000', title2)

def DramaTV(title2):
    return BrowseShows(baseUrl() + '/ahah/block/id/2790/title/TV/categoryLevels/2/cacheLifetime/300/group/format/weight/1/contentType/tv/sorting/most_popular/type/featured?perpage=1000', title2)

def KidsTv(title2):
    return BrowseShows(baseUrl() + '/ahah/block/id/20288/title/TV/categoryLevels/2/cacheLifetime/300/group/format/weight/1/contentType/tv/sorting/last_change/type/featured?perpage=1000', title2, True)

def SportTv(title2):
    return BrowseShows(baseUrl() + '/ahah/placeholders/id/413/title/Sport/categoryLevels/2/cacheLifetime/3/weight/3/contentType/sport/sorting/sport_documentaries/type/featured?perpage=1000', title2, True)

def Tv3(title2):
    return BrowseShows(baseUrl() + '/ahah/block/id/13955/title/TV/categoryLevels/2/cacheLifetime/300/group/format/weight/1/contentType/tv/sorting/last_change/type/featured?perpage=1000', title2, True)

def Tv6(title2):
    return BrowseShows(baseUrl() + '/ahah/block/id/13962/title/TV/categoryLevels/2/cacheLifetime/300/group/format/weight/1/contentType/tv/sorting/last_change/type/featured?perpage=1000', title2, True)

def Tv8(title2):
    return BrowseShows(baseUrl() + '/ahah/block/id/13964/title/TV/categoryLevels/2/cacheLifetime/300/group/format/weight/1/contentType/tv/sorting/last_change/type/featured?perpage=1000', title2, True)

def WarnerTv(title2):
    return BrowseShows(baseUrl() + '/ahah/block/id/9065/title/TV/categoryLevels/2/cacheLifetime/300/group/format/weight/1/contentType/tv/sorting/last_change/type/featured?perpage=1000', title2, True)

###################################
def BrowseShows(url, title2, sort=False):
    oc = ObjectContainer(title2=title2)
    
    for item in HTML.ElementFromURL(url).xpath('//li[@data-product-id]'):

        url = baseUrl() + item.xpath('.//a[@class="title"]')[0].get('href')
        devices = item.get('devices')
        if (devices.find('iosweb') < 0) or "/film/" in url:
            continue
        
        thumb_url = item.xpath('.//img')[0].get('src')
        thumb_url = re.sub("(.+)\\?.*", "\\1", thumb_url)
        thumb_url = thumb_url.replace("Highlight", "Background") 
        url = baseUrl() + item.xpath('.//a[@class="title"]')[0].get('href')
        title =  item.xpath('.//a[@class="title"]')[1].get('title')
        
        summary = ""
        summary_list = item.xpath('.//p[@class="synopsis"]/text()')
        if len(summary_list) > 0:
            summary = summary_list[0]
        oc.add(DirectoryObject(key = Callback(BrowseSeasons, url = url, title2=title, thumb=thumb_url),
                               title = title,
                               summary = summary,
                               thumb = Resource.ContentsOfURLWithFallback(thumb_url,'icon-default.png')))
    if sort:
        oc.objects.sort(key=lambda obj: obj.title)
    return oc

def BrowseSeasons(url, title2, thumb):
    oc = ObjectContainer(title2=title2)
    i          = 0
    for item in HTML.ElementFromURL(url).xpath("//div[@class='media-wrapper seasons']"):
        Active = item.xpath('.//h2[@class="active"]/text()')
        if len(Active) > 0:
            oc.add(DirectoryObject(key   = Callback(BrowseSeason, url = url, title2=title2 + " - " + Active[0]),
                                   title = Active[0],
                                   thumb = thumb))
        else:
            season    = item.xpath('.//h2[@class=""]/text()')[0]
            url       = re.sub("(.+)(/season-[0-9]+/episode-[0-9]+)", "\\1", url)
            seasonUrl = re.sub(".+([0-9]+)", url + "/season-" + "\\1" + "/episode-1", season)
            oc.add(DirectoryObject(key   = Callback(BrowseSeason, url = seasonUrl, title2=title2 + " - " + season),
                                   title = season,
                                   thumb = Resource.ContentsOfURLWithFallback(thumb,'icon-default.png')))
        i = i+1
    if len(oc) > 1:
        oc.objects.sort(key=lambda obj: obj.title)
        oc.objects.reverse()
        return oc
    else:
        return BrowseSeason(url, title2 + " - " + oc.objects[0].title)

###################################
def BrowseSeason(url, title2):
    oc = ObjectContainer(title2=title2)
    
    for item in HTML.ElementFromURL(url).xpath('//div[@class="media-wrapper seasons"]//li[@data-product-id]'):
        thumb_url = item.xpath('.//img')[0].get('src')
        thumb_url = re.sub("(.+)\\?.*", "\\1", thumb_url)
        thumb_url = thumb_url.replace("Highlight", "Background") 
        url = baseUrl() + item.xpath('.//a[@class="title"]')[0].get('href') 
        title =  item.xpath('.//span[@class="seasons"]/text()')
        if len(title) > 0: 
            title = title[0]
        else:
            title = item.xpath('.//a[@class="title"]')[1].get('title')
            
        show_title = item.xpath('.//h3/text()')[0]
        
        # We are using the iOS web interface for streaming so we need to make sure that the streaming is available
        devices = item.get('devices')
        if (devices.find('iosweb') < 0):
            continue
        
        summary = ""
        summary_list = item.xpath('.//p[@class="synopsis"]/text()')
        if len(summary_list) > 0:
            summary = summary_list[0]
        
        oc.add(EpisodeObject(
                           title = title,
                           show = show_title,
                           summary = summary,
                           thumb = Resource.ContentsOfURLWithFallback(thumb_url,'icon-default.png'),
                           url = url))

    sortOnAirData(oc)
    return oc


def BrowseTvHits(url, title2):
    oc = ObjectContainer(title2=title2)
    hits = []
    
    for item in HTML.ElementFromURL(url).xpath('//li[@data-product-id]'):
        rating_key = item.get('data-product-id')
        thumb_url = item.xpath('.//img')[0].get('src')
        thumb_url = re.sub("(.+)\\?.*", "\\1", thumb_url)
        thumb_url = thumb_url.replace("Highlight", "Background") 
        url = baseUrl() + item.xpath('.//a[@class="title"]')[0].get('href')
        
        title =  item.xpath('.//a[@class="title"]')[1].get('title')
        
        # We are using the iOS web interface for streaming so we need to make sure that the streaming is available
        devices = item.get('devices')
        if (len(devices) > 0 and (devices.find('iosweb') < 0)) or myAny(hits, title):
            continue
        hits.append(title)
        summary = ""
        summary_list = item.xpath('.//p[@class="synopsis"]/text()')
        if len(summary_list) > 0:
            summary = summary_list[0]
        oc.add(DirectoryObject(key = Callback(BrowseSeasons, url = url, title2=title, thumb=thumb_url),
                               title = title,
                               summary = summary,
                               thumb = Resource.ContentsOfURLWithFallback(thumb_url,'icon-default.png')))
            
    return oc

def myAny(theList, value):
    for i in theList:
        if i == value:
            return True
    return False

def sortOnAirData(Objects):
    for obj in Objects.objects:
        if obj.originally_available_at == None:
            return Objects.objects.reverse()
    return Objects.objects.sort(key=lambda obj: (obj.originally_available_at,obj.title))

################################################################
# Movies
################################################################
def MoviesList():
    oc = ObjectContainer(title2 = L('Movies Menu Title'))
    oc.add(DirectoryObject(key=Callback(MostPopularMovies,title2=L('Most Popular Menu Title')), title = L('Most Popular Menu Title'), thumb = R('icon-popular.png')))
    oc.add(DirectoryObject(key=Callback(NewMovies,title2=L('New Menu Title')), title = L('New Menu Title'), thumb = R('icon-flaged.png')))
    oc.add(DirectoryObject(key=Callback(LastChanceMovies,title2=L('Last Chance Menu Title')), title = L('Last Chance Menu Title'), thumb = R('icon-last.png')))
    oc.add(DirectoryObject(key=Callback(NordicMovies,title2=L('Nordic Menu Title')), title = L('Nordic Menu Title'), thumb = R('icon-nordic.png')))
    oc.add(DirectoryObject(key=Callback(HDMovies,title2=L('HD Menu Title')), title = L('HD Menu Title')))
    oc.add(DirectoryObject(key=Callback(CriticMovies,title2=L('Critically Acclaimed Menu Title')), title = L('Critically Acclaimed Menu Title'), thumb = R('icon-starred.png')))
    oc.add(DirectoryObject(key=Callback(ActionMovies,title2=L('Action Menu Title')), title = L('Action Menu Title'), thumb = R('icon-action.png')))
    oc.add(DirectoryObject(key=Callback(ThrillerMovies,title2=L('Thriller Menu Title')), title = L('Thriller Menu Title'), thumb = R('icon-personal.png')))
    oc.add(DirectoryObject(key=Callback(ScienceFictionMovies,title2=L('Science Fiction Menu Title')), title = L('Science Fiction Menu Title'), thumb = R('icon-syfy.png')))
    oc.add(DirectoryObject(key=Callback(ComedyMovies,title2=L('Comedy Menu Title')), title = L('Comedy Menu Title'), thumb = R('icon-comedy.png')))
    oc.add(DirectoryObject(key=Callback(RomanceMovies,title2=L('Romance Menu Title')), title = L('Romance Menu Title'), thumb = R('icon-romance.png')))
    oc.add(DirectoryObject(key=Callback(HorrorMovies,title2=L('Horror Menu Title')), title = L('Horror Menu Title'), thumb = R('icon-comedy2.png')))
    oc.add(DirectoryObject(key=Callback(DramaMovies,title2=L('Drama Menu Title')), title = L('Drama Menu Title'), thumb = R('icon-menu.png')))
    oc.add(DirectoryObject(key=Callback(DocumentaryMovies,title2=L('Documentary Menu Title')), title = L('Documentary Menu Title'), thumb = R('icon-bookmark.png')))
    oc.add(DirectoryObject(key=Callback(KidsMovies,title2=L('Kids Menu Title')), title = L('Kids Menu Title'), thumb = R('icon-kids.png')))
    oc.add(DirectoryObject(key=Callback(SportMovies,title2=L('Sport Menu Title')), title = L('Sport Menu Title')))
    oc.add(DirectoryObject(key=Callback(AllMovies,title2=L('All Menu Title')), title = L('All Menu Title')))
    return oc

def MostPopularMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/250/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/most_popular/type/featured', title2)

def AllMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/250/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured?perpage=1000', title2, True)

def NewMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/250/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/recently_added/type/featured', title2)

def LastChanceMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/250/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured', title2)

def NordicMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/6137/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured?perpage=1000', title2)

def CriticMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/27753/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured?perpage=1000', title2)

def HDMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/8704/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured?perpage=1000', title2)

def ThrillerMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/1073/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured?perpage=1000', title2)

def ScienceFictionMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/1167/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured?perpage=1000', title2)

def ComedyMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/1063/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured?perpage=1000', title2)

def RomanceMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/1161/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured?perpage=1000', title2)

def HorrorMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/1069/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured?perpage=1000', title2)

def DramaMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/1059/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured?perpage=1000', title2)

def DocumentaryMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/1306/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured?perpage=1000', title2)

def KidsMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/1264/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured?perpage=1000', title2, True)

def SportMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/placeholders/id/413/title/Sport/categoryLevels/2/cacheLifetime/3/weight/3/contentType/sport/sorting/sport_documentaries/type/featured?perpage=1000', title2, True)

def Sport(title2):
    return BrowseMovies(baseUrl() + '/ahah/placeholders/id/413/title/Sport/categoryLevels/2/cacheLifetime/3/weight/3/contentType/sport/sorting/live_schedule/type/featured/perpage/100000/maxlimit/100000/pricePolicy/all', title2)

def Kids(title2):
    return BrowseMovies(baseUrl() + '/ahah/placeholders/id/0/title/Barn/weight/4/contentType/children/sorting/last_change/type/featured/perpage/100000/maxlimit/100000/getChildrenContent/1', title2, True)

def ActionMovies(title2):
    return BrowseMovies(baseUrl() + '/ahah/block/id/1077/title/Film/categoryLevels/3/cacheLifetime/1000/contentType/movies/sorting/last_change/type/featured', title2)

###################################
def BrowseMovies(url,title2,sort=False):
    oc = ObjectContainer(title2=title2)
    for item in HTML.ElementFromURL(url).xpath('//li[@data-product-id]'):
        rating_key = item.get('data-product-id')
        thumb_url = item.xpath('.//img')[0].get('src')
        thumb_url = re.sub("(.+)\\?.*", "\\1", thumb_url)
        url = baseUrl() + item.xpath('.//a[@class="title"]')[0].get('href')
        
        title =  item.xpath('.//a[@class="title"]')[1].get('title')
        
        # We are using the iOS web interface for streaming so we need to make sure that the streaming is available
        devices = item.get('devices')
        if (len(devices) > 0 and (devices.find('iosweb') < 0)) or '/tv/' in url:
            continue
        
        summary = ""
        summary_list = item.xpath('.//p[@class="synopsis"]/text()')
        if len(summary_list) > 0:
            summary = summary_list[0]
        
        if '-tv-' in item.xpath('.//a[@id]')[0].get('id'):
            oc.add(DirectoryObject(key = Callback(BrowseSeasons, url = url, title2=title, thumb=thumb_url),
                                   title = title,
                                   summary = summary,
                                   thumb = Resource.ContentsOfURLWithFallback(thumb_url,'icon-default.png')))
        else:
            oc.add(MovieObject(
                    title = title,
                    summary = summary,
                    thumb = Resource.ContentsOfURLWithFallback(thumb_url,'icon-default.png'),
                    url = url))
            
    if sort:
        oc.objects.sort(key=lambda obj: obj.title)
    return oc


def baseUrl():
    return 'http://viaplay.' + Prefs['site'].lower()
