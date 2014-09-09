#
# http://iphone.cdn.viasat.tv/iphone/008/00866/S86666_premonition_oxsfoewz60oneyvj_iphone.m3u8

# TV3
# http://viastream.viasat.tv/MobileStream/319793
# http://iphone.cdn.viasat.tv/iphone/009/00916/S91659_djurakuten_jhtrvgxbmmxsz44a_iphone.m3u8'
####################################################################################################
import re
import datetime

MyJson       = SharedCodeService.viaplaylib.MyJson
Login        = SharedCodeService.viaplaylib.Login
GetDeviceKey = SharedCodeService.viaplaylib.GetDeviceKey

VIDEO_PREFIX = "/video/viaplay"

ART = 'art-default.jpg'
ICON = 'icon-default.jpg'
ICON_PREFS = 'icon-prefs.png'

IPAD_UA = 'Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X; en-us) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B176 Safari/7534.48.3'

SEASON_TRANSLATED  = ""
EPISODE_TRANSLATED = ""
SEARCH_TRANSLATED  = "Search"

MAX_LEN = 50

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
    contents = MyJson("https://content.viaplay."+site)
    translations = MyJson(contents['_links']['viaplay:translate-content']['href'])
    for country in translations:
        if suffix in country:
            SEASON_TRANSLATED  = unicode(translations[country]['Season']['text'])
            EPISODE_TRANSLATED = unicode(translations[country]['Episode']['text'])
            SEARCH_TRANSLATED  = unicode(translations[country]['Search']['text'])
            break

# This main function will setup the displayed items.
@handler(VIDEO_PREFIX, L('Title'), ICON, ART)
def MainMenu():

    oc = ObjectContainer()
    try:
        Login()
        sections = MyJson(baseUrl())
        for section in sections['_links']['viaplay:sections']:
            if section['type'] == 'vod':
                title = unicode(section['title'])
                oc.add(CreateDirObject(title, Callback(Section, title2=title, url=section['href'])))
        oc.add(CreateDirObject("Re-Login", Callback(ReLogin)))
        oc.add(PrefsObject(title = L('Preferences Menu Title'), thumb=R(ICON_PREFS)))
        oc.add(InputDirectoryObject(key    = Callback(Search), 
                                    title  = SEARCH_TRANSLATED, 
                                    prompt = SEARCH_TRANSLATED,
                                    thumb  = R('icon-search.png')
                                    )
               )
    except:
        oc.message = "Login failed"
        oc.add(CreateDirObject("Login", Callback(MainMenu)))
        oc.add(PrefsObject(title = L('Preferences Menu Title'), thumb = R(ICON_PREFS)))

    return oc

@route('/video/viaplay/section', 'GET')
def Section(title2, url):
    Log("JTDEBUG Section(%s %s)" % (title2, url))
    oc = ObjectContainer(title2=title2)
    sections = MyJson(url)

    if len(sections['_embedded']['viaplay:blocks']) > 0:
        for block in sections['_embedded']['viaplay:blocks']:
            if (block["type"] != 'list' and block["type"] != 'dynamicList') or not '_links' in block:
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

@route('/video/viaplay/category', sort=bool, offset=int)
def Category(title2, url, sort = True, offset=0):
    Log("JTDEBUG Category(%s %s %s %i)" % (title2, url, sort, offset))
    oc = ObjectContainer(title2=unicode(title2))
    if sort == True:
        next_url = url+"?sort=alphabetical"
    else:
        next_url = url
    return ContinueCategory(oc, next_url, offset)

def ContinueCategory(oc, next_url, offset=0):
    Log("JTDEBUG ContinueCategory(%s %s %i)" % (oc, next_url, offset))
    org_url = next_url
    try:
        base_url = re.sub("(.+)\\?.*", "\\1", next_url)
        sections = MyJson(next_url)
    except Exception as e:
        if len(oc) > 0:
            return oc
        else:
            oc.header  = "Sorry"
            oc.message = "%s" % e
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
                oc = LoopCategory(oc, items['_embedded']['viaplay:products'], next_url, org_url, offset)
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
        oc = LoopCategory(oc, sections['_embedded']['viaplay:products'], next_url, org_url, offset)
    # elif len(oc) > 0:
    #     return oc
    elif '_embedded' in sections and 'viaplay:errors' in sections['_embedded']:
        oc.header  = "Sorry"
        oc.message = sections['_embedded']['viaplay:errors'][0]['message']
    else:
        oc.header  = "Sorry"
        oc.message = "No programs found."

    return oc

