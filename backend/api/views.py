from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.conf import settings
import sys

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import (
    NewFeedSerializer, ReMassSerializer, RegistrationSerializer,
    DailyGospelSerializer, ProvinceSerializer, AccountSerializer
)
from .producer import publish
from .permissions import IsOwner

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from adminapp.models import NewFeed, Mass, DailyGospel, MassTime, Registration, Province
from core.constants import *
from adminapp.common_messages import *

# Create your viewsets here.


class UserIDView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'userID': request.user.id}, status=HTTP_200_OK)

# API Discription
# Name: getNewFeed
# Url:
# Detail:
# Requirements:
# Output:



class NewFeedViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def getlist(self, request):  # /api/newfeed
        newfeeds = NewFeed.objects.all().order_by('-nf_date_edited')
        serializer = NewFeedSerializer(newfeeds, many=True)
        return Response(serializer.data)

    # /api/newfeed/<str:pk> for more detail.
    def retrieve(self, request, pk=None):
        try:
            newfeed = NewFeed.objects.get(id=pk)
        except:
            print("End retrieve newfeed error: ", sys.exc_info()[0])
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = NewFeedSerializer(newfeed)
        return Response(serializer.data)

# API Discription
# Name: ReMassListViewSet
# Serializer: ListRegistrationMassSerializer
# Url: /api/getMass
# Detail: Get list registration that are available
# Requirements:
# Output:


class ReMassListViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)

    def getlist(self, request):  # /api/getMass
        listmasses = Mass.objects.all().order_by(
            '-mass_date', '-mass_last_updated_date')
        serializer = ReMassSerializer(listmasses, many=True)
        return Response(serializer.data)

    # /api/getMass/<str:pk> for more detail.
    def retrieve(self, request, pk=None):
        mass = Mass.objects.get(id=pk)
        serializer = ReMassSerializer(mass)
        return Response(serializer.data)

# API Discription
# Name: ReMassListViewSet
# Serializer: ListRegistrationMassSerializer
# Url: /api/getMass
# Detail: Get list registration that are available
# Requirements:
# Output:


class MassRegister(viewsets.ViewSet):
    result = {
        STATUS: OK,
        CONTENT: BLANK,
    }
    permission_classes = (IsAuthenticated,)

    # /api/massregister/  get registration history of a user.
    def getlist(self, request, *args, **kwargs):
        try:
            request_user = request.user
            print("Start get "+request_user.username+" registration")
            registers = Registration.objects.filter(
                registration_user=request_user)
            serializer = RegistrationSerializer(registers, many=True)
            print("End get "+request_user.username+" registration")
            return Response(serializer.data)
        except:
            print("End get "+request_user.username +
                  " registration error: ", sys.exc_info()[0])
            return Response({ERROR: SYSTEM_QUERY_0001}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):  # /api/massregister/   create a new registration for a mass
        print("Start create new massregister")
        try:
            from .controller import singleRegister
            request_user = request.user  # get requested user
            # get id of the Mass  (mid)
            mass_id = request.data.get(MASS_ID, None)
            print(request_user.username +
                  " request for registration of the Mass: "+str(mass_id))
            # get user condition confirmation [ucondi]
            user_condition = request.data[USERCONDITION]
            # get single register of a Mass for an User
            register = singleRegister(mass_id, user_condition, request_user)
            # status here maybe approved or waiting
            if register[STATUS] != ERROR:
                serializer = RegistrationSerializer(register[RESULT])
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:                # Register was error
                return Response(register, status=status.HTTP_400_BAD_REQUEST)
        except:
            print("End get user registration error: ", sys.exc_info()[0])
            return Response({ERROR: "System error"}, status=status.HTTP_404_NOT_FOUND)

    # /api/massregister/<int:rid>/   get registration detail of a user.
    def retrieve(self, request, rid=None):
        try:
            request_user = request.user
            registers = Registration.objects.get(
                id=rid, registration_user=request_user)
        except:
            print("End get user registration error: ", sys.exc_info()[0])
            return Response({ERROR: SYSTEM_QUERY_0001}, status=status.HTTP_404_NOT_FOUND)
        serializer = RegistrationSerializer(registers)
        print("End get user registration")
        return Response(serializer.data)

    def update(self, request, pk=None):  # /api/massregister/<str:id>
        print("Start update Province")
        province = Province.objects.get(id=pk)
        serializer = ProvinceSerializer(instance=province, data=request.data)
        if serializer.is_valid():
            serializer.save()
            # publish('Province_updated',serializer.data)
            print("End update Province Successful")
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            print("End update error")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API Discription
# Name: reMassListViewSet
# Serializer: ListRegistrationMassSerializer
# Url:
# Detail: Get list registration that are available
# Requirements:
# Output:

class GospelViewSet(viewsets.ViewSet):

    def getlist(self, request):  # /api/gospel   -- get gospel by next 4 days.
        gospels = DailyGospel.objects.all().order_by('-nf_date_edited')
        serializer = DailyGospelSerializer(gospels, many=True)
        return Response(serializer.data)

    # /api/gospel/<str:pdate> get gospel by date %Y-%m-%d
    def retrieve(self, request, pdate=None):
        date = datetime.today()
        if pdate:
            date = datetime.datetime.strptime(pdate, "%Y-%m-%d").date()
        newfeed = NewFeed.objects.get(daily_gospel_date=date)
        serializer = NewFeedSerializer(newfeed)
        return Response(serializer.data)

