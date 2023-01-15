from utils import *


class AdminRoutes(Route):

    def __init__(self, app):
        super().__init__('Administration Routes', 'All routes used for administration pages and utilities...')
        self.app = app

    def build(self):
        @self.app.route('/admin')
        def moderation():
            logged, user = is_logged()
            if logged:
                if user['administrator']:
                    success = None
                    if request.args.get('success'):
                        success = True if request.args.get('success') == 'y' else False
                    reports = videos.get_reported()
                    users_nb = users.total
                    videos_nb = videos.total
                    views_nb = videos.total_views
                    reports_nb = videos.total_reports
                    notifs = notifications.get('admins')
                    return auth('admin.html', success=success, reports=reports, users_nb=users_nb, videos_nb=videos_nb, views_nb=views_nb, reports_nb=reports_nb, notifs=notifs)
            return redirect('/log')

        @self.app.route('/admin/users')
        def moderationUsers():
            logged, user = is_logged()
            if logged:
                if user['administrator']:
                    if request.args.get('user') is not None:
                        username = request.args.get('user')
                        user = users.find_by_username(username)
                        return auth('admin_users.html', result=user)
                    return auth('admin_users.html', result=None)
            return redirect('/log')

        @self.app.route('/admin/mails')
        def moderationMails():
            logged, user = is_logged()
            if logged:
                if user['administrator']:
                    campagnes = mailing_lists
                    total = mails.total
                    mailing_campagnes = []
                    for liste in campagnes:
                        emails = list(mails.get_list_mails(liste))
                        mailing_campagnes.append({'name': liste, 'mails': emails, 'number': len(emails)})
                    return auth('admin_mails.html', campagnes=mailing_campagnes, total=total)
            return redirect('/log')

        @self.app.route('/admin/report/<report>', methods=['POST'])
        def moderationDeleteReport(report):
            logged, user = is_logged()
            if logged:
                if user['administrator']:
                    videos.delete_report(report)
                    return redirect('/admin')
            return redirect('/log')

        @self.app.route('/admin/ban', methods=['POST'])
        def banUser():
            logged, user = is_logged()
            if logged:
                if user['administrator']:
                    form = request.form
                    today = datetime.datetime.now()
                    username = form['username']
                    reason = form['reason']
                    user_email = users.find_by_username(username)['email']
                    to = form['to']
                    if to == 'always':
                        date = True
                    elif to == 'week':
                        date = today + datetime.timedelta(weeks=1)
                    elif to == 'month':
                        date = today + datetime.timedelta(weeks=4)
                    elif to == '2month':
                        date = today + datetime.timedelta(weeks=4 * 2)
                    elif to == '5month':
                        date = today + datetime.timedelta(weeks=4 * 5)
                    else:
                        date = True
                    users.ban(username, date, today, user['username'], reason)
                    if date and type(date) == bool:
                        ban_type = 'définitif'
                        after = '.'
                    else:
                        ban_type = 'temporaire'
                        today_string = today.strftime("%A %-d %B")
                        date_string = date.strftime("%A %-d %B")
                        after = f' et durera du {today_string} au {date_string}.'
                    content = templates.banned.format(type=ban_type, end=after, reason=reason)
                    mails.send_mail(user_email, 'TricksTok - Bannissement', content)
                    return redirect('/admin?success=y')
            return redirect('/log')

        @self.app.route('/admin/certify', methods=['POST'])
        def certifyUser():
            logged, user = is_logged()
            if logged:
                if user['administrator']:
                    form = request.form
                    username = form['username']
                    users.certify(username)
                    return redirect('/admin?success=y')
            return redirect('/log')



        @self.app.route('/ask-certify', methods=['POST'])
        def askCertify():
            logged, user = is_logged()
            if logged:
                form = request.form
                why = form['why']
                email = user['email']
                mails.send_mail(email, 'Demande de certification prise en compte', templates.base.format(email=email, content=f"Nous avons bien reçu ta demande de certification pour le compte trickstok @{user['username']}.<br>Nous traiterons ta demande sous peu..."))
                notifications.add('admins', f"Demande de certification de @{user['username']}.\n\n{why}")
                return redirect(f'/home#account')
            return redirect('/log')
