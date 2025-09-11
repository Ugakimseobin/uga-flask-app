from flask import Flask, render_template, send_file, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
import json
import base64
from config import Config
import os
#from pyngrok import ngrok

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ugahan582818@localhost:3306/ugamedical'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

IMP_KEY = "아임포트 REST API 키"
IMP_SECRET = "아임포트 REST API 시크릿"

db = SQLAlchemy(app)

# -----------------------------
# DB 모델
# -----------------------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    affiliation = db.Column(db.String(100))
    base_address = db.Column(db.String(255))      # 기본주소
    detail_address = db.Column(db.String(255))    # 상세주소
    phone = db.Column(db.String(15))
    # ✅ 약관 동의 컬럼 추가
    agree_terms = db.Column(db.Boolean, default=False, nullable=False)
    agree_privacy = db.Column(db.Boolean, default=False, nullable=False)
    agree_marketing = db.Column(db.Boolean, default=False)

class BannerImage(db.Model):
    __tablename__ = 'banner_images'
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255))
    image_data = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)
    image_data = db.Column(db.LargeBinary) 
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    main_prod = db.Column(db.String(255))

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete="CASCADE"), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    image_id = db.relationship('Product')
    user = db.relationship('User', back_populates='cart_items')
    product = db.relationship('Product')

User.cart_items = db.relationship('CartItem', back_populates='user', cascade='all, delete-orphan')

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))
    delivery_address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    items = db.relationship('OrderItem', back_populates='order', cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete="CASCADE"))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product')

class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.TEXT)
    video_name = db.Column(db.String(255), nullable=False)
    video_data = db.Column(db.LargeBinary, nullable=True)  # MP4 파일 저장, NULL 허용
    video_url = db.Column(db.String(500), nullable=True)   # 유튜브 URL 저장, NULL 허용
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

# -----------------------------
# 사용자 관련 함수
# -----------------------------
def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return True
    return False

def register_user(email, password, name, title=None, affiliation=None, base_address=None, detail_address=None, phone=None,
                  agree_terms=False, agree_privacy=False, agree_marketing=False):
    hashed_password = generate_password_hash(password)
    new_user = User(
        email=email,
        password=hashed_password,
        name=name,
        title=title,
        affiliation=affiliation,
        base_address=base_address,
        detail_address=detail_address,
        phone=phone,
        agree_terms=agree_terms,
        agree_privacy=agree_privacy,
        agree_marketing=agree_marketing
    )
    db.session.add(new_user)
    db.session.commit()

def reset_user_password(email, new_password):
    user = User.query.filter_by(email=email).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()

def get_token():
    url = "https://api.iamport.kr/users/getToken"
    headers = {"Content-Type": "application/json"}
    data = {
        "imp_key": IMP_KEY,
        "imp_secret": IMP_SECRET
    }
    res = requests.post(url, json=data).json()
    return res['response']['access_token']

# -----------------------------
# 배너 관련 함수
# -----------------------------
def get_image_from_db(image_id):
    banner = BannerImage.query.get(image_id)
    if banner:
        return banner.image_data
    return None

# -----------------------------
# 메인 상품 관련 함수
# -----------------------------


# -----------------------------
# 라우트
# -----------------------------
@app.route('/')
def home():
    banners = BannerImage.query.order_by(BannerImage.created_at.asc()).all()
    user_name = session.get('user_name')
    user_title = session.get('user_title')
    show_login = request.args.get("show_login", 0)

    products = Product.query.order_by(Product.created_at.desc()).limit(8).all()

    # ✅ 메인 상품 페이지네이션 (1개씩 출력)
    page = request.args.get('page', 1, type=int)
    per_page = 1
    pagination = Product.query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page)
    products = pagination.items

    videos = Video.query.order_by(Video.created_at.asc()).limit(4).all()

    return render_template(
        'index.html',
        banners=banners,
        videos=videos,
        show_login=show_login,
        user_name=user_name,
        user_title=user_title,
        products=products,
        pagination=pagination
    )

@app.route('/products_page')
def products_page():
    page = request.args.get('page', 1, type=int)
    per_page = 1  # 👉 메인에서 한 번에 보여줄 상품 개수
    pagination = Product.query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page)
    products = pagination.items

    # 상품 카드만 있는 partial 템플릿 반환
    return render_template('partials/main_products.html', products=products, pagination=pagination)

