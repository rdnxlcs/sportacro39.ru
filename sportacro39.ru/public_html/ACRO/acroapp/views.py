from django.shortcuts import render

import datetime

import re
import emoji

import json

with open('/home/c/centromebel/acro/public_html/ACRO/acroapp/mss.json', 'r', encoding='utf-8') as file:
  mss = json.load(file)

with open('/home/c/centromebel/acro/public_html/ACRO/acroapp/coaches.json', 'r', encoding='utf-8') as file:
  coaches = json.load(file)

import vk_api

def replace_vk_links(text):
    pattern = r'\[club(\d+)\|([^\]]+)\]'
    
    # Функция замены
    def replacer(match):
        club_id = match.group(1)  # ID клуба
        link_text = match.group(2)  # Текст ссылки
        return f'<a href="https://vk.com/club{club_id}" class="text-blue">{link_text}</a>'

    return re.sub(pattern, replacer, text)

def replace_links(text):
    # Регулярное выражение для поиска ссылок
    url_pattern = r'(https?://[^\s]+)'
    
    # Функция для замены найденных ссылок на <a> теги
    def replace_with_a_tag(match):
        url = match.group(0)
        return f'<a href="{url}" class="text-blue text-decoration-underline" target="_blank">{url}</a>'
    
    # Замена ссылок на <a> теги
    result = re.sub(url_pattern, replace_with_a_tag, text)
    return result

def get_wall(token, group_id, count=100):
  vk_session = vk_api.VkApi(token=token)
  vk = vk_session.get_api()

  try:
    response = vk.wall.get(owner_id=-int(group_id), count=count)
    return response['items']
  except vk_api.exceptions.ApiError as e:
    print(f"Ошибка API: {e}")
    return []
  
def get_video(access_token, owner_id, video_id, access_key):
  vk_session = vk_api.VkApi(token=access_token)
  vk = vk_session.get_api()

  try:
    videos = f"{owner_id}_{video_id}_{access_key}"
      
    response = vk.video.get(videos=videos)
    if response["count"] > 0:
      video_info = response["items"][0]
      return video_info.get("player")  # Прямая ссылка на проигрыватель
    else:
      print("Видео не найдено.")
  except vk_api.exceptions.ApiError as e:
    print(f"Ошибка API: {e}")
    return None

def get_enogh(posts):
  new_posts = []
  texts = []
  for post in [post for post in posts]:
    try:
      photos = [attachment['photo']['orig_photo']['url'] for attachment in post['attachments'] if attachment['type'] == 'photo']
    except:
      photos = []

    try:
      videos = [get_video(access_token, f'-{group_id}', attachment['video']['id'], attachment['video']['access_key']) for attachment in post['attachments'] if attachment['type'] == 'video']
    except:
      videos = []

    try:
      cover = [attachment for attachment in post['attachments'] if 'video' in attachment][0]['video']['photo_1280']
    except:
      cover = ''



    t = {
      'title': delete_emojis(post['text'].split('\n')[0]),
      'text': replace_links(replace_vk_links(delete_emojis(re.sub(r'^( <br> )+', '', ''.join(re.split(r'(\n)', post['text'])[1:]).replace('\n', ' <br> '))))),
      'date': datetime.datetime.fromtimestamp(post['date']),
      'photos': photos,
      'videos': videos,
      'cover': cover
    }
    if post['text']:
      new_posts.append(t)
  return new_posts

def delete_emojis(text):
  return emoji.replace_emoji(text, replace='')

def get_show(posts, text):
  t = []
  for post in posts:
    if text in post['title'] or text in post['text']:
      t.append(post)
  return t
      

access_token = 'vk1.a.YsOUyacskb6Q90oYztrKpxJzENSqM7UqFH30TjWXPuNMp03jZvyDwUbeY7ofghmHULiePuGQYqpnrPoCFFOtduo7vUQQ1H1a-qY-8MK6_LG_ccffBkUCskHwdewg1FT1dE4WS98pQe9LCgCP_yBRSLte-wYz9AMGdk8QxFxXbGraSaCmpBhuMryR9m12XkNuPOLA2z3m0iyVPJNJgD58pQ'
group_id = "19645656"

with open('/home/c/centromebel/acro/public_html/ACRO/acroapp/posts.json', 'r', encoding='utf-8') as file:
  posts = json.load(file)

for post in posts:
  post['date'] = datetime.datetime.strptime(post['date'], "%Y-%m-%d %H:%M:%S")

with open('/home/c/centromebel/acro/public_html/ACRO/acroapp/articles.json', 'r', encoding='utf-8') as file:
  articles = json.load(file)


news_context = {
  'posts': get_show(posts, 'Итоги')[0:3],
  'rec': get_show(posts, 'Показательное выступление')[0],
  'last': posts[0:3],
  'articles': articles,
}

with open('/home/c/centromebel/acro/public_html/ACRO/acroapp/competitions.json', 'r', encoding='utf-8') as file:
  competitions = json.load(file)

with open('/home/c/centromebel/acro/public_html/ACRO/acroapp/region_competitions.json', 'r', encoding='utf-8') as file:
  region_competitions = json.load(file)

with open('/home/c/centromebel/acro/public_html/ACRO/acroapp/members.json', 'r', encoding='utf-8') as file:
  members = json.load(file)

def index(request):
  context = {
    'main_coaches': coaches[:4],
    'coaches': coaches[4:],
    'rec': get_show(posts, 'Показательное выступление')[0],
  }
  return render(request, 'index.html', context)

def news(request):
  return render(request, 'news.html', news_context)

def ms(request):
  return render(request, 'ms.html', {'mss': mss})

def calendar(request):
  return render(request, 'calendar.html',  {'competitions': competitions, 'region_competitions': region_competitions})

def groups(request):
  return render(request, 'groups.html')

def coach(request):
  for i in range(len(coaches)):
    coaches[i]['theme'] = i % 2

  return render(request, 'coach.html', {'coaches': coaches})

def committee(request):
    return render(request, 'committee.html', {'members': members})

def contacts(request):
  return render(request, 'contacts.html')

def article(request, art):
  if art == "coach":
    return render(request, 'article-coach.html', news_context)
  elif art == "groups":
    return render(request, 'article-groups.html', news_context)
  else:
    try:
      news_context['current_article'] = [a for a in articles if a['art'] == art][0]
    except IndexError:
      return render(request, 'article-not-found.html')
    return render(request, 'article.html', news_context)

def wall(request):
  news_context['posts'] = posts
  return render(request, 'wall.html', news_context)

def backup(request):
  pos = get_enogh(get_wall(access_token, group_id))

  with open('/home/c/centromebel/acro/public_html/ACRO/acroapp/posts.json', 'w', encoding='utf-8') as json_file:
    json.dump(pos, json_file, ensure_ascii=False, indent=4, default=str)
    
  return render(request, 'backup.html', {'pos': pos})