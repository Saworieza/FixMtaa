from __future__ import absolute_import

import sys

sys.path.insert(0,'../..')

from django.shortcuts import render

# Create your views here.

from proj.query import getRawTweets, getRawTweetsToAnalyze

from rest_framework.views import APIView, Response, status

from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)

from rest_framework import status, exceptions

class GetRawTweets(APIView):
    permission_classes = (AllowAny,)

    def get(self,request,format=None):
        data = getRawTweets()
        return Response({'data': data})
