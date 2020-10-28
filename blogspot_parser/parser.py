# -*- coding: utf-8 -*-
# @author: memosarium@gmail.com

import xml.etree.ElementTree 
import sys
import os
import re
import urllib.request
import base64

""" ------------------------------------
"  Парсер xml-файла экспорта blogger
"  -------------------------------------
"  Экспорт содержимого сайта и сохранение 
"  его в виде html-страниц с использованием
"  шаблонов из директорий tmpl
" ---------------------------------- """ 

# Имя xml-файла
XML_FILE = 'blog.xml'

# Текущая конфигурация. От нее зависят настройки экспорта и выбор директории шаблонов
CONFIGURATION = 'custom' # По умолчанию: 'all'

# директория с текущим шаблоном
TMPL_FOLDER = "tmpl_"+CONFIGURATION

# Требуется ли скачивание картинок с сайта blogger и замена их адресов на локальные
SAVE_IMAGES = False

# Режим "генерации документа" - использование упрощенного шаблона (с подчерком _doc),
# отсутствие экспорта картинок и вывода категорий
FOR_DOC = False

# материалы блога идут в обратном порядке
REVERSE_MODE = False

# вырезать теги <img> из материалов блога
NO_IMAGES = False

# название одной из страниц
GALLERY_TITLE = 'Галерея'

# при наличии этих тегов материалы блога сохраняются и добавляются в генерируемый html
# если список пустой - разрешены все теги
ALLOWED_TAGS = []

# при наличии этих тегов материалы не сохраняются
PROHIBED_TAGS = []

# разрешенные для сохранения страницы блога
# если список пустой - разрешены все страницы
ALLOWED_PAGES = []

# выходной файл блога
OUT_FILE = CONFIGURATION+'.html'

# название ссылки "readmore"
READMORE_TEXT = "Дальше »"

if CONFIGURATION == 'custom':  

    ALLOWED_TAGS = []

    FOR_DOC = True

    REVERSE_MODE = True

    NO_IMAGES = True

elif CONFIGURATION == 'site':  

    ALLOWED_TAGS = ['мы']
    PROHIBED_TAGS = ['private']

    ALLOWED_PAGES = [GALLERY_TITLE]

    SAVE_IMAGES = True

if FOR_DOC:
    TMPL_FOLDER+="_doc"    



TMPLS_TYPES = ['post', 'page', 'site', 'gallery', 'img']
READMORE_TAG = "<a name='more'></a>"

PP_TYPES = {
    'post' : 'http://schemas.google.com/blogger/2008/kind#post',
    'page' : 'http://schemas.google.com/blogger/2008/kind#page'
}

TMPLS = {}
ALL_CATS = []
ALL_CATS_NUMS = {}
ALL_IMAGES = {'small' : {}, 'big' : {}}

IMGS_EXTS = ["jpg", "jpeg", "png", "gif"]

MONTH_NAMES = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 
'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
 
#ARCHIVE = {}
ARCHIVE_IMGS = {
    
    "open" : "&#9660;&#160;",
    "closed" : "&#9658;&#160;"
}   

GALLERY_CAT = 'рисунки'


def getTmpls():
    for tmpl_type in TMPLS_TYPES:
        with open(TMPL_FOLDER+'/'+tmpl_type+'.html', encoding='utf-8', mode='r') as fl:
            TMPLS[tmpl_type] = fl.read() 
        fl.close()


def getTag(tag):
    return tag.tag.replace("{http://www.w3.org/2005/Atom}", "")

def process_content(content):
    cnt = content.split(READMORE_TAG)
    if (len(cnt)) > 1:
        content = cnt[0]+"<div class='lucid_more'>"+cnt[1]+"</div><div class='jump-link'><a class='lucid_readmore catsTd' onclick='lucid_more(this)' "
        content += " href='javascript:void(null)'>"
        content += READMORE_TEXT+"</a></div>"

    return content

def lucid_encode(string):
    sr = base64.b64encode (bytes(string, "utf-8")).decode("utf-8").replace(
        "=", "").replace("+", "").replace("/", "")
    return sr[0:30] if len(sr)>30 else sr


def remove_img_tags(data):
    p = re.compile(r'<img.*?/>')
    return p.sub('', data)

