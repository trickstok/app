import smtplib
from email.mime.text import MIMEText

from trickstok import DatabaseObject


class Template:

    base = """
    <body>
    Bonjour {email} 👋 !<br>
    {content}<br>
    Bons tricks,<br>
    L'équipe TricksTok.<br>
    </body>
    """

    betaopen = """
    Enfin, la beta access de TricksTok est là 🤗 ! Tu peux dès maintenant te rendre sur <a href={link}>ce lien</a> pour te créer un compte TricksTok 🤟 ! (Attention ce lien est unique, ne le passe à personne !)<br>
    Nous le savons TricksTok doit être truffé de bug et erreurs, à toi d'en reporter le plus possible sur <a href="http://support.camarm.fr/newissue">support.camarm.fr/newissue</a> en prenant soin de détailler le problème, ou est-il apparu et quand. (Les 10 avec le plus de report auront une petite surprise 🤫)<br>
    Bonne beta-access,<br>
    """

    betalog = """
    Tout d’abord merci de t’être inscris à la beta access 🙏. En mi-janvier (normalement 😅) tu recevra un email contenant tous ce dont tu aura besoin pour accéder et mener à bien ta première expérience sur TricksTok en beta access.<br>
    En attendant, tu peux nous visiter de temps en temps sur YouTube (<a href="https://youtube.com/@trickstok">https://youtube.com/@trickstok</a>) pour savoir où on en est 😊 !<br>
    """

    banned = """
    Bonjour.
    Suite à un non respect du règlement tu as été banni pour la raison suivante:<br>
    <b>{reason}</b>
    <br>
    Ton bannissement est {type}{end}<br> 
    L'équipe TricksTok.
    """


class Mailer(DatabaseObject):

    def __init__(self, user, password, url):
        super().__init__(user, password, url)
        self.mails = self.collection.mailing
        self._from = 'Trickstok <trickstok@camarm.dev>'

    @property
    def total(self):
        return self.mails.count_documents({})

    def add_to_list(self, email, list, callback=None, args={}):
        if self.mails.find_one({'email': email, 'list': list}) is not None:
            self.mails.insert_one({'mail': email, 'list': list})
            if callback is not None:
                callback(**args)

    def get_list_mails(self, list):
        return self.mails.find({'list': list})

    def send_mail(self, to, subject, content):
        server = smtplib.SMTP('192.168.1.141', 25)
        message = MIMEText(content, 'html')
        message['From'] = self._from
        message['Subject'] = subject
        message['To'] = to
        server.send_message(message, 'armand@camponovo.xyz', to)


