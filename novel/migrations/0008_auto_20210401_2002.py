# Generated by Django 3.1.7 on 2021-04-01 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('novel', '0007_auto_20210401_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinformation',
            name='sex',
            field=models.CharField(choices=[('男', '男'), ('女', '女')], default=0, max_length=20, verbose_name='性别'),
        ),
        migrations.AlterField(
            model_name='novelcontent',
            name='novelId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='novel.novelinfo', verbose_name='小说'),
        ),
        migrations.AlterField(
            model_name='novelwordcloud',
            name='novelId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='novel.novelinfo', verbose_name='小说'),
        ),
    ]