@app.route('/banner/<int:image_id>')
def get_banner_image(image_id):
    image_data = get_image_from_db(image_id)
    if image_data:
        return send_file(BytesIO(image_data), mimetype='image/jpeg')
    return "Image not found", 404

@app.route('/promo_video/<int:video_id>')
def get_promo_video(video_id):
    video = Video.query.get_or_404(video_id)
    return send_file(BytesIO(video.video_data), mimetype='video/mp4')

@app.route('/add_video', methods=['GET', 'POST'])
def add_video():
    if request.method == 'POST':
        description = request.form.get('description')
        video_file = request.files.get('video_file')
        video_url = request.form.get('video_url')

        video_data = video_file.read() if video_file else None

        # video_name 처리
        video_name = request.form.get('video_name')
        if not video_name:
            if video_url:
                # 유튜브 URL에서 ID 추출
                import urllib.parse
                parsed = urllib.parse.urlparse(video_url)
                qs = urllib.parse.parse_qs(parsed.query)
                vid_id = qs.get('v', ['no_id'])[0]
                video_name = f"youtube_{vid_id}"
                # URL 깨끗하게 정리
                video_url = f"https://www.youtube.com/watch?v={vid_id}"
            elif video_file:
                video_name = video_file.filename
            else:
                video_name = "no_name"

        new_video = Video(
            description=description,
            video_name=video_name,
            video_data=video_data,
            video_url=video_url
        )
        db.session.add(new_video)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add_video.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['usermail']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        # 세션 저장
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_title'] = user.title
        session['user_aff'] = user.affiliation
        session['user_base_address'] = user.base_address
        session['user_detail_address'] = user.detail_address

        return jsonify(success=True, message="로그인 성공!")
    else:
        return jsonify(success=False, message="아이디 또는 비밀번호가 올바르지 않습니다.")

@app.route('/my_page')
def my_page():
    if 'user_id' not in session:
        flash('로그인이 필요합니다.', 'warning')
        return redirect(url_for('home', show_login=1))

    user_id = session['user_id']
    user = User.query.get(user_id)
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    return render_template('my_page.html', user=user, orders=orders)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash("로그인이 필요합니다.", "warning")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash("유저를 찾을 수 없습니다.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # 입력값 받기
        name = request.form.get('name')
        title = request.form.get('title')
        affiliation = request.form.get('affiliation')
        base_address = request.form.get('base_address')
        detail_address = request.form.get('detail_address')
        phone = request.form.get('phone')

        # DB 값 업데이트
        user.name = name
        user.title = title
        user.affiliation = affiliation
        user.base_address = base_address
        user.detail_address = detail_address
        user.phone = phone

        db.session.commit()

        # ✅ 세션 값도 갱신 (헤더 즉시 반영)
        session['user_name'] = user.name
        session['user_title'] = user.title
        session['user_aff'] = user.affiliation

        flash("개인정보가 수정되었습니다.", "success")
        return redirect(url_for('my_page'))

    return render_template('edit_profile.html', user=user)


@app.route('/logout')
def logout():
    session.clear()  # ✅ 세션 초기화
    flash('Logged out successfully!', 'info')
    return redirect(url_for('home'))

@app.route('/product')
def product_page():
    if 'user_id' not in session:
        flash('상품 페이지는 로그인 후 이용 가능합니다.', 'warning')
        return render_template("product_notid.html") # 홈으로 가면서 로그인창 자동 열기

    page = request.args.get('page', 1, type=int)  # 현재 페이지 번호
    per_page = 50  # 5열 × 10줄 = 50개씩
    pagination = Product.query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page)
    products = pagination.items

    user_id = session.get('user_id')
    if user_id is not None:
        try:
            user_id = int(user_id)   # 🔥 정수로 변환
        except ValueError:
            user_id = None

    user_aff = session.get('user_aff')

    return render_template(
        'product.html',
        products=products,
        pagination=pagination,
        user_id=user_id,
        user_aff=user_aff
    )

@app.route('/products/<category>')
def product_category(category):
    products = Product.query.filter_by(category=category).all()
    return render_template('product.html', products=products)

