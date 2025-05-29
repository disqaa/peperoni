from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import current_user, login_required
from datetime import datetime
from ..models import Product, CartItem, Order, OrderItem, Ingredient, Review
from ..forms import DeliveryForm, ReviewForm
from ..extensions import db
from flask import abort


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route("/menu")
def menu():
    category = request.args.get("category")
    query = Product.query

    if category:
        query = query.filter_by(category=category)
    products = query.all()

    categories = (
        db.session.query(Product.category)
        .distinct()
        .order_by(Product.category)
        .all()
    )
    categories = [c[0] for c in categories]

    # логика любимых категорий
    favorite_products = []
    if current_user.is_authenticated and current_user.favorite_categories:
        fav_list = [c.strip() for c in current_user.favorite_categories.split(',')]
        favorite_products = Product.query.filter(Product.category.in_(fav_list)).limit(6).all()

    return render_template("menu.html",
                           products=products,
                           current_category=category,
                           categories=categories,
                           favorite_products=favorite_products,
                           show_favorites=(category is None))


def get_cart_items():
    items = []
    if current_user.is_authenticated:
        for ci in CartItem.query.filter_by(user_id=current_user.id).all():
            items.append(ci)
    else:
        session_cart = session.get('cart', {})
        for key, qty in session_cart.items():
            pid, ing = key.split('|', maxsplit=1)
            product = Product.query.get(int(pid))
            if product:
                items.append({'product': product, 'quantity': qty, 'chosen_ingredients': ing})
    return items

#логика с картой
@main_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))

    chosen_ingredients = {}
    total_ingredient_price = 0.0
    for ingredient in product.ingredients:
        key = f'ingredient_{ingredient.id}'
        count_str = request.form.get(key)
        if count_str:
            count = int(count_str)
            if count > 0:
                chosen_ingredients[ingredient.name] = count
                total_ingredient_price += ingredient.price * count

    total_price = (product.price + total_ingredient_price) * quantity

    ingredient_str = ", ".join([f"{name} x{qty}" for name, qty in chosen_ingredients.items()])

    cart_item = CartItem(
        user_id=current_user.id,
        product_id=product.id,
        quantity=quantity,
        chosen_ingredients=ingredient_str,
        price=total_price
    )
    db.session.add(cart_item)
    db.session.commit()
    flash('Товар добавлен в корзину.', 'success')
    return redirect(url_for('main.menu'))


@main_bp.route('/cart')
def cart():
    items = get_cart_items()
    return render_template('cart.html', items=items)

@main_bp.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            flash('Item removed from cart.', 'info')
    else:
        cart = session.get('cart', {})
        cart.pop(str(product_id), None)
        session['cart'] = cart
        session.modified = True
        flash('Item removed from cart.', 'info')
    return redirect(url_for('main.cart'))

@main_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = get_cart_items()
    if not items:
        flash('Корзина пуста.', 'warning')
        return redirect(url_for('main.menu'))

    form = DeliveryForm()
    if form.validate_on_submit():
        delivery_time = form.delivery_time.data
        address = form.address.data

        # подсчет суммы
        total = 0
        for item in items:
            if hasattr(item, 'price'):
                total += item.price
            else:
                total += item['product'].price * item['quantity']

        order = Order(user_id=current_user.id,
                      delivery_time=delivery_time,
                      address=address,
                      total=total)
        db.session.add(order)
        db.session.flush()

        for item in items:
            if isinstance(item, dict):
                pname = item['product'].name
                qty = item['quantity']
                unit = item['product'].price
                ingred = item.get('chosen_ingredients', '')
            else:
                pname = item.product.name
                qty = item.quantity
                unit = item.price / qty
                ingred = getattr(item, 'chosen_ingredients', '')

            order_item = OrderItem(
                order_id=order.id,
                product_name=pname,
                quantity=qty,
                price=unit,
                chosen_ingredients=ingred
            )
            db.session.add(order_item)

      #чистка
        CartItem.query.filter_by(user_id=current_user.id).delete()
        session.pop('cart', None)

        db.session.commit()
        flash('Заказ оформлен!', 'success')
        return redirect(url_for('main.orders'))

    return render_template('checkout.html', form=form, items=items)


@main_bp.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

from flask_login import user_logged_in

@user_logged_in.connect
def merge_cart_to_db(sender, user):
    from flask import session
    cart = session.pop('cart', {})
    for pid_str, qty in cart.items():
        pid = int(pid_str)
        cart_item = CartItem.query.filter_by(user_id=user.id, product_id=pid).first()
        if cart_item:
            cart_item.quantity += qty
        else:
            cart_item = CartItem(user_id=user.id, product_id=pid, quantity=qty)
            db.session.add(cart_item)
    db.session.commit()
#основная лоигка с карточками(траблы одни((
@main_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()
    reviews = product.reviews.order_by(Review.timestamp.desc()).all()

    # Обработка отзыва
    if form.validate_on_submit() and current_user.is_authenticated:
        existing_review = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        review = Review(
            rating=int(form.rating.data),
            text=form.text.data,
            user_id=current_user.id,
            product_id=product.id
        )
        db.session.add(review)
        db.session.commit()
        flash('Спасибо за отзыв!', 'success')
        return redirect(url_for('main.product_detail', product_id=product_id))

    # корзина
    if request.method == 'POST' and 'quantity' in request.form:
        quantity = int(request.form.get('quantity', 1))
        ingredients_data = {}

        for key, value in request.form.items():
            if key.startswith('ingredient_'):
                ing_id = int(key.split('_')[1])
                qty = int(value)
                ingredients_data[ing_id] = qty

        added = []
        removed = []
        base_ings = {ing.id: 1 for ing in product.ingredients}

        for ing_id, qty in ingredients_data.items():
            base_qty = base_ings.get(ing_id, 0)
            diff = qty - base_qty
            if diff > 0:
                added.append((ing_id, diff))
            elif diff < 0:
                removed.append((ing_id, -diff))

        added_names = [Ingredient.query.get(ing_id).name + f" +{qty}" for ing_id, qty in added]
        removed_names = [Ingredient.query.get(ing_id).name + f" -{qty}" for ing_id, qty in removed]
        chosen_ingredients_str = ', '.join(added_names + removed_names) if added or removed else 'Стандартный набор'

        total_price = product.price * quantity
        for ing_id, qty in added:
            ing = Ingredient.query.get(ing_id)
            if ing:
                total_price += ing.price * qty * quantity

        if current_user.is_authenticated:
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=product.id,
                quantity=quantity,
                chosen_ingredients=chosen_ingredients_str,
                price=total_price
            )
            db.session.add(cart_item)
            db.session.commit()
        else:
            session_cart = session.get('cart', {})
            key = f"{product.id}|{chosen_ingredients_str}"
            session_cart[key] = session_cart.get(key, 0) + quantity
            session['cart'] = session_cart
            session.modified = True

        flash('Товар добавлен в корзину', 'success')
        return redirect(url_for('main.cart'))

    return render_template('product_detail.html', product=product, form=form, reviews=reviews)
