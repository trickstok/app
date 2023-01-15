import os
import markdown
from utils import *


class BasicRoutes(Route):

    def __init__(self, app):
        super().__init__('Basics Trickstok Routes', 'Landing page and blog...')
        self.app = app

    @staticmethod
    def get_article(name):
        post_file = open(f'blog/{name}')
        content = "".join(post_file.readlines()[1:])
        content = markdown.markdown(content)
        post_file.seek(0)
        meta_datas = post_file.readline()
        date, title, cover = meta_datas.split(';')
        day, month, year = date.split('-')
        date = datetime.datetime(year=int(year), month=int(month), day=int(day)).strftime("%A %-d %B")
        return {'title': title, 'date': date, 'content': content, 'cover': cover, 'name': name.split('.')[0]}

    def get_articles(self):
        all_posts = os.listdir('blog/')
        articles = []
        for post in all_posts:
            if os.path.isfile(f'blog/{post}') and post not in 'draft':
                articles.append(self.get_article(post))
        return articles

    def build(self):

        @self.app.route('/prelogin', methods=['POST'])
        def betaAccess():
            form = request.form
            email = form['email']
            content = templates.base.format(email=email, content=templates.betalog)
            mails.add_to_list(email, 'beta', mails.send_mail, args={"to": email, "subject": 'Tu a bien été préinscris !', "content": content})
            return redirect('/')

        @self.app.route('/')
        def presentation():
            return render_template('landing.html')

        @self.app.route('/blog')
        def blog():
            if request.args.get('post') is None:
                articles = self.get_articles()
                return render_template('blog_index.html', articles=articles)
            post = request.args.get('post')
            if os.path.isfile(f'blog/{post}.md'):
                article = self.get_article(f'{post}.md')
            else:
                article = {'title': "Erreur 404; Article introuvable", 'date': "Erreur 404; Article introuvable", "content": "<h1>404 article introuvable</h1><br><p>Cet article à été déplacé ou supprimé...</p>", 'cover': "/static/assets/posts/404.png"}
            articles = self.get_articles()
            return render_template('blog.html', **article, articles=articles)