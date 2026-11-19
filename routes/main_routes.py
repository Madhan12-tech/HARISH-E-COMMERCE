
from flask import (
    Blueprint,
    render_template,
    request,
    abort
)

from models import db, Product, Category


main_bp = Blueprint("main", __name__)


# HOME PAGE
@main_bp.route("/")
def home():

    featured_products = Product.query.filter_by(
        active=True,
        featured=True
    ).order_by(Product.created_at.desc()).limit(8).all()

    latest_products = Product.query.filter_by(
        active=True
    ).order_by(Product.created_at.desc()).limit(12).all()

    categories = Category.query.order_by(
        Category.name.asc()
    ).all()

    return render_template(
        "index.html",
        featured_products=featured_products,
        latest_products=latest_products,
        categories=categories
    )


# ALL PRODUCTS
@main_bp.route("/products")
def products():

    search = request.args.get("search", "").strip()
    category_id = request.args.get("category", "").strip()
    sort = request.args.get("sort", "latest")

    query = Product.query.filter_by(active=True)

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%")
        )

    if category_id.isdigit():
        query = query.filter(
            Product.category_id == int(category_id)
        )

    if sort == "price_low":
        query = query.order_by(Product.price.asc())

    elif sort == "price_high":
        query = query.order_by(Product.price.desc())

    elif sort == "name":
        query = query.order_by(Product.name.asc())

    else:
        query = query.order_by(Product.created_at.desc())

    all_products = query.all()

    categories = Category.query.all()

    return render_template(
        "products.html",
        products=all_products,
        categories=categories,
        search=search,
        selected_category=category_id,
        sort=sort
    )


# PRODUCT CATEGORY
@main_bp.route("/category/<int:category_id>")
def category_products(category_id):

    category = db.session.get(Category, category_id)

    if not category:
        abort(404)

    all_products = Product.query.filter_by(
        category_id=category_id,
        active=True
    ).order_by(Product.created_at.desc()).all()

    categories = Category.query.all()

    return render_template(
        "products.html",
        products=all_products,
        categories=categories,
        selected_category=str(category_id),
        category_name=category.name,
        search="",
        sort="latest"
    )


# PRODUCT DETAILS
@main_bp.route("/product/<int:product_id>")
def product_detail(product_id):

    product = Product.query.filter_by(
        id=product_id,
        active=True
    ).first_or_404()

    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.active == True
    ).limit(4).all()

    return render_template(
        "product_detail.html",
        product=product,
        related_products=related_products
    )


# SEARCH PRODUCTS
@main_bp.route("/search")
def search_products():

    search = request.args.get("q", "").strip()

    results = []

    if search:
        results = Product.query.filter(
            Product.name.ilike(f"%{search}%"),
            Product.active == True
        ).all()

    categories = Category.query.all()

    return render_template(
        "products.html",
        products=results,
        categories=categories,
        search=search,
        selected_category="",
        sort="latest"
    )


# ABOUT US
@main_bp.route("/about")
def about():

    return render_template("about.html")


# CONTACT US
@main_bp.route("/contact")
def contact():

    return render_template("contact.html")