def LoopCategory(oc, items, next_url, org_url, offset):
    Log("JTDEBUG LoopCategory(%s %d %s %s %i)" % (oc, len(items), next_url, org_url, offset))
    new_offset = offset
    if offset > 0:
        items = items[offset:]
    for item in items:
        new_offset = new_offset+1
        if item['type'] == 'series' and IsNotDrm(item):
            oc.add(MakeSeriesObject(item))
        elif IsNotDrm(item):
            oc.add(MakeMovieObject(item))
        if len(oc) == MAX_LEN:
            break

    if len(oc) < MAX_LEN and next_url != None:
        return ContinueCategory(oc, next_url)
    else:
        any_non_drm = AnyNonDrm(items[(new_offset-offset):], next_url)
        if any_non_drm == 'items':
            next_url = org_url
            pass
        elif any_non_drm == 'next_url':
            new_offset = 0
            pass
        else:
            return oc

        oc.add(NextPageObject(
                key     = Callback(Category, title2=oc.title2, url=next_url, sort=False, offset=new_offset),
                title   = "More...",
                art     = R(ART)
                )
               )
    return oc

@route('/video/viaplay/serie', 'GET')
def Serie(title2, url):
    Log("JTDEBUG Serie(%s %s)" % (title2, url))
    oc = ObjectContainer(title2=unicode(title2))

    try:
        serie = MyJson(url)
    except Exception as e:
        oc.header  = "Sorry"
        oc.message = "No Series found. %s" % e
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
        oc.add(SeasonObject(
                key           = Callback(Season, title2=title, url=url, alt=alt),
                rating_key    = url,
                index         = int(season['title']),
                title         = title,
                show          = title2,
                episode_count = int(season['totalProductCount']),
                thumb         = R(ICON),
                art           = R(ART)
                )
               )
    if len(oc) > 1:
        oc.objects.sort(key = lambda obj: int(re.sub("[^0-9]+","",obj.title)), reverse = True)
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
    except Exception as e:
        if len(alt) > 0:
            episodes = alt
        else:
            oc.header  = "Sorry"
            oc.message = "No Seasons found. %s" % e
            return oc

    for episode in episodes:
        if IsNotDrm(episode):
            content  = episode['content']
            title    = content['series']['episodeTitle']
            oc.add(MakeEpisodeObject(title, episode))
    return oc

