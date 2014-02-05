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

SEASON_TRANSLATED  = ""
EPISODE_TRANSLATED = ""
SEARCH_TRANSLATED  = "Search"

####################################################################################################

# This function is initially called by the PMS framework to initialize the plugin. This includes
# setting up the Plugin static instance along with the displayed artwork.
def Start():

    global SEASON_TRANSLATED
    global EPISODE_TRANSLATED
    global SEARCH_TRANSLATED
    
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

    site = Prefs['site'].lower()
    suffix = "-" + site
    translations = MyJson("https://cms-api.viaplay."+site+"/translations/web")
    for country in translations:
        if suffix in country:
            SEASON_TRANSLATED  = unicode(translations[country]['Season']['text'])
            EPISODE_TRANSLATED = unicode(translations[country]['Episode']['text'])
            SEARCH_TRANSLATED  = unicode(translations[country]['Search']['text'])
            break

# This main function will setup the displayed items.
@handler(VIDEO_PREFIX, L('Title'), ICON, ART)
def MainMenu():

    Login()

    oc = ObjectContainer()
    sections = MyJson(baseUrl())
    for section in sections['_links']['viaplay:sections']:
        if section['type'] == 'vod':
            title = unicode(section['title'])
            oc.add(CreateDirObject(title,
                                   Callback(Section, title2=title, url=section['href']),
                                   )
                   )
    oc.add(CreateDirObject("Logout",
                           Callback(Logout),
                           )
           )
    oc.add(InputDirectoryObject(key = Callback(Search), 
                                title=SEARCH_TRANSLATED, 
                                prompt=SEARCH_TRANSLATED,
                                thumb = R('icon-search.png')
                                )
           )
    oc.add(PrefsObject(title = L('Preferences Menu Title'), thumb = R(ICON_PREFS)))
    return oc

@route('/video/viaplay/section', 'GET')
def Section(title2, url):
    Log("JTDEBUG Section(%s %s)" % (title2, url))
    oc = ObjectContainer(title2=title2)
    sections = MyJson(url)

    if len(sections['_embedded']['viaplay:blocks']) > 0:
        for block in sections['_embedded']['viaplay:blocks']:
            if block["type"] != 'list':
                continue
            title = unicode(block['title'])
            if 'viaplay:seeAll' in block['_links']:
                url = block['_links']['viaplay:seeAll']['href']
            else:
                url = block['_links']['self']['href']
            oc.add(CreateDirObject(title,
                                   Callback(Category, title2=title, url=url, sort=False),
                                   )
                   )

    if ('viaplay:categoryFilters' in sections['_links'] and
        len(sections['_links']['viaplay:categoryFilters']) > 0):
        for category in sections['_links']['viaplay:categoryFilters']:
            title = unicode(category['title'])
            duplicate = False
            for s in oc.objects:
                if title == s.title:
                    duplicate = True
                    continue
            if duplicate:
                continue
            oc.add(CreateDirObject(title,
                                   Callback(Category, title2=title, url=category['href']),
                                   )
                   )
    return oc

@route('/video/viaplay/category', 'GET')
def Category(title2, url, sort = True):
    Log("JTDEBUG Category(%s %s %s)" % (title2, url, sort))
    oc = ObjectContainer(title2=unicode(title2))
    if sort == True:
        next_url = url+"?sort=alphabetical"
    else:
        next_url = url
    return ContinueCategory(oc, next_url)

def ContinueCategory(oc, next_url):
    Log("JTDEBUG ContinueCategory(%s %s)" % (oc, next_url))
    
    try:
        base_url = re.sub("(.+)\\?.*", "\\1", next_url)
        sections = MyJson(next_url)
    except:
        if len(oc) > 0:
            return oc
        else:
            oc.header  = "Sorry"
            oc.message = "HTTP request failed"
            return oc

    ## Check for subcategories
    if ('viaplay:categoryFilters' in sections['_links'] and
        len(sections['_links']['viaplay:categoryFilters']) > 0 and
        base_url + "/" in sections['_links']['viaplay:categoryFilters'][0]['href']):
        return Section(oc.title2, next_url)

    if ('viaplay:blocks' in sections['_embedded'] and 
        len(sections['_embedded']['viaplay:blocks']) > 0):
        for items in sections['_embedded']['viaplay:blocks']:
            if 'next' in sections['_links']:
                next_url = sections['_links']['next']['href']
            elif 'next' in items['_links']:
                next_url = items['_links']['next']['href']
            else:
                next_url = None

            if 'viaplay:products' in items['_embedded']:
                oc = LoopCategory(oc, items['_embedded']['viaplay:products'], next_url)
            # else:
            #     title = items['title']
            #     url   = items['_links']['self']['href']
            #     oc.add(CreateDirObject(title,
            #                            Callback(Category, title2=title, url=url, sort=False),
            #                            )
            #            )
    elif ('viaplay:products' in sections['_embedded'] and
          len(sections['_embedded']['viaplay:products']) > 0):
        if 'next' in sections['_links']:
            next_url = sections['_links']['next']['href']
        else:
            next_url = None
        oc = LoopCategory(oc, sections['_embedded']['viaplay:products'], next_url)
    # elif len(oc) > 0:
    #     return oc
    elif '_embedded' in sections and 'viaplay:errors' in sections['_embedded']:
        oc.header  = "Sorry"
        oc.message = sections['_embedded']['viaplay:errors'][0]['message']
    else:
        oc.header  = "Sorry"
        oc.message = "No programs found."

    return oc

