from flask import Flask, render_template, send_file, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from io import BytesIO
import os
import requests
import base64
import urllib.parse
from math import ceil
from pyngrok import ngrok
from urllib.parse import unquote

# -----------------------------
# Flask & DB 설정
# -----------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ugahan582818@localhost:3306/ugamedical'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Mail 설정
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='fkemfem85@gmail.com',
    MAIL_PASSWORD='jkwz jkcc gccl yvgh',
    MAIL_DEFAULT_SENDER='fkemfem85@gmail.com'
)

db = SQLAlchemy(app)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

# URL 세그먼트를 한글로 매핑해두면 자동생성 시 더 친절한 이름으로 나옵니다.
SEGMENT_NAME_MAP = {
    'product': '상품',
    'products': '상품',
    'category': '카테고리',
    'my_page': '마이페이지',
    'sign_up_terms': '회원가입',
    'reset_password': '비밀번호 초기화',
    'company': '회사소개',
    'checkout_page':'결제화면',
    # 필요하면 더 추가
}

# -----------------------------
# 아임포트 키
# -----------------------------
IMP_KEY = "5725674101821141"
IMP_SECRET = "fmHPJ9V9k8TkXerskLSMd4byOKJp13IGYBoL849Y4HtLnDX2oYlrzuLTZaW0geEddnrZHAYBUEl5hVqY"


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
    base_address = db.Column(db.String(255))
    detail_address = db.Column(db.String(255))
    phone = db.Column(db.String(15))
    agree_terms = db.Column(db.Boolean, default=False, nullable=False)
    agree_privacy = db.Column(db.Boolean, default=False, nullable=False)
    agree_marketing = db.Column(db.Boolean, default=False)
    cart_items = db.relationship('CartItem', back_populates='user', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', cascade='all, delete-orphan')

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

    user = db.relationship('User', back_populates='cart_items')
    product = db.relationship('Product')

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')
    delivery_address = db.Column(db.String(255))
    payment_completed_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    items = db.relationship('OrderItem', back_populates='order', cascade="all, delete-orphan")

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    options = db.Column(db.JSON, nullable=True)
    discount = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())

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
    try:
        response = requests.post(url, json=data)
        res = response.json()
        if res.get('code') != 0:
            print("아임포트 토큰 발급 실패:", res)
            return None
        return res['response']['access_token']
    except Exception as e:
        print("get_token 에러:", e)
        return None

def is_admin():
    return session.get('user_aff') == '유가'

def prettify_segment(seg):
    # 숫자(id)나 UUID면 그대로 두거나 추후 라우트에서 덮어쓰기 가능
    if seg.isdigit():
        return seg
    # 하이픈/언더바를 공백으로 변경
    return SEGMENT_NAME_MAP.get(seg, seg.replace('-', ' ').replace('_', ' ').title())

# -----------------------------
# 배너 관련 함수
# -----------------------------
def get_image_from_db(image_id):
    banner = BannerImage.query.get(image_id)
    if banner:
        return banner.image_data
    return None

# -----------------------------
# 라우트
# -----------------------------
@app.route('/')
def home():
    banners = BannerImage.query.order_by(BannerImage.created_at.asc()).all()
    products = Product.query.order_by(Product.created_at.desc()).limit(8).all()
    videos = Video.query.order_by(Video.created_at.asc()).limit(4).all()

    page = request.args.get('page', 1, type=int)
    per_page = 1
    pagination = Product.query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page)
    products = pagination.items

    return render_template('index.html',
                           banners=banners,
                           videos=videos,
                           products=products,
                           pagination=pagination,
                           user_name=session.get('user_name'),
                           user_title=session.get('user_title'),
                           show_login=request.args.get("show_login", 0))


