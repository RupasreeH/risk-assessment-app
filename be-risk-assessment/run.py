from riskassessmentapp.app import create_app, db

flask_app = create_app()

if __name__ == '__main__':
    with flask_app.app_context():
        db.create_all()
    flask_app.run(host='0.0.0.0', port=5757, debug=True)