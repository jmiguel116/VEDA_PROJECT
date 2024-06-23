from veda_app import create_app, db
from veda_app.models import YourModel

app = create_app()

with app.app_context():
    data = [
        YourModel(column1='value1', column2='value2'),
        YourModel(column1='value3', column2='value4')
    ]

    db.session.bulk_save_objects(data)
    db.session.commit()