# 상품 이미지 불러오기
@app.route('/product_image/<int:product_id>')
def get_product_image(product_id):
    product = Product.query.get_or_404(product_id)
    if product.image_data:
        return send_file(BytesIO(product.image_data), mimetype='image/jpeg')
    return "No image", 404

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    user_id = session.get('user_id')
    user_aff = session.get('user_aff')  # 세션에서 가져오기
    return render_template('product_detail.html', product=product, user_id=user_id, user_aff=user_aff)

# 카트에 상품 추가
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401

    data = request.get_json()
    try:
        product_id = int(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': '잘못된 데이터입니다.'}), 400

    user_id = session['user_id']

    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()

    total_items = db.session.query(db.func.sum(CartItem.quantity)).filter_by(user_id=user_id).scalar() or 0

    return jsonify({'success': True, 'cart_total_items': total_items})

@app.route('/cart_items')
def cart_items():
    if 'user_id' not in session:
        return jsonify([])

    user_id = session['user_id']
    items = CartItem.query.filter_by(user_id=user_id).all()

    result = []
    for item in items:
        # 이미지가 있으면 base64로 변환, 없으면 기본 이미지
        if item.product.image_data:
            import base64
            img_str = base64.b64encode(item.product.image_data).decode('utf-8')
            img_src = f"data:image/png;base64,{img_str}"
        else:
            img_src = url_for('static', filename='images/default.png')

        result.append({
            'cart_id': item.id,
            'name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity,
            'image': img_src
        })

    return jsonify(result)

@app.route('/update_cart/<int:cart_id>', methods=['POST'])
def update_cart(cart_id):
    data = request.get_json()
    quantity = int(data.get('quantity', 1))
    cart_item = CartItem.query.get(cart_id)
    if cart_item:
        cart_item.quantity = quantity
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Cart item not found'}), 404

@app.route('/remove_cart/<int:cart_id>', methods=['POST'])
def remove_cart(cart_id):
    cart_item = CartItem.query.get(cart_id)
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Cart item not found'}), 404

# 상품 구매
@app.route('/checkout_page')
def checkout_page():
    total = request.args.get('total', 0)
    return render_template('checkout.html', total=total)

@app.route('/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    items = data.get('items', [])
    if not items:
        return jsonify({'success': False, 'message': '카트가 비어있습니다.'}), 400

    total_price = sum(item['price'] * item['quantity'] for item in items)
    return jsonify({'success': True, 'total': total_price})

@app.route('/pay', methods=['POST'])
def pay():
    data = request.get_json()
    imp_uid = data.get("imp_uid")   # 결제번호
    merchant_uid = data.get("merchant_uid")

    # 1) 아임포트에서 결제정보 가져오기
    token = get_token()
    url = f"https://api.iamport.kr/payments/{imp_uid}"
    headers = {"Authorization": token}
    res = requests.get(url, headers=headers).json()
    payment_data = res['response']

    # 2) 서버 DB 금액과 비교
    amount = payment_data['amount']
    status = payment_data['status']  # paid, ready 등

    if status == "paid":
        # ✅ 주문 생성
        user_id = session['user_id']
        delivery_address = data.get("buyer_addr", "")
        method = payment_data['pay_method']

        # 총 금액은 장바구니 기준
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        order = Order(
            user_id=user_id,
            total_price=total_price,
            payment_method=method,
            delivery_address=delivery_address
        )
        db.session.add(order)
        db.session.flush()  # order.id 확보

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product.id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.session.add(order_item)

        # 장바구니 비우기
        CartItem.query.filter_by(user_id=user_id).delete()

        db.session.commit()

        return jsonify({"success": True, "message": "결제 성공", "order_id": order.id})
    else:
        return jsonify({"success": False, "message": "결제 실패"})

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session['cart'] = []
    return jsonify({'success': True})

# 결제 후 이동
@app.route('/order_complete/<int:order_id>')
def order_complete(order_id):
    order = Order.query.get_or_404(order_id)
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    return render_template("order_complete.html", order=order, items=order_items)

@app.route('/order_complete_mobile')
def order_complete_mobile():
    imp_uid = request.args.get('imp_uid')
    merchant_uid = request.args.get('merchant_uid')

    if not imp_uid or not merchant_uid:
        return "결제 정보가 부족합니다.", 400

    # 아임포트 결제 정보 확인
    token = get_token()
    url = f"https://api.iamport.kr/payments/{imp_uid}"
    headers = {"Authorization": token}
    res = requests.get(url, headers=headers).json()
    payment_data = res.get('response')

    if not payment_data or payment_data.get('status') != 'paid':
        return "결제 실패", 400

    # 주문 생성
    user_id = session.get('user_id')
    if not user_id:
        return "로그인이 필요합니다.", 401

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    order = Order(
        user_id=user_id,
        total_price=total_price,
        payment_method=payment_data.get('pay_method', ''),
        delivery_address=payment_data.get('buyer_addr', '')
    )
    db.session.add(order)
    db.session.flush()

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product.id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.session.add(order_item)

    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    # 모바일 완료 페이지
    return render_template('order_complete.html', order=order, items=order.items)

# 상품 추가
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_file = request.files['image']
        image_data = image_file.read() if image_file else None

        new_product = Product(
            name=name,
            description=description,
            price=float(price),
            image_data=image_data
        )
        db.session.add(new_product)
        db.session.commit()
        flash('상품이 추가되었습니다!', 'success')
        return redirect(url_for('product_page'))

    return render_template('add_product.html')

# 상품 수정
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        image_file = request.files['image']
        if image_file:
            product.image_data = image_file.read()
        db.session.commit()
        flash('상품이 수정되었습니다!', 'success')
        return redirect(url_for('product_page'))

    return render_template('edit_product.html', product=product)

# 상품 삭제
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('상품이 삭제되었습니다!', 'success')
    return redirect(url_for('product_page'))

#회원가입
@app.route('/sign_up_terms', methods=['GET', 'POST'])
def sign_up_terms():
    if request.method == 'POST':
        agree_terms = request.form.get('agree_terms')
        agree_privacy = request.form.get('agree_privacy')
        agree_marketing = request.form.get('agree_marketing', 'off')  # 선택적

        if not agree_terms or not agree_privacy:
            flash("필수 약관에 모두 동의해야 회원가입이 가능합니다.", "danger")
            return redirect(url_for('sign_up_terms'))

        # 세션에 동의 여부 저장
        session['agree_terms'] = True
        session['agree_privacy'] = True
        session['agree_marketing'] = (agree_marketing == 'on')

        return redirect(url_for('sign_up'))

    return render_template('sign_up_terms.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    # 약관 동의 안 한 상태라면 접근 금지
    if not session.get('agree_terms') or not session.get('agree_privacy'):
        flash("회원가입을 위해 필수 약관에 동의해야 합니다.", "warning")
        return redirect(url_for('sign_up_terms'))

    if request.method == 'POST':
        # 여기서 form 데이터 처리
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        title = request.form.get('title')
        affiliation = request.form.get('affiliation')
        base_address = request.form['base_address']
        detail_address = request.form['detail_address']
        phone = request.form.get('phone')

        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.', 'danger')
            return redirect(url_for('sign_up'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('이미 가입된 이메일입니다.', 'danger')
            return redirect(url_for('sign_up'))

        try:
            register_user(
                email=email,
                password=password,
                name=name,
                title=title,
                affiliation=affiliation,
                base_address=base_address,
                detail_address=detail_address,
                phone=phone,
                agree_terms=session.get('agree_terms'),
                agree_privacy=session.get('agree_privacy'),
                agree_marketing=session.get('agree_marketing')
            )
            # 세션 초기화
            session.pop('agree_terms', None)
            session.pop('agree_privacy', None)
            session.pop('agree_marketing', None)

            return render_template("signup_popup.html")
        except Exception as e:
            db.session.rollback()
            return f'에러 발생: {str(e)}', 500

    return render_template('sign_up.html')

@app.route('/reset_password', methods=['POST'])
def reset_password_route():
    email = request.form['usermail']
    new_password = request.form['new_password']
    reset_user_password(email, new_password)
    flash('Password reset successful! You can now log in.', 'success')
    return redirect(url_for('home'))

port = int(os.environ.get("PORT", 5000))  # Render가 준 포트 쓰고, 없으면 5000
# -----------------------------
# Flask 실행
# -----------------------------
if __name__ == "__main__":
    app.run()
#    try:
#       # public_url = ngrok.connect(5000)
#        print("앱 실행 시도", flush=True)
#        app.run(host='0.0.0.0',debug=True, port=port)
#    except Exception as e:
#        print(f"Flask run error: {e}", flush=True)
#        input("Press Enter to exit")