def LoopCategory(oc, items=[], next_url=None):
    Log("JTDEBUG LoopCategory(%s %d %s)" % (oc, len(items), next_url))
    for item in items:
        content = item['content']
        art = R(ART)
        thumb = R(ICON)
        if item['type'] == 'series':
            title   = content['series']['title']
            url     = item['_links']['viaplay:page']['href']
            if 'landscape' in content['images']:
                art   = content['images']['landscape']['url']
                thumb = art
            if 'boxart' in content['images']:
                thumb = content['images']['boxart']['url']
            oc.add(CreateDirObject(title,
                                   Callback(Serie, title2=title, url=url),
                                   thumb,
                                   art,
                                   content['synopsis']
                                   )
                   )
            continue
        # Movie
        # try:
        #     if not "drm" in item['system']['flags']:
        #         oc.add(MakeMovieObject(item))
        # except:
        #     oc.add(MakeMovieObject(item))
        oc.add(MakeMovieObject(item))
    if len(oc) < 30 and next_url != None:
        return ContinueCategory(oc, next_url)
    elif next_url != None:
        oc.add(CreateDirObject("Continue...",
                               Callback(Category, title2=oc.title2, url=next_url, sort=False),
                               ))
    return oc

@route('/video/viaplay/serie', 'GET')
def Serie(title2, url):
    Log("JTDEBUG Serie(%s %s)" % (title2, url))
    oc = ObjectContainer(title2=title2)

    try:
        serie = MyJson(url)
    except:
        oc.header  = "Sorry"
        oc.message = "No Series found."
        return oc

    for season in serie['_embedded']['viaplay:blocks']:
        if season['type'] != 'season-list':
            continue
        title = SEASON_TRANSLATED + " " + season['title']
        try:
            url = season['_links']['self']['href']
        except:
            # Hope for alt below...
            url = []
        # Some links doesn't work for some reason...
        try:
            alt = season['_embedded']['viaplay:products']
        except:
            alt = []
        oc.add(CreateDirObject(title,
                               Callback(Season, title2=title, url=url, alt=alt)
                               )
               )
    if len(oc) > 1:
        oc.objects.sort(key=lambda obj: obj.title)
        oc.objects.reverse()
        return oc
    else:
        return Season(title2=title, url=url, alt=alt)
    return oc

@route('/video/viaplay/season', 'GET')
def Season(title2, url, alt=[]):
    Log("JTDEBUG Season(%s %s %d)" % (title2, url, len(alt)))
    oc = ObjectContainer(title2=unicode(title2))

    try:
        season = MyJson(url)
        episodes = season['_embedded']['viaplay:products']
    except:
        if len(alt) > 0:
            episodes = alt
        else:
            oc.header  = "Sorry"
            oc.message = "No Seasons found."
            return oc

    for episode in episodes:
        content  = episode['content']
        title    = content['series']['episodeTitle']
        oc.add(MakeEpisodeObject(title, episode))
    return oc

@route('/video/viaplay/search', 'GET')
def Search (query):
    Log("JTDEBUG Search (%s)" % query)
    oc = ObjectContainer(title2='Search')
    query = String.Quote(query)
    search = MyJson(baseUrl() + '/search?query=' + query)
    hits = []

    for hit in search['_embedded']['viaplay:blocks']:
        if 'error' in hit:
            continue;
        search_type = hit['_embedded']['viaplay:products'][0]['type']
        if search_type == 'episode' or search_type == 'movie' or search_type == 'sport':
            if 'next' in hit['_links']:
                next_url = hit['_links']['next']['href']
            else:
                next_url = None
            hits.append((hit['title'],search_type, hit['_embedded']['viaplay:products'], next_url))

    if len(hits) == 0:
        return MessageContainer(
            "Search results",
            "Did not find any result for '%s'" % query
            )
    elif len(hits) == 1:
        return BrowseHits(hits[0])
    else:
        for (title, search_type, objects, next_url) in hits:
            oc.add(CreateDirObject(title,
                                   Callback(BrowseHits, hit=(title, search_type, objects, next_url))
                                   )
                   )
        return oc

