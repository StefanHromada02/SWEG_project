"""
from django.test import TestCase
from django.contrib.auth.models import User
from domains.posts.serializers import PostSerializer
from domains.posts.models import Post
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


class PostSerializerTests(TestCase):
    #Tests for PostSerializer validation and serialization.#

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='serializer_user', password='password123')

        cls.valid_data = {
            "user": 1,
            "title": "Ein valider Titel",
            "text": "Ein valider Textinhalt."
        }

        cls.invalid_data_no_title = {
            "user": 1,
            "text": "Hier fehlt der Titel."
        }

    def test_serializer_with_valid_data(self):
        #Test deserialization (validation) of correct data.#
        serializer = PostSerializer(data=self.valid_data)
        is_valid = serializer.is_valid()
        
        if not is_valid:
            print(serializer.errors)
        
        self.assertTrue(is_valid)

    def test_serializer_with_invalid_data_missing_title(self):
        #Test serializer detects missing required fields (e.g. title).#
        serializer = PostSerializer(data=self.invalid_data_no_title)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_serializer_with_invalid_data_missing_text(self):
        #Test serializer detects missing text field.#
        data = {"user": 1, "title": "Only Title"}
        serializer = PostSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('text', serializer.errors)

    def test_serializer_read_only_fields(self):
        #Test that image field is read-only and not required on input.#
        data = {
            "user": 1,
            "title": "Test",
            "text": "Content"
        }
        serializer = PostSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_save_creates_post(self):
        #Test that serializer.save() creates a Post object.#
        data = {
            "user": 1,
            "title": "Created Post",
            "text": "Test content"
        }
        serializer = PostSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        post = serializer.save()
        self.assertIsInstance(post, Post)
        self.assertEqual(post.title, "Created Post")
        self.assertEqual(post.user, 1)

    def test_serializer_output_format(self):
        #Test serializer output includes all expected fields.#
        post = Post.objects.create(
            user=1,
            title="Test Post",
            text="Test Content",
            image="posts/test.jpg"
        )
        
        serializer = PostSerializer(post)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('title', data)
        self.assertIn('text', data)
        self.assertIn('image', data)
        self.assertIn('created_at', data)
        self.assertEqual(data['title'], "Test Post")
        self.assertEqual(data['image'], "posts/test.jpg")


class PostSerializerImageValidationTests(TestCase):
    #Tests for image upload validation in serializer.#

    def create_test_image(self, size_mb=1, format='JPEG'):
        #Helper to create test image of specific size.#
        file = BytesIO()
        # Create image with size approximately size_mb MB
        dimension = int((size_mb * 1024 * 1024 / 3) ** 0.5)
        image = Image.new('RGB', (dimension, dimension), color='red')
        image.save(file, format)
        file.seek(0)
        return file

    def test_image_validation_valid_jpeg(self):
        #Test that valid JPEG images are accepted.#
        image_file = self.create_test_image(size_mb=1, format='JPEG')
        uploaded_file = SimpleUploadedFile(
            "test.jpg",
            image_file.read(),
            content_type="image/jpeg"
        )
        
        data = {
            "user": 1,
            "title": "Test",
            "text": "Content",
            "image_file": uploaded_file
        }
        
        serializer = PostSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_image_validation_valid_png(self):
        #Test that valid PNG images are accepted.#
        image_file = self.create_test_image(size_mb=1, format='PNG')
        uploaded_file = SimpleUploadedFile(
            "test.png",
            image_file.read(),
            content_type="image/png"
        )
        
        data = {
            "user": 1,
            "title": "Test",
            "text": "Content",
            "image_file": uploaded_file
        }
        
        serializer = PostSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_image_validation_too_large(self):
        #Test that images larger than 5MB are rejected.#
        # Create 6MB image
        image_file = self.create_test_image(size_mb=6, format='JPEG')
        uploaded_file = SimpleUploadedFile(
            "large.jpg",
            image_file.read(),
            content_type="image/jpeg"
        )
        
        data = {
            "user": 1,
            "title": "Test",
            "text": "Content",
            "image_file": uploaded_file
        }
        
        serializer = PostSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('image_file', serializer.errors)
        self.assertIn('5MB', str(serializer.errors['image_file']))

    def test_image_validation_invalid_format(self):
        #Test that non-image files are rejected.#
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"This is not an image",
            content_type="text/plain"
        )
        
        data = {
            "user": 1,
            "title": "Test",
            "text": "Content",
            "image_file": invalid_file
        }
        
        serializer = PostSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('image_file', serializer.errors)
"""