@app.context_processor
def inject_breadcrumbs():
    path = unquote(request.path)  # /product/category/123
    # 루트('/')만 있는 경우 빈 리스트
    if path == '/' or path == '':
        return {'breadcrumbs': []}

    parts = [p for p in path.split('/') if p]
    crumbs = []
    accum = ''
    for i, part in enumerate(parts):
        accum += '/' + part
        title = prettify_segment(part)

        # 마지막이면 url을 None (템플릿에서 링크 안걸림)
        if i == len(parts) - 1:
            crumbs.append({'title': title, 'url': None})
        else:
            crumbs.append({'title': title, 'url': accum})
    return {'breadcrumbs': crumbs}

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
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    user_aff = session.get('user_aff', '')

    page = request.args.get('page', 1, type=int)
    per_page = 5

    if user_aff == '유가':
        orders_pagination = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    else:
        orders_pagination = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('my_page.html', user=user, pagination=orders_pagination)

@app.route('/my_page/orders_data')
def orders_data():
    try:
        page = int(request.args.get('page', 1))
        per_page = 5
        user_id = session.get('user_id')
        user_aff = session.get('user_aff', '')

        # 주문 쿼리
        if user_aff == '유가':
            orders_query = Order.query.order_by(Order.created_at.desc())
        else:
            orders_query = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc())

        total_orders = orders_query.count()
        total_pages = ceil(total_orders / per_page)
        orders = orders_query.offset((page - 1) * per_page).limit(per_page).all()

        orders_data = []
        for order in orders:
            order_items_data = []
            for item in order.items:
                product = item.product
                if product:
                    img_src = url_for('get_product_image', product_id=product.id)
                    order_items_data.append({
                        'name': product.name,
                        'quantity': item.quantity,
                        'price': item.unit_price,
                        'total_price': item.total_price,
                        'image_url': img_src
                    })

            # 버튼 표시 여부
            can_cancel = order.status not in ['배송중', '배송 완료', '취소됨']
            can_ship = order.status == '결제완료'
            can_deliver = order.status == '배송중'

            orders_data.append({
                'id': order.id,
                'total_price': order.total_price,
                'status': order.status,
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
                'notes': order.notes,
                'items': order_items_data,
                'is_admin': user_aff == '유가',
                'can_cancel': can_cancel,
                'can_ship': can_ship,
                'can_deliver': can_deliver
            })

        pagination = {
            'page': page,
            'pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }

        return jsonify({'orders': orders_data, 'pagination': pagination})

    except Exception as e:
        return jsonify({'error': str(e)})

# 주문내역 다시 주문
@app.route('/reorder/<int:order_id>', methods=['POST'])
def reorder(order_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 403

    user_id = session['user_id']
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'message': '주문이 없습니다.'}), 404

    # 기존 장바구니 아이템과 관계없이 새로 추가
    for item in order.items:
        product = item.product
        if not product:
            continue

        # 1️⃣ 장바구니에 이미 있는지 확인
        cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product.id).first()
        if cart_item:
            # 이미 있으면 수량만 증가
            cart_item.quantity += item.quantity
        else:
            # 없으면 새로 추가
            new_cart_item = CartItem(
                user_id=user_id,
                product_id=product.id,
                quantity=item.quantity
            )
            db.session.add(new_cart_item)

    db.session.commit()
    return jsonify({'success': True, 'message': '장바구니에 다시 담았습니다.'})

@app.route('/admin/update_order/<int:order_id>', methods=['POST'])
def update_order(order_id):
    if session.get('user_aff') != '유가':
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403

    data = request.get_json()
    action = data.get('action')
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'message': '주문이 없습니다.'}), 404

    if action == 'ship':
        if order.status == '취소됨':
            return jsonify({'success': False, 'message': '취소된 주문은 배송할 수 없습니다.'})
        order.status = '배송중'
        order.shipped_at = datetime.now()
    elif action == 'deliver':
        if order.status != '배송중':
            return jsonify({'success': False, 'message': '배송 중인 주문만 배송 완료 처리할 수 있습니다.'})
        order.status = '배송 완료'
        order.delivered_at = datetime.now()
    elif action == 'cancel':
        if order.status in ['배송중', '배송 완료']:
            return jsonify({'success': False, 'message': '배송 중이거나 완료된 주문은 취소할 수 없습니다.'})
        order.status = '취소됨'
    else:
        return jsonify({'success': False, 'message': '잘못된 요청입니다.'}), 400

    db.session.commit()
    return jsonify({'success': True, 'status': order.status})

