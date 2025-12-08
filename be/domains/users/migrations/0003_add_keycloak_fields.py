# Generated migration for User model Keycloak integration

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_create_default_superuser'),
    ]

    operations = [
        # Add new Keycloak fields
        migrations.AddField(
            model_name='user',
            name='keycloak_id',
            field=models.CharField(default='', max_length=255, help_text='Keycloak user ID (sub claim)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default='', max_length=200, help_text='Keycloak username'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(null=True, blank=True),
        ),
        
        # Make study_program optional with default
        migrations.AlterField(
            model_name='user',
            name='study_program',
            field=models.CharField(max_length=200, blank=True, default=''),
        ),
        
        # Add unique constraints
        migrations.AlterField(
            model_name='user',
            name='keycloak_id',
            field=models.CharField(max_length=255, unique=True, db_index=True, help_text='Keycloak user ID (sub claim)'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=200, unique=True, help_text='Keycloak username'),
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['keycloak_id'], name='users_user_keycloak_id_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['username'], name='users_user_username_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['email'], name='users_user_email_idx'),
        ),
    ]
