# Generated by Django 2.0.1 on 2019-11-11 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rbac', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='部门')),
            ],
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=32, verbose_name='主机名')),
                ('ip', models.GenericIPAddressField(verbose_name='IP')),
                ('depart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.Department', verbose_name='归属部门')),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='用户名')),
                ('password', models.CharField(max_length=32, verbose_name='密码')),
                ('email', models.EmailField(max_length=32, verbose_name='邮箱')),
                ('phone', models.CharField(max_length=32, verbose_name='联系方式')),
                ('level', models.IntegerField(choices=[(1, 'T1'), (2, 'T2'), (3, 'T3')], verbose_name='级别')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.Department', verbose_name='部门')),
                ('roles', models.ManyToManyField(blank=True, to='rbac.Role', verbose_name='关联的角色')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