@app.route('/user/cancel_order/<int:order_id>', methods=['POST'])
def user_cancel_order(order_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 403

    user_id = session['user_id']
    order = Order.query.get(order_id)

    if not order:
        return jsonify({'success': False, 'message': '주문이 없습니다.'}), 404

    if order.user_id != user_id:
        return jsonify({'success': False, 'message': '본인 주문만 취소 가능합니다.'}), 403

    # 배송 전/결제 완료 상태에서만 취소 가능
    if order.status in ['배송중', '배송 완료', '취소됨']:
        return jsonify({'success': False, 'message': '취소할 수 없는 상태입니다.'})

    order.status = '취소됨'
    db.session.commit()
    return jsonify({'success': True})

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

# 마이페이지 업로드 배너
@app.route('/upload_banner', methods=['POST'])
def upload_banner():
    if 'user_id' not in session or session.get('user_aff') != '유가':
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403

    image_file = request.files.get('banner_image')
    image_name = request.form.get('image_name')

    if not image_file or not image_name:
        return jsonify({'success': False, 'message': '이름과 이미지를 모두 입력해주세요.'}), 400

    new_banner = BannerImage(
        image_name=image_name,
        image_data=image_file.read()
    )
    db.session.add(new_banner)
    db.session.commit()

    return jsonify({'success': True, 'message': '배너 이미지가 추가되었습니다!'})

# 마이페이지 업로드 영상
@app.route('/upload_video', methods=['POST'])
def upload_video():
    # 관리자 확인
    if 'user_id' not in session or session.get('user_aff') != '유가':
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403

    description = request.form.get('description')
    video_file = request.files.get('video_file')
    video_url = request.form.get('video_url')
    video_name = request.form.get('video_name') or 'no_name'

    # 유튜브 URL 처리
    if video_url:
        import urllib.parse
        parsed = urllib.parse.urlparse(video_url)
        qs = urllib.parse.parse_qs(parsed.query)
        vid_id = qs.get('v', ['no_id'])[0]
        video_name = f"youtube_{vid_id}"
        video_url = f"https://www.youtube.com/watch?v={vid_id}"
        video_file = None  # 유튜브 업로드 시 파일은 무시

    # DB 저장
    new_video = Video(
        description=description,
        video_name=video_name,
        video_data=video_file.read() if video_file else None,
        video_url=video_url if video_url else None
    )
    db.session.add(new_video)
    db.session.commit()

    return jsonify({'success': True, 'message': '프로모션 영상이 추가되었습니다!'})

@app.route('/logout')
def logout():
    session.clear()
    flash("로그아웃되었습니다.", "success")
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
    return send_file(os.path.join('static', 'images', 'default.png'), mimetype='image/png')

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
    imp_uid = data.get("imp_uid")
    merchant_uid = data.get("merchant_uid")
    buyer_addr = data.get("buyer_addr", "")
    notes = data.get("notes", "")

    token = get_token()
    if not token:
        return jsonify({"success": False, "message": "토큰 발급 실패"}), 500

    url = f"https://api.iamport.kr/payments/{imp_uid}"
    headers = {"Authorization": token}

    try:
        res = requests.get(url, headers=headers).json()
    except Exception as e:
        return jsonify({"success": False, "message": f"결제 정보 요청 실패: {e}"}), 500

    if res.get('code') != 0:
        return jsonify({"success": False, "message": f"결제 조회 실패: {res}"}), 400

    payment_data = res.get('response')
    if not payment_data or payment_data.get('status') != 'paid':
        return jsonify({"success": False, "message": "결제 실패"})

    user_id = session['user_id']
    method = payment_data.get('pay_method')
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({"success": False, "message": "카트가 비어있습니다."}), 400

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # 주문 생성
    order = Order(
        user_id=user_id,
        total_price=total_price,
        payment_method=method,
        status='결제완료',
        delivery_address=buyer_addr,
        payment_completed_at=db.func.current_timestamp(),
        notes=notes
    )
    db.session.add(order)
    db.session.flush()  # order.id 필요

    # OrderItem 생성
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product.id,
            quantity=item.quantity,
            unit_price=item.product.price,  # CartItem에 없으므로 product.price 사용
            total_price=item.product.price * item.quantity
        )
        db.session.add(order_item)

    # 카트 비우기
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({"success": True, "message": "결제 성공", "order_id": order.id})


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
    buyer_addr = request.args.get('buyer_addr', "")
    notes = request.args.get('notes', "")

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

    user_id = session.get('user_id')
    if not user_id:
        return "로그인이 필요합니다.", 401

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return "카트가 비어있습니다.", 400

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    method = payment_data.get('pay_method')

    # 주문 생성
    order = Order(
        user_id=user_id,
        total_price=total_price,
        payment_method=method,
        status='결제완료',
        delivery_address=buyer_addr,
        payment_completed_at=db.func.current_timestamp(),
        notes=notes
    )
    db.session.add(order)
    db.session.flush()  # order.id 필요

    # OrderItem 생성
    for item in cart_items:
        unit_price = item.product.price
        quantity = item.quantity
        total_price_item = unit_price * quantity

        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product.id,
            quantity=quantity,
            unit_price=item.product.price,
            total_price=total_price_item,
            options=None,
            discount=0,
            tax=0,
            status='pending'
        )
        db.session.add(order_item)

    # 카트 비우기
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    return render_template('order_complete.html', order=order, items=order.items)

