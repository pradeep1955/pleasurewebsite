"""# In users/models.py

from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.files import File  # Add this import
from io import BytesIO              # Add this import

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
#    image = models.ImageField(default='image/default.jpg', upload_to='profile_pics')
    image = models.ImageField(default='home/images/default.jpg', upload_to='profile_pics')
    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        # Call the original save method
        super().save(*args, **kwargs)

        # Open the image from the storage (S3)
        # self.image is a file-like object that Pillow can read
        img = Image.open(self.image)

        # Check if the image needs resizing
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)

            # Create an in-memory byte stream to save the resized image
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=95)

            # "Rewind" the stream to the beginning
            thumb_io.seek(0)

            # Save the resized image back to the same storage field
            # We use self.image.name to keep the original filename
            # `save=False` is crucial to prevent an infinite save loop
            self.image.save(self.image.name, File(thumb_io), save=False)

            # Call the original save method again to update the image field
            super().save(update_fields=['image'])
"""
# In users/models.py

from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.files import File
from io import BytesIO

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='myapp/images/default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        # Call the original save method first.
        super().save(*args, **kwargs)

        # --- Start of the robust image processing logic ---
        try:
            # Check if there's an image associated with this profile
            if not self.image:
                return # If no image, do nothing.

            self.image.open() # Open the file stream from S3
            img = Image.open(self.image)

            # Check if the image needs resizing
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)

                thumb_io = BytesIO()
                image_format = 'PNG' if img.mode == 'RGBA' else 'JPEG'
                img.save(thumb_io, format=image_format, quality=95)
                thumb_io.seek(0)

                # Save the resized image back to S3
                self.image.save(self.image.name, File(thumb_io), save=False)

                # Update the database record for the image field
                super().save(update_fields=['image'])

        except FileNotFoundError:
            # This is the crucial part: if the file is not in S3,
            # catch the error, print a warning, and continue without crashing.
            print(f"Warning: Could not find file {self.image.name} in S3 for user {self.user.username}. Skipping image processing.")
            pass # Continue execution gracefully
        # --- End of the robust image processing logic ---
