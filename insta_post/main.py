import json
import time
import requests
import openai
from google.cloud import storage
from datetime import datetime
import mysql.connector


# Set your API keys and other configuration variables
# Set the OpenAI API key

openai_api_key = "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"
ig_user_id ="17841463306216373"
access_token='EAAPG3sN8iS8BO0WBVFflll3p5IuS09KZCXquEq5weCPVxqNYqaVvtI2F7rQLL4RhgZBhqj9knGr9nx6NHYnqoDZCV8vxVEYLZBRcSfvNKidb8AeFe5YLnIDBRieRtFz7AD32jdAJL0GKSCHL28lALupV6oZAKUhrMxzOkb1ZAzt7ZCa9GjhgYLEdrLBflNHJqCijxockDZABkeiNcBS4nuwMIZBLopEkBZB0fOchv2'
bucket_name = 'promt-story-photo'


# configration parameter for mysql

db_config = {
    'user': 'wiomsudo',
    'password': 'wiomsudo',
    'host': '34.131.151.203',
    'database': 'wiombot'
}

# inserting the required data to the mysql table

def insert_into_instabot_logs(image_url, creation_time, posted_time, caption):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO instabot_logs (image_url, post_created_at, post_posted_at, caption)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (image_url, creation_time, posted_time, caption))
        print("Success in sending the data to the instabot_logs table")

        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Upload the video or images 
# need to change this function image url depends upon audio/video or images 

def upload_image(image_url, access_token, ig_user_id):
    post_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media"
    payload = {
        'media_type': 'IMAGE',
        'image_url': image_url,  # Ensure this is a valid, publicly accessible URL
        'caption': 'Instagram post',
        'access_token': access_token
    }
    
    response = requests.post(post_url, data=payload)
    print(response.text)
    return json.loads(response.text)


#######   get the status code 
def status_code(ig_container_id, access_token):
    graph_url = 'https://graph.facebook.com/v18.0/'   
    url = graph_url + ig_container_id
    param = {}
    param['access_token'] = access_token
    param['fields'] = 'status_code'
    response = requests.get(url, params=param)
    response = response.json()
    return (response['status_code'])


##  Publish the video / Images

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


# generate stroty from gpt 

def generate_story_from_gpt3(prompt, openai_api_key):
    openai.api_key = openai_api_key
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Write a short story about {prompt}:",
        max_tokens=80
    )
    story = response.choices[0].text.strip()
    print(story)

# Generate image from story
def generate_image(story, openai_api_key):
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json",
    }

    json_data = {
        "prompt": f"a light hearted water color painting depicting this story: {story}",
        "n": 1
    }

    response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=headers,
        json=json_data
    )

    if response.status_code == 200:
        # Extract the URL of the image from the JSON response
        image_url = response.json()['data'][0]['url']
        return image_url
    else:
        raise Exception("Failed to generate image: " + response.text)

def upload_to_gcp_bucket(image_url, destination_blob_name, bucket_name):
    # Initialize the Google Cloud client
    storage_client = storage.Client()

    # Get the bucket object
    bucket = storage_client.bucket(bucket_name)
    
    # Download the image from the OpenAI provided URL
    image_response = requests.get(image_url)
    if image_response.status_code != 200:
        raise Exception("Failed to download image from OpenAI")

    # Create a new blob in the bucket and upload the image data
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(
        image_response.content,
        content_type='image/png'
    )

    # The URL to access the newly uploaded blob
    public_url = f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
    print(f"File {destination_blob_name} uploaded to {bucket_name} with public URL: {public_url}")

    return public_url

# Main logic to combine the functionality
def main():

    # Define your prompts
    prompts = ["A young girl in a slum discovers online graphic design tutorials, opening a window to a career that could break the cycle of poverty for her family.",
                "A father in a middle-class family sets up an online tutoring service for his daughter, bringing quality education right to their living room."
             
                ]

    for prompt in prompts:
        posted_time = datetime.now()

       
        try:   
              # Generate a story for the prompt
            story = generate_story_from_gpt3(prompt, openai_api_key)
            
            # Generate an image for the story
            image_data = generate_image(story, openai_api_key)

            # Record the current time as the time of image creation for GCP bucket
            creation_time = datetime.now()
            creation_time_str = creation_time.strftime('%Y-%m-%d %H:%M:%S')


            # Upload the image to GCP bucket
            destination_blob_name = creation_time.strftime('%Y-%m-%d-%H-%M-%S.png')
            insta_image_url = upload_to_gcp_bucket(image_data, destination_blob_name, bucket_name)
            caption = "instagram second post"

            insert_into_instabot_logs(insta_image_url, creation_time, posted_time, caption)
            
            # Post the image to Instagram
            results = upload_image(insta_image_url, access_token, ig_user_id)
            if 'id' in results:
                ig_container_id = results['id']
                s = status_code(ig_container_id, access_token)

                # Record the current time as the time of posting to Instagram
                posted_time = datetime.now()
                posted_time_str = posted_time.strftime('%Y-%m-%d %H:%M:%S')


                if s == 'FINISHED':
                    print('Image uploaded successfully')
                    publish_video(results, access_token)
                else:
                    print('Image upload failed or is still in progress')
                    time.sleep(30)  # Adjust the sleep time as necessary
                    publish_video(results, access_token)
            
            # Here, you can save creation_time and posted_time to your database
            # along with the other details like image_url and prompt
            
            print(f"Processed prompt: {prompt} | Created at: {creation_time} | Posted at: {posted_time}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()







