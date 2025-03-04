from flask import Flask, render_template, redirect, url_for, request, flash
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app, database, and SocketIO
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change to a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model for database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Chat message model for storing messages
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(500), nullable=False)

# Initialize database
with app.app_context():
    db.create_all()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))  # Redirect to chat if already logged in
    return redirect(url_for('login'))  # Otherwise, redirect to login


# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('chat'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return 'User already exists'
        
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        # Flash success message after successful registration
        flash('Registration successful! Please log in.', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Logs the user out
    flash('You have been logged out successfully!', 'info')  # Flash message after logout
    return redirect(url_for('login'))  # Redirect to login page after logout

@app.route('/chat')
@login_required
def chat():
    # Fetch all users except the current user
    users = User.query.filter(User.username != current_user.username).all()
    
    # Fetch all previous messages
    messages = Message.query.all()
    return render_template('chat.html', messages=messages, users=users)


# Real-time chat handler with SocketIO
@socketio.on('chat message')
def handle_message(data):
    message = Message(sender=data['username'], content=data['message'])
    db.session.add(message)
    db.session.commit()

    # Broadcast the message to all connected clients
    emit('chat message', {'username': data['username'], 'message': data['message']}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True,host='0.0.0.0')
