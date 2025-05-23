from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import current_user, login_required
from datetime import datetime
from ..models import Product, CartItem, Order, OrderItem
from ..forms import DeliveryForm
from ..extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/menu')
def menu():
    products = Product.query.all()
    return render_template('menu.html', products=products)

def get_cart_items():
    if current_user.is_authenticated:
        return CartItem.query.filter_by(user_id=current_user.id).all()
    else:
        cart = session.get('cart', {})
        items = []
        for pid, qty in cart.items():
            product = Product.query.get(pid)
            if product:
                item = {'product': product, 'quantity': qty}
                items.append(item)
        return items

@main_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        db.session.commit()
    else:
        cart = session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
        session['cart'] = cart
        session.modified = True
    flash(f'Added {quantity} "{product.name}" to cart.', 'success')
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
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('main.menu'))

    form = DeliveryForm()
    if form.validate_on_submit():
        delivery_time = form.delivery_time.data
        total = sum(item.product.price * (item.quantity if hasattr(item, 'quantity') else item['quantity']) for item in items)
        order = Order(user_id=current_user.id, delivery_time=delivery_time, total=total)
        db.session.add(order)
        db.session.flush()

        for item in items:
            if isinstance(item, dict):
                pname = item['product'].name
                qty = item['quantity']
                price = item['product'].price
            else:
                pname = item.product.name
                qty = item.quantity
                price = item.product.price

            order_item = OrderItem(
                order_id=order.id,
                product_name=pname,
                quantity=qty,
                price=price
            )
            db.session.add(order_item)

        CartItem.query.filter_by(user_id=current_user.id).delete()

        session.pop('cart', None)

        db.session.commit()
        flash('Order placed successfully!', 'success')
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

