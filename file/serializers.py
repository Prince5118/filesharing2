from rest_framework import serializers
from file.models import File
import views
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import os

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('name', 'user', 'path', )


class UserSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True)
    class Meta:
        model = User
        fields = ('id','first_name','last_name','username', 'password', 'email', 'files')
        depth = 2

    def create(self, validated_data):
        files_data = validated_data.pop('files')
        user = User.objects.create_user(**validated_data)
        for file_data in files_data:
            name = file_data['name']
            path = file_data['path']
            File.objects.create(user=user, name = name, path=path)
        return user


