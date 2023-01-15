
def start():
    import routes

    app = routes.Flask('Testing Trickstok')
    routes.build(app)
    app.run(host='0.0.0.0')
