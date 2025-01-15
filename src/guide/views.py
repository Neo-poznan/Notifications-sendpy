from django.views.generic import TemplateView

class SmtpGuideView(TemplateView):
    template_name = 'guide/smtp_guide.html'


class MailGuideView(TemplateView):
    template_name = 'guide/mail_guide.html'

class QuickStartGuideView(TemplateView):
    template_name = 'guide/quick_start_guide.html'