from requests_html import HTMLSession
import requests
import xlwt
from xlwt import Workbook


def get_last_videos(api_key, channel_name):
    session = HTMLSession()
    base_url = f'https://www.youtube.com/c/' + channel_name
    r = session.get(base_url)
    temp = r.html.find('meta[itemprop="channelId"]', first=True)
    if (temp == None):
        raise ValueError("Incorrect channel name!")
    channel_id = temp.attrs['content']

    video_ids = []
    titles = []
    descs = []
    pub_dates = []
    next_page_token = ""
    url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=50&pageToken={next_page_token}"
    response = requests.get(url)
    data = response.json()
    items = data['items']
    data = {}
    for i in range(len(items)):
        video = items[i]
        if (video['id']['kind'] == 'youtube#video'):
            data[video['id']['videoId']] = dict(url=video['id']['videoId'],
                                                title=video['snippet']['title'],
                                                date=video['snippet']['publishedAt'])

    return data


def yt_data(api_key, channel_name):
    session = HTMLSession()
    base_url = f'https://www.youtube.com/c/' + channel_name
    r = session.get(base_url)
    temp = r.html.find('meta[itemprop="channelId"]', first=True)
    if (temp == None):
        raise ValueError("Incorrect channel name!")
    channel_id = temp.attrs['content']

    video_ids = []
    titles = []
    descs = []
    pub_dates = []
    like_count = []
    view_count = []
    comment_count = []
    next_page_token = ""
    while (1):
        url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=50&pageToken={next_page_token}"
        response = requests.get(url)
        data = response.json()
        items = data['items']
        next_page_token = data.get("nextPageToken", None)
        for i in range(len(items)):
            video = items[i]
            if (video['id']['kind'] == 'youtube#video'):
                video_ids.append(video['id']['videoId'])
            titles.append(video['snippet']['title'])
            pub_dates.append(video['snippet']['publishedAt'])
            descs.append(video['snippet']['description'])

        for video_id in video_ids:
            print(video_id)
            try:
                stats = video_data(api_key, video_id)['statistics']
                like_count.append(stats['likeCount'])
                view_count.append(stats['viewCount'])
                comment_count.append(stats['commentCount'])
            except:
                like_count.append(0)
                view_count.append(0)
                comment_count.append(0)

        if next_page_token is None:
            break

    wb = Workbook()

    sheet1 = wb.add_sheet('Sheet 1', cell_overwrite_ok=True)
    bold = xlwt.easyxf('font: bold 1')
    sheet1.write(0, 1, 'title', bold)
    sheet1.write(0, 2, 'videoIDs', bold)
    sheet1.write(0, 3, 'video_description', bold)
    sheet1.write(0, 4, 'published_Date', bold)
    sheet1.write(0, 5, 'likes', bold)
    sheet1.write(0, 6, 'views', bold)
    sheet1.write(0, 7, 'comment', bold)

    all_data = [titles, video_ids, descs, pub_dates, like_count, view_count, comment_count]
    num_videos = len(video_ids)

    for num in range(num_videos):
        sheet1.write(num + 1, 0, num, bold)

    for col in range(1, 8):
        for row in range(num_videos):
            sheet1.write(row + 1, col, all_data[col - 1][row])

    channel_title = items[0]['snippet']['channelTitle'] + '.xls'
    wb.save(channel_title)
    print('обработка завершена')


def video_data(api_key, video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    # likes, views, comments
    # the API no longer gives public access to dislike count since Dec 13

    return data['items'][0]