def Search (query):
    Log("JTDEBUG Search (%s)" % query)
    oc = ObjectContainer(title2='Search')
    unquotedQuery = query
    query = String.Quote(query)
    search = MyJson(baseUrl() + '/search?query=' + query)
    hits = []

    for hit in search['_embedded']['viaplay:blocks']:
        if 'error' in hit or len(hit['_embedded']['viaplay:products']) == 0:
            continue;
        search_type = hit['_embedded']['viaplay:products'][0]['type']
        if search_type == 'series' or search_type == 'episode' or search_type == 'movie' or search_type == 'sport':
            if 'next' in hit['_links']:
                next_url = hit['_links']['next']['href']
            else:
                next_url = None
            if AnyNonDrm(hit['_embedded']['viaplay:products'], next_url):
                hits.append((hit['title'],search_type, hit['_embedded']['viaplay:products'], next_url))

    if len(hits) == 0:
        return MessageContainer(
            "Search results",
            "Did not find any result for '%s'" % unquotedQuery
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

@route('/video/viaplay/continuesearch', 'GET')
def ContinueSearch (title2, search_type, next_url, oc=None):
    sections = MyJson(next_url)
    if 'next' in sections['_links']:
        next_url = sections['_links']['next']['href']
    else:
        next_url = None
    return BrowseHits((title2, search_type, sections['_embedded']['viaplay:products'], next_url), oc)

def IsNotDrm(item=[]):
    try:
        return not ("drm" in item['system']['flags'])
    except:
        return True

def AnyNonDrm(items, next_url):
    for item in items:
        if IsNotDrm(item):
            return 'items'
    if next_url:
        sections = MyJson(next_url)
        if 'next' in sections['_links']:
            next_url = sections['_links']['next']['href']
        else:
            next_url = None
        if AnyNonDrm(sections['_embedded']['viaplay:products'], next_url):
            return 'next_url'
    return False

@route('/video/viaplay/browsegits', hit=tuple)
def BrowseHits(hit=(), oc=None):
    (title2, search_type, objects, next_url) = hit
    Log("JTDEBUG BrowseHits(%s %s %d %s %r)" % (title2, search_type, len(objects), next_url, type(oc)))
    if not oc:
        oc = ObjectContainer(title2=title2+" Search hits")

    index = 0
    for obj in objects:
        index = index+1
        if IsNotDrm(obj):
            if search_type == 'series':
                oc.add(MakeSeriesObject(obj))
            elif search_type == 'episode':
                content = obj['content']
                title   = unicode(content['title'])
                if 'season' in content['series']:
                    title = title + " - " + SEASON_TRANSLATED + \
                        " %i" % content['series']['season']['seasonNumber']
                if 'episodeNumber' in content['series']:
                    title = title + " - " + EPISODE_TRANSLATED + \
                        " %i" % content['series']['episodeNumber']
                oc.add(MakeEpisodeObject(title, obj))
            elif search_type == 'movie' or search_type == 'sport':
                oc.add(MakeMovieObject(obj))
            if len(oc) == MAX_LEN:
                break

    if len(oc) < MAX_LEN and next_url != None:
        return ContinueSearch(title2, search_type, next_url, oc)
    else:
        rest_objects = objects[index:]
        any_non_drm = AnyNonDrm(rest_objects, next_url)
        if any_non_drm == 'items':
            key = Callback(BrowseHits, hit=(title2, search_type, rest_objects, next_url))
        elif any_non_drm == 'next_url':
            key = Callback(ContinueSearch, title2=title2, search_type=search_type, next_url=next_url)
        else:
            return oc

        oc.add(NextPageObject(
                key   = key,
                title = "More...",
                art   = R(ART)
                )
               )
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

def ReLogin():
    site = Prefs['site'].lower()
    url = "https://login.viaplay."+site+"/api/logout/v1?deviceKey=" + GetDeviceKey(site)
    MyJson(url)
    return MainMenu()

def MakeMovieObject(item=[]):
    art = R(ART)
    thumb = R(ICON)
    content = item['content']
    try:
        duration = int(content['duration']['milliseconds'])
    except:
        duration = None

    if 'images' in content and 'landscape' in content['images']:
        art   = content['images']['landscape']['url']
        thumb = art
    if 'images' in content and 'boxart' in content['images']:
        thumb = content['images']['boxart']['url']

    try:
        year = content['production']['year']
    except:
        year = None

    try:
        countries = [content['production']['country']]
    except:
        countries = []

    genres = []
    if 'viaplay:genres' in item['_links']:
        for genre in item['_links']['viaplay:genres']:
            genre = genres.append(unicode(genre['title']))

    directors = []
    if 'people' in content and 'directors' in content['people']:
        for director in content['people']['directors']:
            directors.append(unicode(director))

    return MovieObject(title          = AddEpgInfo(content['title'], item),
                       summary        = content['synopsis'],
                       thumb          = thumb,
                       art            = art,
                       url            = item['_links']['viaplay:page']['href'],
                       duration       = duration,
                       year           = year,
                       countries      = countries,
                       genres         = genres,
                       directors      = directors,
                       content_rating = content['parentalRating'] if 'parentalRating' in content else None
                       )

def AddEpgInfo(title, item=[]):
    if 'epg' in item:
        start_time = datetime.datetime.strptime(item['epg']['start'], '%Y-%m-%dT%H:%M:%S.000Z')
        end_time = datetime.datetime.strptime(item['epg']['streamEnd'], '%Y-%m-%dT%H:%M:%S.000Z')
        now = datetime.datetime.now()

        if start_time < now and now < end_time:
            epg = "Now"
        elif now > end_time:
            epg = "Ended %s" % end_time.strftime('%H:%M')
        else:
            if start_time.strftime('%Y%m%d') == now.strftime('%Y%m%d'):
                # Today
                epg = start_time.strftime('%H:%M')
            elif (start_time.timetuple().tm_yday - now.timetuple().tm_yday) < 7:
                # Within a week
                epg = start_time.strftime('%A %H:%M')
            else:
                epg = start_time.strftime('%b %d %H:%M')

        return '%s: %s' % (epg, title)
    return title

def MakeSeriesObject(item=[]):
    content = item['content']
    art = R(ART)
    thumb = R(ICON)
    synopsis = None
    title   = content['series']['title']
    url     = item['_links']['viaplay:page']['href']
    if 'images' in content and 'landscape' in content['images']:
        art   = content['images']['landscape']['url']
        thumb = art
    if 'images' in content and 'boxart' in content['images']:
        thumb = content['images']['boxart']['url']
    if 'synopsis' in content:
        synopsis = content['synopsis']
    elif 'synopsis' in content['series']:
        synopsis = content['series']['synopsis']

    genres = []
    if 'viaplay:genres' in item['_links']:
        for genre in item['_links']['viaplay:genres']:
            genre = genres.append(unicode(genre['title']))

    if 'parentalRating' in content:
        content_rating = content['parentalRating']
    else:
        content_rating = None
    
    return TVShowObject(key            = Callback(Serie, title2=title, url=url),
                        rating_key     = url,
                        content_rating = content_rating,
                        genres         = genres,
                        title          = title,
                        thumb          = thumb,
                        art            = art,
                        summary        = synopsis
                        )

def MakeEpisodeObject(title, episode=[]):
    art = R(ART)
    thumb = R(ICON)
    content = episode['content']
    if 'images' in content and 'landscape' in content['images']:
        art   = content['images']['landscape']['url']
        thumb = art
    if 'images' in content and 'boxart' in content['images']:
        thumb = content['images']['boxart']['url']
    air_date = Datetime.ParseDate(episode['system']['availability']['start']).date()
    if 'episodeNumber' in content['series']:
        index = int(content['series']['episodeNumber'])
    else:
        index = None
    try:
        duration = int(content['duration']['milliseconds'])
    except:
        duration = None
    return EpisodeObject(title    = unicode(title),
                         show     = unicode(content['series']['title']),
                         summary  = unicode(content['synopsis']),
                         duration = duration,
                         thumb    = thumb,
                         art      = art,
                         url      = episode['_links']['viaplay:page']['href'],
                         index    = index,
                         season   = int(content['series']['season']['seasonNumber']),
                         originally_available_at = air_date
                         )
