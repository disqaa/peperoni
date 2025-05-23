from app import create_app
from app.extensions import db
from app.models import Product

def seed_products():
    app = create_app()
    with app.app_context():
        if Product.query.first():
            print("Продукты уже есть в базе. Сеединг не нужен.")
            return

        products = [
            Product(name='Pizza 1', description='Classic cheese and tomato pizza', price=7.99),
            Product(name='Pizza 2', description='Pepperoni and cheese', price=8.99),
            Product(name='Pizza 3', description='Ham and pineapple', price=9.49),
            Product(name='Pizza 4', description='Mixed vegetables and cheese', price=8.50),
        ]

        db.session.add_all(products)
        db.session.commit()
        print("Продукты успешно добавлены в базу!")

if __name__ == '__main__':
    seed_products()
