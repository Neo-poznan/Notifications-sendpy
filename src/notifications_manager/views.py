from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import request, response
from django.urls import reverse_lazy

from .forms import RecipientsTableForm
from .mixins import SmtpPasswordRequiredMixin, MessageRequiredMixin
from .repository import RecipientContactsRepository, SmtpCredentialsRepository, MessageRepository
from .use_case import NotificationsManagerUseCase



class IndexView(TemplateView):
    template_name = 'notifications_manager/index.html'

class SetRecipientListView(LoginRequiredMixin, View):
    template_name = 'notifications_manager/set_recipient_list.html'

    def get(self, request: request) -> response:
        '''
        Отображение страницы по get запросу
        '''
        recipient_list = RecipientContactsRepository().get_user_contacts(self.request.user)
        return render(request, self.template_name, {'form': RecipientsTableForm, 'recipient_list': recipient_list})
    
    def post(self, request: request) -> response:
        '''
        Обработка post запроса с формы принимаем файл - список рассылки
        файл проходит валидацию и мы добавляем контакты в базу
        '''
        use_case = NotificationsManagerUseCase()
        csv_file = request.FILES['table_file'].read()
        status = use_case.set_recipient_contacts(csv_file, self.request.user)
        context = {'form': RecipientsTableForm, 'recipient_list': RecipientContactsRepository().get_user_contacts(self.request.user), 
            'errors': status, 'recipient_list': RecipientContactsRepository().get_user_contacts(self.request.user)}
        return render(request, self.template_name, context)


@login_required
def clear_contact_database_view(request: request) -> response:
    '''
    Очистка базы контактов
    '''
    RecipientContactsRepository().delete_user_contacts(request.user)

    return HttpResponseRedirect(reverse_lazy('notifications_manager:index'))
       

class SetSmtpPasswordView(LoginRequiredMixin, TemplateView):
    template_name = 'notifications_manager/set_smtp_password.html'

    def get(self, request: request) -> response:
        '''
        Отображение страницы по get запросу
        '''
        current_app_password = SmtpCredentialsRepository().get_user_smtp_password(self.request.user)
        return render(request, self.template_name, {'app_password': current_app_password})
    def post(self, request: request) -> response:
        '''
        Обработка post запроса с формы принимаем пароль проверяем 
        чтобы он совпадал с почтой пользователя и заносим его в базу
        '''
        app_password = request.POST['smtp_password']
        user = self.request.user
        SmtpCredentialsRepository().create_object_with_user_email_and_password(user, app_password)
        return render(request, self.template_name, {'app_password': app_password})
    

class SetSmtpCredentialsView(SmtpPasswordRequiredMixin,LoginRequiredMixin, View):
    template_name = 'notifications_manager/set_smtp_server.html'

    def get(self, request):
        '''
        Отображение страницы по get запросу
        '''
        smtp_data_object = SmtpCredentialsRepository().get_user_smtp_credentials(self.request.user)
        current_server_host = smtp_data_object.smtp_server_host
        current_server_port = smtp_data_object.smtp_server_port
        return render(request, self.template_name, {'host': current_server_host, 'port': current_server_port})
    
    def post(self, request):
        '''
        Обработка post запроса с формы принимаем данные о сервере
        проверяем их с помощью авторизации на сервере
        заносим данные в базу
        '''
        server_host = request.POST['server_host']
        server_port = request.POST['server_port']
        status = NotificationsManagerUseCase().set_smtp_credentials(self.request.user, server_host, server_port)
        return render(request, self.template_name, {'host': server_host, 'port': server_port, 'errors': status})
         
        
class SetMessageView(SmtpPasswordRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'notifications_manager/set_message.html'

    def get(self, request: request) -> response:
        '''
        Отображение страницы по get запросу
        '''
        message_object = MessageRepository().get_user_message(self.request.user)
        message = message_object.message if message_object else ''
        message_subject = message_object.subject if message_object else ''

        return render(request, self.template_name, {'message': message, 'message_subject': message_subject})
    
    def post(self, request: request) -> response:
        '''
        Обработка post запроса с формы принимаем сообщение
        и заголовок если они не пустые добавляем их в базу
        '''
        message = request.POST['message']
        message_subject = request.POST['message_subject']

        if message and message_subject:
            MessageRepository().create_or_update_user_message(self.request.user, message, message_subject)
            return render(request, self.template_name, {'message': message, 'message_subject': message_subject})
        else:
            return render(request, self.template_name, {'errors': 'Заполните оба поля!'})
    
    
class SendMessageView(MessageRequiredMixin, SmtpPasswordRequiredMixin, LoginRequiredMixin, View):
    template_name = 'notifications_manager/success.html'

    def get(self, request: request) -> response:
        '''
        Достаем из базы контакты и сообщение проверяем чтобы они были не пустыми
        и отправляем на рассылку если пользователь пропустил этап с указанием настроек сервера, значит 
        эти поля в json будут иметь пустые значения и воркер будет распознавать это сообщение как то, которое
        нужно отправлять с личной почты. 
        '''
        NotificationsManagerUseCase().send_notifications(user=self.request.user)
        return render(request, self.template_name)
    