def process_images(el):

    if not isinstance(el.text,str):
        return el.text

    if NO_IMAGES:
        return remove_img_tags(el.text)


    pat = re.compile (r'<img [^>]*src="([^"]+)')
    imgs = pat.findall(el.text)

    if imgs:
        for img in imgs:

            if img in ALL_IMAGES['small'].keys():
                img_name = ALL_IMAGES['small'][img]
            else: 
                img_name = img.split('/')[-1]

                while True:
                    if img_name not in ALL_IMAGES['small'].values():
                        ALL_IMAGES['small'][img] = img_name
                        break
                    else:
                        img_name = "0"+img_name

                to_location = "imgs/small/"+urllib.request.unquote(
                        img_name)

                if SAVE_IMAGES:
                    try:
                        urllib.request.urlretrieve(img, to_location)
                    except Exception as e:
                        print("Cannot copy image '"+img+"' to location: "+to_location+ (
                            "\nI/O error({0}): {1}".format(e.errno, e.strerror)))


    pat = re.compile (r'<a [^>]*href="([^"]+)')
    imgs = pat.findall(el.text)

    if imgs:
        for img in imgs:

            go = False
            for ext in IMGS_EXTS:
                if img.lower().endswith("."+ext):
                    go = True

            if not go:
                continue

            if img in ALL_IMAGES['big'].keys():
                img_name = ALL_IMAGES['big'][img]
            else: 
                img_name = img.split('/')[-1]

                while True:
                    if img_name not in ALL_IMAGES['big'].values():
                        ALL_IMAGES['big'][img] = img_name
                        break
                    else:
                        img_name = "0"+img_name

                to_location = "imgs/big/"+urllib.request.unquote(
                        img_name)

                if SAVE_IMAGES:
                    try:
                        urllib.request.urlretrieve(img, to_location)
                    except Exception as e:
                        print("Cannot copy image '"+img+"' to location: "+to_location+ (
                            "\nI/O error({0}): {1}".format(e.errno, e.strerror)))


    txt = el.text

    for imtype, imgs in ALL_IMAGES.items():
        for img, img_name in imgs.items():
            txt = txt.replace(img, "imgs/"+imtype+"/"+img_name)

    return txt


def prepare_archive(entries):

    html = ""
    
    year_prev = ""
    mon_prev = ""

    html += "<div class='psy_archive'>"
    html += "<div class='psy_archive_elems' style='display:none'>"
    html += "<span class='el_open'>"+ARCHIVE_IMGS["open"]+"</span>"
    html += "<span class='el_closed'>"+ARCHIVE_IMGS["closed"]+"</span>"
    html += "</div>"
    html += "<ul class='psy_archive_years'>"

    last_month = False
    last_year = False

    for post in entries['post']:

            year = post['published'][0:4]
            mon  = post['published'][5:7]
            day  = post['published'][8:10]

            if mon != mon_prev or year != year_prev:
                 if year_prev: 
                    html += "</ul></li>"
            

            addclass= ""

            if year != year_prev:
                if year_prev: 
                    html += "</ul></li>"

                opclose = "closed"

                if not last_year:
                    addclass = " class='last_year' "
                    last_year = True
                    opclose = "open"
                

                year_html = "\
                <a class='toggle' href='javascript:void(0)'>\
                    <span class='zippy toggle-"+opclose+"'>"+ARCHIVE_IMGS[opclose]+"</span>\
                </a>\
                <a class='psy_year_title' href='javascript:void(0)' \
                onclick=\"lucid_show_date(this, '"+year+"', 'year')\">"+year+"</a>"

                html += "<li"+addclass+">"+year_html+"<ul class='psy_archive_mons'>"
            

            if mon != mon_prev or year != year_prev:

                opclose = "closed";                   
                if not last_month:
                    addclass= " class='last_month' "
                    last_month = True
                    opclose = "open"
                

                mon_html = "\
                <a class='toggle' href='javascript:void(0)'>\
                    <span class='zippy toggle-"+opclose+"'>"+ARCHIVE_IMGS[opclose]+"</span>\
                </a>\
                <a class='psy_mon_title' href='javascript:void(0)' \
                    onclick=\"lucid_show_date(this, '"+year+"_"+str(int(mon))+"', 'yearmon')\" \
                    >"+MONTH_NAMES[int(mon)-1]+"</a>"             

                html += "<li"+addclass+">"+mon_html+"<ul class='psy_archive_days'>"
            

            html += "<li><a class='catsTd' href='javascript:void(null)' \
            onclick='lucid_show_title(this, \"" + lucid_encode(post['title']) +"\")' \
             >"+post['title']+"</a></li>";

            year_prev = year;
            mon_prev = mon;


    html +=  "</li></ul></li></ul></div>"

    return html   


