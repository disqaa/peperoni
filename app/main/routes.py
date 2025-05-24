from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import current_user, login_required
from datetime import datetime
from ..models import Product, CartItem, Order, OrderItem, Ingredient
from ..forms import DeliveryForm
from ..extensions import db
from flask import abort


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/menu')
def menu():
    products = Product.query.all()
    return render_template('menu.html', products=products)


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


@main_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    #работа с меню здесб, не забыть!!!!!!!!!!!
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))


    chosen_ingredients_str = "Стандартный набор"
    unit_price = product.price
    line_price = unit_price * quantity

    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id,
            product_id=product_id,
            chosen_ingredients=chosen_ingredients_str
        ).first()

        if cart_item:
            cart_item.quantity += quantity
            cart_item.price += line_price
        else:
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity,
                chosen_ingredients=chosen_ingredients_str,
                price=line_price
            )
            db.session.add(cart_item)
        db.session.commit()
    else:
    #лохов в сессию
        cart = session.get('cart', {})
        key = f"{product_id}|{chosen_ingredients_str}"
        cart[key] = cart.get(key, 0) + quantity
        session['cart'] = cart
        session.modified = True

    flash(f'Добавлено: {quantity} × "{product.name}"', 'success')
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

#подсчет суммы, сверять название и типы
        total = sum(
            (item.price if hasattr(item, 'price') else
             item['product'].price * item['quantity'])
            for item in items
        )

        order = Order(user_id=current_user.id,
                      delivery_time=delivery_time,
                      total=total)
        db.session.add(order)
        db.session.flush()

        for item in items:
            if isinstance(item, dict):
                pname = item['product'].name
                qty = item['quantity']
                unit = item['product'].price
                ingred = item['chosen_ingredients']
            else:
                pname = item.product.name
                qty = item.quantity
                unit = item.price / qty
                ingred = item.chosen_ingredients

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

    if request.method == 'POST':
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

    return render_template('product_detail.html', product=product)