def BrowseHits(hit):
    (title2, search_type, objects, next_url) = hit
    Log("JTDEBUG BrowseHits(%s %s %d %s)" % (title2, search_type, len(objects), next_url))
    oc = ObjectContainer(title2=title2+" Search hits")
    if search_type == 'episode':
        for episode in objects:
            content        = episode['content']
            if 'episodeNumber' in content['series']:
                episode_number = content['series']['episodeNumber']
            else:
                episodeNumber  = '?'
            title          = unicode(content['title'])
            title = title + " - " + EPISODE_TRANSLATED + " %i" % episode_number
            oc.add(MakeEpisodeObject(title, episode))

    elif search_type == 'movie' or search_type == 'sport':
        for movie in objects:
            oc.add(MakeMovieObject(movie))

    if next_url != None:
        # A bit ugly to re-use the Category function - and episode titles aren't fixed as above
        oc.add(CreateDirObject("Continue...",
                               Callback(Category, title2=title2, url=next_url, sort=False),
                               ))
    return oc

def CreateDirObject(name, key, thumb=R(ICON), art=R(ART), summary=None):
    myDir         = DirectoryObject()
    myDir.title   = name
    myDir.key     = key
    myDir.summary = summary
    myDir.thumb   = thumb
    myDir.art     = art
    return myDir

def sortOnAirData(Objects):
    for obj in Objects.objects:
        if obj.originally_available_at == None:
            return Objects.objects.reverse()
    return Objects.objects.sort(key=lambda obj: (obj.originally_available_at,obj.title))

def baseUrl():
    site = Prefs['site'].lower()
    return 'http://content.viaplay.' + site + '/' + GetDeviceKey(site)

def Login():
    site = Prefs['site'].lower()
    device_key = GetDeviceKey(site)
    api = "https://login.viaplay." + site + "/api"
    url = api + "/persistentLogin/v1?deviceKey=" + device_key + "&returnurl=http%3A%2F%2Fcontent.viaplay." + site + "%2F" + device_key
    try:
        loginPage = MyJson(url)
        loginResult = loginPage['success']
    except:
        loginResult = False
    if loginResult == False:
        email    = String.Quote(Prefs['username'])
        password = String.Quote(Prefs['password'])
        authUrl = api + "/login/v1?deviceKey=" + device_key + "&returnurl=http%3A%2F%2Fcontent.viaplay."+ site + "%2F" + device_key + "&username=" + email + "&password="+ password + "&persistent=true"
        loginPage  = MyJson(authUrl)
        if loginPage['success'] == False:
            raise Exception("Login Failed")

    if Prefs['ageVerification'] == True:
        agePage = MyJson(api + "/ageVerification/v1?deviceKey=" + device_key + "&returnurl=https%3A%2F%2Fcontent.viaplay." + site + "%2F" + device_key)
        if agePage['success'] == False:
            raise Exception("Age Failed")

def Logout():
    site = Prefs['site'].lower()
    url = "https://login.viaplay."+site+"/api/logout/v1?deviceKey=" + GetDeviceKey(site)
    MyJson(url)
    return MessageContainer("Logout", "Logged Out")

def GetDeviceKey(site):
    # return "web-" + site
    return "androidnodrm-" + site
    
def MyJson(url):
    return JSON.ObjectFromURL(re.sub("{\\?dtg}", "", url))

def MakeMovieObject(item=[]):
    art = R(ART)
    thumb = R(ICON)
    content = item['content']
    try:
        duration = int(content['duration']['milliseconds'])
    except:
        duration = None

    if 'landscape' in content['images']:
        art   = content['images']['landscape']['url']
        thumb = art
    if 'boxart' in content['images']:
        thumb = content['images']['boxart']['url']
    return MovieObject(title    = content['title'],
                       summary  = content['synopsis'],
                       thumb    = thumb,
                       art      = art,
                       url      = item['_links']['viaplay:page']['href'],
                       duration = duration
                       )

def MakeEpisodeObject(title, episode=[]):
    art = R(ART)
    thumb = R(ICON)
    content = episode['content']
    if 'landscape' in content['images']:
        art   = content['images']['landscape']['url']
        thumb = art
    if 'boxart' in content['images']:
        thumb = content['images']['boxart']['url']
    air_date = Datetime.ParseDate(episode['system']['availability']['start']).date()
    if 'episodeNumber' in content['series']:
        index = int(content['series']['episodeNumber'])
    else:
        index = None
    return EpisodeObject(title    = unicode(title),
                         show     = unicode(content['series']['title']),
                         summary  = unicode(content['synopsis']),
                         duration = int(content['duration']['milliseconds']),
                         thumb    = thumb,
                         art      = art,
                         url      = episode['_links']['viaplay:page']['href'],
                         index    = index,
                         season   = int(content['series']['season']['seasonNumber']),
                         originally_available_at = air_date
                         )
