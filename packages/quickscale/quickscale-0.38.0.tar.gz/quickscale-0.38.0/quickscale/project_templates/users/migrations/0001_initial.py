"""Initial migration for CustomUser model.

This is a pre-generated migration file to avoid memory issues during project creation.
Instead of dynamically generating migrations during the build process, we include
pre-created migration files in the templates, which significantly reduces memory usage
and eliminates Out-of-Memory errors that could occur on systems with limited resources.

This consolidated migration includes all CustomUser fields and options.
"""
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    """Initial migration for CustomUser model with all profile fields."""

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(blank=True, help_text='Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, null=True, verbose_name='username')),
                ('email', models.EmailField(error_messages={'unique': 'A user with that email already exists.'}, max_length=254, unique=True, verbose_name='email address')),
                ('bio', models.TextField(blank=True, verbose_name='bio')),
                ('phone_number', models.CharField(blank=True, max_length=20, verbose_name='phone number')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pictures', verbose_name='profile picture')),
                ('job_title', models.CharField(blank=True, max_length=100, verbose_name='job title')),
                ('company', models.CharField(blank=True, max_length=100, verbose_name='company')),
                ('website', models.URLField(blank=True, verbose_name='website')),
                ('location', models.CharField(blank=True, max_length=100, verbose_name='location')),
                ('twitter', models.CharField(blank=True, help_text='Twitter username', max_length=100, verbose_name='twitter')),
                ('linkedin', models.CharField(blank=True, help_text='LinkedIn username', max_length=100, verbose_name='linkedin')),
                ('github', models.CharField(blank=True, help_text='GitHub username', max_length=100, verbose_name='github')),
                ('email_notifications', models.BooleanField(default=True, verbose_name='email notifications')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'app_label': 'users',
            },
        ),
    ] 