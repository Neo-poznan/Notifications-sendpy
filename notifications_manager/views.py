from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import View, TemplateView
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import request, response
from django.urls import reverse_lazy

from .validators import csv_file_validator, csv_file_content_validator
from .forms import RecipientsTableForm
from .models import Recipient_contact, Message, SmtpLoginAndServerData
from .kafka import distribute_contact_list_message_and_authentication_data_to_partitions
from .mixins import AppPasswordRequiredMixin
from .smtp import smtp_login_test, smtp_server_test


class IndexView(TemplateView):
    template_name = 'notifications_manager/index.html'


class SetRecipientListView(LoginRequiredMixin, View):
    template_name = 'notifications_manager/set_recipient_list.html'

    def get(self, request: request) -> response:
        '''
        Отображение страницы по get запросу
        '''
        recipient_queryset = Recipient_contact.objects.filter(user=self.request.user)
        return render(request, self.template_name, {'form': RecipientsTableForm, 'recipient_list': recipient_queryset})
    
    def post(self, request: request) -> response:
        '''
        Обработка post запроса с формы принимаем файл - список рассылки
        файл проходит валидацию и мы добавляем контакты в базу
        '''
        csv_file = request.FILES['table_file'].read()
        try:
            csv_file_validator(csv_file)
            csv_file_content_validator(csv_file)
        except ValidationError as error:
            return render(request, self.template_name, {
                'form': RecipientsTableForm,
                'errors': error.message,
                'recipient_list': Recipient_contact.objects.filter(user=self.request.user)
                  })
        Recipient_contact.parse_csv_and_add_contacts_to_database(csv_file, self.request.user)
        recipient_queryset = Recipient_contact.objects.filter(user=self.request.user)
        return render(request, self.template_name, {'form': RecipientsTableForm, 'recipient_list': recipient_queryset})


@login_required
def clear_contact_database_view(request: request) -> response:
    '''
    Очистка базы контактов
    '''
    Recipient_contact.objects.all().delete()

    return HttpResponseRedirect(reverse_lazy('notifications_manager:index'))


class SetAppPasswordView(LoginRequiredMixin, TemplateView):
    template_name = 'notifications_manager/set_app_password.html'

    def get(self, request: request) -> response:
        '''
        Отображение страницы по get запросу
        '''
        smtp_data_row = SmtpLoginAndServerData.objects.filter(user_id=self.request.user).first()
        current_app_password = smtp_data_row.app_password if smtp_data_row else None
        return render(request, self.template_name, {'app_password': current_app_password})
    def post(self, request: request) -> response:
        '''
        Обработка post запроса с формы принимаем пароль проверяем 
        чтобы он совпадал с почтой пользователя и заносим его в базу
        '''
        app_password = request.POST['app_password']
        user = self.request.user
        try:
            smtp_login_test(user.email, app_password)
        except Exception:
            return render(request, self.template_name, {'errors': '''Неверные данные. Почему это могло произойти?
                При копировании пароля когда он высвечивается там ставятся неправильные пробелы не соответствующие кодировке ascii.
                Чтобы это исправить уберите пробелы и проставьте их вручную.'''})
        else:
            SmtpLoginAndServerData.objects.create(user_id=user, email=user.email, app_password=app_password)
            
        return render(request, self.template_name, {'app_password': app_password})
    

class SetMailServer(AppPasswordRequiredMixin, View):
    template_name = 'notifications_manager/set_mail_server.html'

    def get(self, request):
        smtp_data_row = SmtpLoginAndServerData.objects.get(user_id=self.request.user)
        current_server_host = smtp_data_row.mail_server_host
        current_server_port = smtp_data_row.mail_server_port
        return render(request, self.template_name, {'host': current_server_host, 'port': current_server_port})
    
    def post(self, request):
        server_host = request.POST['server_host']
        server_port = request.POST['server_port']
        try:
            smtp_server_test(server_host, server_port)
        except:
            return render(request, self.template_name, context={'message': 'Введите правильные данные сервера'})
        else:
            SmtpLoginAndServerData.set_server_data(self.request.user, server_host, server_port)
            return render(request, self.template_name, {'host': server_host, 'port': server_port})
        
        
class SetMessageView(AppPasswordRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'notifications_manager/set_message.html'

    def get(self, request: request) -> response:
        '''
        Отображение страницы по get запросу
        '''
        current_message = Message.objects.filter(user=self.request.user).first()
        return render(request, self.template_name, {'message': current_message.message_layout, 'message_header': current_message.header})
    
    def post(self, request: request) -> response:
        '''
        Обработка post запроса с формы принимаем сообщение
        и заголовок если они не пустые добавляем их в базу
        '''
        message = request.POST['message']
        message_header = request.POST['message_header']

        if message and message_header:
            Message.reset_user_message(message, message_header, self.request.user)
            new_message = Message.objects.get(user=self.request.user)
            return render(request, self.template_name, {'message': new_message.message_layout, 'message_header': new_message.header})
        return render(request, self.template_name, {'errors': 'Заполните оба поля!'})
    

class SendMessageView(AppPasswordRequiredMixin, LoginRequiredMixin, View):
    template_name = 'notifications_manager/send_message.html'

    def get(self, request: request) -> response:
        '''
        Достаем из базы контакты и сообщение проверяем чтобы они были не пустыми
        и отправляем на рассылку если пользователь пропустил этап с указанием настроек сервера, значит 
        эти поля в json будут иметь пустые значения и воркер будет распознавать это сообщение как то, которое
        нужно отправлять с личной почты. 
        '''
        recipient_list = Recipient_contact.get_contacts_from_database(request.user)
        message_object = Message.objects.get(user=request.user)
        if recipient_list and message_object:
            message = message_object.message_layout
            header = message_object.header
            smtp_data_row = SmtpLoginAndServerData.objects.get(user_id=self.request.user)
            distribute_contact_list_message_and_authentication_data_to_partitions(contact_list=recipient_list, 
                message=message, message_header=header, sender_email=smtp_data_row, app_password=smtp_data_row.app_password,
                server_host=smtp_data_row.mail_server_host, server_port=smtp_data_row.mail_server_port)
            return render(request, 'notifications_manager/success.html')
        return render(request, 'notifications_manager/error_message.html')

