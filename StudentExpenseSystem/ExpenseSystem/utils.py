import requests  # Import the requests module
from django.core.files.base import ContentFile

def save_profile_picture_from_url(user, image_url):
    """
    Downloads an image from the given URL and saves it as the user's profile picture.

    :param user: The user instance whose profile picture needs to be updated.
    :param image_url: The URL of the image to be saved.
    """
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            # Extract the file name from the URL
            file_name = image_url.split("/")[-1]
            # Save the image to the user's profile
            user.profile.profile_picture.save(file_name, ContentFile(response.content), save=True)
            return True
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error in save_profile_picture_from_url: {e}")
        return False