# API Discription
# Name: getMassTime
# Serializer: ListRegistrationMassSerializer
# Url:
# Detail: Get list mass schedule
# Requirements:
# Output:



class MassTimeViewSet(viewsets.ViewSet):

    # /api/gospel   -- get all masstime available by country code, default = JP
    def getlist(self, request, country="jp"):
        listmasstime = MassTime.objects.all().order_by('-nf_date_edited')
        serializer = DailyGospelSerializer(listmasstime, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):  # /api/gospel/<str:date> get gospel by date
        pass


# API Template
class ProvinceViewSet(viewsets.ViewSet):
    print("ProvinceViewSet")

    def getlist(self, request):  # /api/province
        provinces = Province.objects.all()
        serializer = ProvinceSerializer(provinces, many=True)
        # publish('Province_gets',serializer.data)
        return Response(serializer.data)

    def create(self, request):  # /api/province
        print("Start create new Province")
        serializer = ProvinceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # publish('Province_created',serializer.data)
            print("End create new Province Successful")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("End create new error")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):  # /api/province/<str:id>
        province = Province.objects.get(id=pk)
        serializer = ProvinceSerializer(province)
        return Response(serializer.data)

    def update(self, request, pk=None):  # /api/province/<str:id>
        print("Start update Province")
        province = Province.objects.get(id=pk)
        serializer = ProvinceSerializer(instance=province, data=request.data)
        if serializer.is_valid():
            serializer.save()
            # publish('Province_updated',serializer.data)
            print("End update Province Successful")
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            print("End update error")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):  # /api/province/<str:id>
        print("Start delete Province")
        if request.user.groups.filter(name=MANAGER).exists():
            province = Province.objects.get(id=pk)
            province.delete()
            # publish('Province_deleted',serializer.data)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "You are not Authorized to do this task"}, status=status.HTTP_400_BAD_REQUEST)

# API Discription
# Name: UserCreate
# Serializer:
# Url:
# Detail:
# Requirements:
# Output:


class UserCreate(viewsets.ViewSet):

    permission_classes = (AllowAny,)

    def create(self, request):  # /api/account/
        print("Start create new account")
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            res = {'status': 'ok',
                   'data': {
                       'token': token.key,
                       'user_id': user.pk,
                       'email': user.email
                   }
                   }
            return Response(res, status=status.HTTP_202_ACCEPTED)
        else:
            res = {
                'status': 'error',
                'message': serializer.errors
            }
            return Response(res, status=status.HTTP_226_IM_USED)

    def requestPassword(self, request, rid=None):
        res = {
            'status': 'error',
            'data': {
                'token': '',
                'user_id': '',
                'email': ''
            },
            'message': ''
        }
        try:
            req_email = request.data.get('email', '')
            user = User.objects.get(email=req_email)
            if user:
                from .controller import userRequestResetPass
                if(userRequestResetPass(user, user.username, req_email)):
                    res['status'] = 'ok'
                    res['message'] = 'Vui lòng kiểm tra hộp thư đến trong email của bạn để đổi mật khẩu.'
                    return Response(res, status=status.HTTP_200_OK)
                else:
                    raise Exception('email', 'Email sending error')
            else:
                res['status'] = ERROR
                res['message'] = 'Email này chưa được đăng ký, xin vui lòng kiểm tra lại'
                return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            print("End request reset password error: ", sys.exc_info()[0])
            res['status'] = ERROR
            res['message'] = SYSTEM_QUERY_0001
            return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def resetPassword(self, request, pk=None):  # /api/province/<str:id>
        res = {
            'status': 'error',
            'data': {
                'token': '',
                'username': '',
                'email': ''
            },
            'message': ''
        }
        try:
            req_usename = request.data.get('username', '')
            req_pass = request.data.get('password', '')
            re_code = request.data.get('code', '')
            user = User.objects.get(username=req_usename)
            if user:
                userprofile = user.userprofile
                if(userprofile.profile_code == re_code):
                    user.set_password(req_pass)
                    user.save()
                    token, created = Token.objects.get_or_create(user=user)
                    res['status'] = 'ok'
                    res['data']['token'] = token.key
                    res['data']['username'] = req_usename
                    res['data']['email'] = user.email
                    res['message'] = 'Đổi mật khẩu thành công'
                    return Response(res, status=status.HTTP_200_OK)
                else:
                    raise Exception('password', 'Mã bảo mật không đúng')
            else:
                raise Exception('password', 'Tài khoản không đúng')
        except:
            print("End request reset password error: ", sys.exc_info()[0])
            res['status'] = ERROR
            res['message'] = sys.exc_info()
            return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# API Discription
# Name: UserCreate
# Serializer:
# Url:
# Detail:
# Requirements:
# Output:


class UserAPIView(APIView):
    pass