def write_posts(entries):

    all_cats_tmpl = ""

    html_posts = ""
    tmpl_site = TMPLS['site']

    archive = prepare_archive(entries)

    if REVERSE_MODE:

        entries['post'] = reversed(entries['post'])

    for post in entries['post']:
        tmpl_post = TMPLS['post']

        title_encoded = lucid_encode(post['title'])

        if not FOR_DOC:
            tt = "<a href='javascript:void(null)' onclick='lucid_show_title(this, \""
            tt += title_encoded +"\")'>"+post['title']+"</a>"
            post['title'] = tt

            post['content'] = process_content(post['content'])


        #2011-04-09T15:12:00.000+04:00
        year = post['published'][0:4]
        mon = int(post['published'][5:7])
        day = int(post['published'][8:10])
        time = post['published'][11:16]

        #if year not in ARCHIVE:
        #    ARCHIVE[year] = {}
        #if mon not in ARCHIVE[year]:
        #    ARCHIVE[year][mon] = []

        #ARCHIVE[year][mon].append([post['title'], title_encoded])


        post['published'] = str(day)+" "+MONTH_NAMES[mon-1]+" "+year+" в "+time

        for field in ('title', 'content', 'published'):
            tmpl_post = tmpl_post.replace("%"+field+"%", post[field])

        cat_html = ""
        cat_classes = ""

        if post["cats"] and not FOR_DOC:

            cat_html += "<span class='lucid_cats'>"

            for cat in post["cats"]:

                if cat not in ALL_CATS:
                    ALL_CATS.append(cat)

                if cat not in ALL_CATS_NUMS.keys():
                    ALL_CATS_NUMS[cat] = 1
                else:
                    ALL_CATS_NUMS[cat] += 1

                cat_num = ALL_CATS.index(cat)

                cat_classes += "lucid_cat_"+str(cat_num)+" "

                cat_html += "<a href='javascript:void(null)' "
                cat_html += " onclick='lucid_show_cat(this, "+str(cat_num+1)+")' "
                cat_html += " class='lucid_cat lucid_cat_sel_"+str(cat_num)+"' >"
                cat_html += cat + "</a> "

            cat_html += "</span>"

            cat_classes += " year_"+year+" yearmon_"+year+"_"+str(mon)  
            cat_classes += " title_"+title_encoded

            tmpl_post = tmpl_post.replace("%"+"cats%", cat_html) 
            tmpl_post = tmpl_post.replace("%"+"cat_classes%", cat_classes) 

        html_posts += tmpl_post

    tmpl_site = tmpl_site.replace("%type%", "post") 
    tmpl_site = tmpl_site.replace("%"+"content%", html_posts)

    tmpl_site = tmpl_site.replace("%"+"archive%", archive)
    tmpl_site = tmpl_site.replace("%"+"LUCID_INDEX%", OUT_FILE) 
    

    for cat in sorted(ALL_CATS):

        cat_num = ALL_CATS.index(cat)

        all_cats_tmpl += "<li><a href='javascript:void(null)' "
        all_cats_tmpl += " onclick='lucid_show_cat(this, "+str(cat_num+1)+")' "
        all_cats_tmpl += " class='lucid_cat_side lucid_cat_side_"+str(cat_num)+"' num='"+str(cat_num+1)+"' >"
        all_cats_tmpl += cat + " ("+str(ALL_CATS_NUMS[cat])+")</a></li>"

    tmpl_site = tmpl_site.replace("%"+"allcats%", all_cats_tmpl)

    with open(OUT_FILE, encoding="utf-8", mode='a') as the_file:

        the_file.write(tmpl_site)

    the_file.close()

    return (all_cats_tmpl, archive)


def translit(word):

    legend = {
        ' ':'-', ',':'', 'а':'a', 'б':'b', 'в':'v', 'г':'g', 'д':'d', 'е':'e', 'ё':'yo', 'ж':'zh', 'з':'z', 'и':'i', 'й':'y', 'к':'k', 'л':'l', 'м':'m', 'н':'n', 'о':'o', 'п':'p', 'р':'r', 'с':'s', 'т':'t', 'у':'u', 'ф':'f', 'х':'h', 'ц':'c', 'ч':'ch', 'ш':'sh', 'щ':'shch', 'ъ':'y', 'ы':'y', 'ь':"-", 'э':'e', 'ю':'yu', 'я':'ya', 
        'А':'A', 'Б':'B', 'В':'V', 'Г':'G', 'Д':'D', 'Е':'E', 'Ё':'Yo', 'Ж':'Zh', 'З':'Z', 'И':'I', 'Й':'Y', 'К':'K', 'Л':'L', 'М':'M', 'Н':'N', 'О':'O', 'П':'P', 'Р':'R', 'С':'S', 'Т':'T', 'У':'U', 'Ф':'F', 'Х':'H', 'Ц':'Ts', 'Ч':'Ch', 'Ш':'Sh', 'Щ':'Shch', 'Ъ':'Y', 'Ы':'Y', 'Ь':"-", 'Э':'E', 'Ю':'Yu', 'Я':'Ya', }

    i=0
    for w in word:

        if re.match("^[A-Za-z0-9-]*$", w):
            i+=1
            continue
        w = legend[w] if w in legend.keys() else "-"

        word=word[0: i]+w+word[(i+1):]
        i+= len(w)

    while "--" in word:
        word = word.replace("--","-")

    while word[-1] == "-":
        word = word[0: -1]       
    while word[0] == "-":
        word = word[1:]  

    return word.lower()


