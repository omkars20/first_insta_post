import json
import time
import requests




def upload_video(video_url, access_token, ig_user_id):
    post_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media"
    payload = {
        'media_type': 'REELS',
        'video_url': video_url,
        'caption': 'instagram post',
        'access_token': access_token
    }
    
    r = requests.post(post_url, data=payload)
    print(r.text)
    results = json.loads(r.text)
    return (results)



def status_code(ig_container_id, access_token):
    graph_url = 'https://graph.facebook.com/v18.0/'
    url = graph_url + ig_container_id
    param = {}
    param['access_token'] = access_token
    param['fields'] = 'status_code'
    response = requests.get(url, params=param)
    response = response.json()
    return (response['status_code'])




def publish_video(results, access_token):
    if 'id' in results:
        creation_id = results['id']
        second_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media_publish"
        second_payload = {
            'creation_id': creation_id,
            'access_token': access_token
        }
        
        r = requests.post(second_url, data=second_payload)
        print(r.text)
        print("Video published to instagram")
    else:
        print("Video posting is not possible check id ")


ig_user_id ="17841463306216373"
access_token='EAAPG3sN8iS8BO1ZA87dU3X5xZAoC9YNM6IwNRizpBwOz626MZAHPNtcwiLJJgZBBp24qYnv6qVAc12gQwK8YY0p7eeZA2XAjxDQBkuk71jy69dFiQTVLMoDAOxzjbUy42u48Buv6KONOUljO35ihzWZBVRT4hCDBltZBbZCkxMhZBbodUgxBzptpdPdvn9fHvC4vU4U59hGnlXc8KYyvnaCozoseBcbdycVZCJZAlIZD'
video_url='https://media.publit.io/file/6a3c147d-eb43-4f00-9bf8-2b05ba9f4e53.mp4'



results = upload_video(video_url, access_token, ig_user_id)
print('please wait for some time')
print('uploading is going on')
time.sleep(10)

# 2
ig_container_id = results['id']
s = status_code(ig_container_id, access_token)

# 3
if s == 'FINISHED':
    print('video uploaded successfully')
    publish_video(results, access_token)
else:
    print('Video upload failed or is still in progress')
    time.sleep(60)
    publish_video(results,access_token)