# 배송 시작
@app.route('/order/<int:order_id>/ship', methods=['POST'])
def ship_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'shipped'
    order.shipped_at = db.func.current_timestamp()
    db.session.commit()
    return jsonify({"success": True, "message": "배송 시작됨", "shipped_at": str(order.shipped_at)})

# 배송 완료
@app.route('/order/<int:order_id>/deliver', methods=['POST'])
def deliver_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'delivered'
    order.delivered_at = db.func.current_timestamp()
    db.session.commit()
    return jsonify({"success": True, "message": "배송 완료됨", "delivered_at": str(order.delivered_at)})

# 주문 취소
@app.route('/order/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)

    # 권한 확인: 관리자 또는 본인
    user_id = session.get('user_id')
    is_admin = session.get('user_aff') == '유가'
    if not is_admin and order.user_id != user_id:
        return jsonify({"success": False, "message": "권한이 없습니다."})

    # 배송 시작 전(paid, pending)만 취소 가능
    if order.status in ['paid', 'pending']:
        order.status = 'canceled'
        db.session.commit()
        return jsonify({"success": True, "message": "주문 취소됨"})

    return jsonify({"success": False, "message": "배송 시작 후에는 주문을 취소할 수 없습니다."})

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

# 비밀번호 변경
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            token = serializer.dumps(email, salt='password-reset-salt')
            reset_link = url_for('reset_with_token', token=token, _external=True)

            # 메일 보내기
            msg = Message('비밀번호 재설정 안내', recipients=[email])
            msg.body = f"다음 링크에서 비밀번호를 재설정하세요:\n{reset_link}\n\n30분 내에 유효합니다."
            mail.send(msg)

            flash('비밀번호 재설정 메일이 전송되었습니다.', 'success')
        else:
            flash('가입된 이메일이 없습니다.', 'danger')

        return redirect(url_for('reset_password'))

    return render_template('reset_password.html')

# 신규 비밀번호
@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=1800)
    except:
        flash('링크가 만료되었거나 잘못되었습니다.', 'danger')
        return redirect(url_for('reset_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('비밀번호가 성공적으로 변경되었습니다.', 'success')
            return redirect(url_for('login'))  # <- 수정됨

    return render_template('reset_with_token.html')

port = int(os.environ.get("PORT", 5000))  # Render가 준 포트 쓰고, 없으면 5000
# -----------------------------
# Flask 실행
# -----------------------------

#if __name__ == "__main__":
#    try:
#       # public_url = ngrok.connect(5000)
#        print("앱 실행 시도", flush=True)
#        app.run(host='0.0.0.0',debug=True, port=port)
#    except Exception as e:
#        print(f"Flask run error: {e}", flush=True)
#        input("Press Enter to exit")

if __name__ == "__main__":
    port = 5000  # 로컬 Flask 포트

    # Flask 서버 실행
    app.run(host='0.0.0.0', port=port, debug=True)