def write_pages(entries, all_cats_tmpl, archive):

    for page in entries['page']:

        if ALLOWED_PAGES and page['title'] not in ALLOWED_PAGES:
            continue

        tmpl_site = TMPLS['site']
        tmpl_page = TMPLS['page'] if not 'gallery' in page.keys() else TMPLS['gallery']

        if 'published' in page.keys():
            year = page['published'][0:4]
            mon = int(page['published'][5:7])
            day = int(page['published'][8:10])
            time = page['published'][11:16]

            page['published'] = str(day)+" "+MONTH_NAMES[mon-1]+" "+year+" в "+time

        for field in ('title', 'content', 'published'):
            if field in page.keys():
                tmpl_page = tmpl_page.replace("%"+field+"%", page[field])

        tmpl_site = tmpl_site.replace("%"+"allcats%", all_cats_tmpl)
        tmpl_site = tmpl_site.replace("%type%", "page") 
        tmpl_site = tmpl_site.replace("%"+"content%", tmpl_page)
        tmpl_site = tmpl_site.replace("%"+"archive%", archive)
        tmpl_site = tmpl_site.replace("%"+"LUCID_INDEX%", OUT_FILE) 

        out_file =  translit(page['title'])+"_"+CONFIGURATION+".html"

        if os.path.exists(out_file):
            os.remove(out_file)


        with open(out_file, encoding="utf-8", mode='a') as the_file:

            the_file.write(tmpl_site)

        the_file.close()

def create_gallery(entries):
    
    if not GALLERY_CAT:
        return
    
    page={}
    page['title']=GALLERY_TITLE 
    page['content']=''
    page['gallery']=True

    for post in entries['post']:
        if post["cats"] and GALLERY_CAT in post["cats"]:

            pat = re.compile (r'<img [^>]*src="([^"]+)')
            imgs = pat.findall(post['content'])

            if imgs:
                #print(imgs[0])
                tmpl_img = TMPLS['img']
                tmpl_img = tmpl_img.replace("%"+"title%", post['title'])
                tmpl_img = tmpl_img.replace("%"+"link%", lucid_encode(post['title'])) 
                tmpl_img = tmpl_img.replace("%"+"img_big%", imgs[0].replace('/small/', '/big/')) 
                tmpl_img = tmpl_img.replace("%"+"img%", imgs[0])
                page['content'] += tmpl_img

    entries['page'].append(page)



def write_entries(entries):
    create_gallery(entries)
    (all_cats_tmpl, archive) = write_posts(entries)
    write_pages(entries, all_cats_tmpl, archive)



######################## MAIN ###############################

getTmpls()

if os.path.exists(OUT_FILE):
    os.remove(OUT_FILE)


entries = {'post' : [], 'page' : []}

with open(XML_FILE, encoding='utf-8', mode='r') as xml_file:
    xml_tree = xml.etree.ElementTree.parse(xml_file)
    root = xml_tree.getroot()

    for child in root:
        if getTag(child) != "entry":
            continue

        entry = {'cats' : []}
        ptype = ""

        for child2 in child:

            if getTag(child2) in ("title", "content", "published"):

                entry[getTag(child2)] = child2.text if getTag(child2
                    ) != "content" or (FOR_DOC and not NO_IMAGES) else process_images(child2)
                
            elif getTag(child2) == "category" :

                if child2.attrib and 'term' in child2.attrib:

                    if child2.attrib['term'] == PP_TYPES['post']:
                        ptype = 'post'

                    elif child2.attrib['term'] == PP_TYPES['page']:
                        ptype = 'page'

                    else:
                        entry["cats"].append(child2.attrib['term'])


        if ptype in ('post', 'page'):

            if ptype == "post" and PROHIBED_TAGS and list(set(entry["cats"]) & set(PROHIBED_TAGS)):
                continue

            if ptype == "post" and ALLOWED_TAGS and not list(set(entry["cats"]) & set(ALLOWED_TAGS)):
                continue

            entries[ptype].append(entry)


xml_file.close()

write_entries(entries)