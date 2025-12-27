from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import io
import json

app = Flask(__name__)
import os

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
# Use /tmp/ directory for SQLite in Vercel (writable location)
# Note: Data in /tmp/ is ephemeral and will be lost when function restarts
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#667eea')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('Task', backref='category', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, working, done
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    due_date = db.Column(db.DateTime, nullable=True)
    reminder_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    tags = db.Column(db.String(200), nullable=True)  # Comma-separated tags

# Create tables
with app.app_context():
    db.create_all()

# Helper Functions
def get_priority_tasks(user_id):
    """Get tasks by priority"""
    return {
        'urgent': Task.query.filter_by(user_id=user_id, priority='urgent', status='pending').count(),
        'high': Task.query.filter_by(user_id=user_id, priority='high', status='pending').count(),
        'medium': Task.query.filter_by(user_id=user_id, priority='medium', status='pending').count(),
        'low': Task.query.filter_by(user_id=user_id, priority='low', status='pending').count(),
    }

def get_overdue_tasks(user_id):
    """Get overdue tasks"""
    now = datetime.utcnow()
    return Task.query.filter(
        Task.user_id == user_id,
        Task.status != 'done',
        Task.due_date < now
    ).count()

def get_upcoming_tasks(user_id, days=7):
    """Get tasks due in the next N days"""
    now = datetime.utcnow()
    future = now + timedelta(days=days)
    return Task.query.filter(
        Task.user_id == user_id,
        Task.status != 'done',
        Task.due_date.between(now, future)
    ).count()

# Routes
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get filter parameters
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    priority_filter = request.args.get('priority', '')
    status_filter = request.args.get('status', '')
    tag_filter = request.args.get('tag', '')
    sort_by = request.args.get('sort', 'created_desc')
    
    # Base query
    query = Task.query.filter_by(user_id=user.id)
    
    # Apply filters
    if search:
        query = query.filter(Task.title.contains(search) | Task.description.contains(search))
    if category_filter:
        query = query.filter_by(category_id=int(category_filter))
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if tag_filter:
        query = query.filter(Task.tags.contains(tag_filter))
    
    # Apply sorting
    if sort_by == 'created_desc':
        query = query.order_by(Task.created_at.desc())
    elif sort_by == 'created_asc':
        query = query.order_by(Task.created_at.asc())
    elif sort_by == 'due_date':
        query = query.order_by(Task.due_date.asc().nullslast())
    elif sort_by == 'priority':
        priority_order = {'urgent': 1, 'high': 2, 'medium': 3, 'low': 4}
        tasks = query.all()
        tasks.sort(key=lambda x: priority_order.get(x.priority, 5))
        query = tasks
    elif sort_by == 'title':
        query = query.order_by(Task.title.asc())
    
    tasks = query.all() if isinstance(query, list) else query.all()
    
    # Count tasks by status
    pending = Task.query.filter_by(user_id=user.id, status='pending').count()
    working = Task.query.filter_by(user_id=user.id, status='working').count()
    done = Task.query.filter_by(user_id=user.id, status='done').count()
    
    # Get categories
    categories = Category.query.filter_by(user_id=user.id).all()
    
    # Get priority counts
    priority_counts = get_priority_tasks(user.id)
    
    # Get overdue and upcoming
    overdue = get_overdue_tasks(user.id)
    upcoming = get_upcoming_tasks(user.id)
    
    # Get all unique tags
    all_tasks = Task.query.filter_by(user_id=user.id).all()
    tags_set = set()
    for task in all_tasks:
        if task.tags:
            tags_set.update([tag.strip() for tag in task.tags.split(',')])
    all_tags = sorted(list(tags_set))
    
    return render_template('index.html', 
                         tasks=tasks, 
                         username=user.username,
                         pending=pending,
                         working=working,
                         done=done,
                         categories=categories,
                         priority_counts=priority_counts,
                         overdue=overdue,
                         upcoming=upcoming,
                         all_tags=all_tags,
                         dark_mode=user.dark_mode,
                         current_filters={
                             'search': search,
                             'category': category_filter,
                             'priority': priority_filter,
                             'status': status_filter,
                             'tag': tag_filter,
                             'sort': sort_by
                         })

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create default categories
        default_categories = [
            {'name': 'Work', 'color': '#667eea'},
            {'name': 'Personal', 'color': '#28a745'},
            {'name': 'Shopping', 'color': '#ffc107'},
            {'name': 'Health', 'color': '#dc3545'},
        ]
        
        for cat in default_categories:
            category = Category(name=cat['name'], color=cat['color'], user_id=new_user.id)
            db.session.add(category)
        
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    priority = request.form.get('priority', 'medium')
    category_id = request.form.get('category_id')
    tags = request.form.get('tags', '')
    due_date_str = request.form.get('due_date')
    reminder_date_str = request.form.get('reminder_date')
    
    due_date = None
    reminder_date = None
    
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        except:
            pass
    
    if reminder_date_str:
        try:
            reminder_date = datetime.strptime(reminder_date_str, '%Y-%m-%dT%H:%M')
        except:
            pass
    
    if title:
        new_task = Task(
            title=title,
            description=description,
            priority=priority,
            category_id=int(category_id) if category_id else None,
            tags=tags,
            due_date=due_date,
            reminder_date=reminder_date,
            user_id=session['user_id']
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
    
    return redirect(url_for('index'))

@app.route('/update/<int:task_id>/<status>')
def update_status(task_id, status):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    
    if task and status in ['pending', 'working', 'done']:
        task.status = status
        if status == 'done':
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None
        db.session.commit()
        flash(f'Task status updated to {status}!', 'success')
    
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    categories = Category.query.filter_by(user_id=session['user_id']).all()
    
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.priority = request.form.get('priority', 'medium')
        task.tags = request.form.get('tags', '')
        
        category_id = request.form.get('category_id')
        task.category_id = int(category_id) if category_id else None
        
        due_date_str = request.form.get('due_date')
        reminder_date_str = request.form.get('reminder_date')
        
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except:
                task.due_date = None
        else:
            task.due_date = None
        
        if reminder_date_str:
            try:
                task.reminder_date = datetime.strptime(reminder_date_str, '%Y-%m-%dT%H:%M')
            except:
                task.reminder_date = None
        else:
            task.reminder_date = None
        
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit.html', task=task, categories=categories)

@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        color = request.form.get('color', '#667eea')
        
        if name:
            category = Category(name=name, color=color, user_id=session['user_id'])
            db.session.add(category)
            db.session.commit()
            flash('Category created successfully!', 'success')
    
    categories = Category.query.filter_by(user_id=session['user_id']).all()
    user = User.query.get(session['user_id'])
    return render_template('categories.html', categories=categories, dark_mode=user.dark_mode)

@app.route('/category/delete/<int:category_id>')
def delete_category(category_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    category = Category.query.filter_by(id=category_id, user_id=session['user_id']).first()
    
    if category:
        # Update tasks to remove category
        tasks = Task.query.filter_by(category_id=category_id).all()
        for task in tasks:
            task.category_id = None
        
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    
    return redirect(url_for('manage_categories'))

@app.route('/toggle-dark-mode')
def toggle_dark_mode():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user.dark_mode = not user.dark_mode
    db.session.commit()
    
    return redirect(request.referrer or url_for('index'))

@app.route('/export/csv')
def export_csv():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Title', 'Description', 'Status', 'Priority', 'Category', 'Tags', 
                     'Due Date', 'Created At', 'Completed At'])
    
    # Write data
    for task in tasks:
        category_name = task.category.name if task.category else ''
        due_date = task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else ''
        created = task.created_at.strftime('%Y-%m-%d %H:%M')
        completed = task.completed_at.strftime('%Y-%m-%d %H:%M') if task.completed_at else ''
        
        writer.writerow([
            task.title,
            task.description or '',
            task.status,
            task.priority,
            category_name,
            task.tags or '',
            due_date,
            created,
            completed
        ])
    
    # Prepare response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'tasks_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/export/json')
def export_json():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    
    tasks_data = []
    for task in tasks:
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'category': task.category.name if task.category else None,
            'tags': task.tags.split(',') if task.tags else [],
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'reminder_date': task.reminder_date.isoformat() if task.reminder_date else None,
            'created_at': task.created_at.isoformat(),
            'completed_at': task.completed_at.isoformat() if task.completed_at else None
        })
    
    return send_file(
        io.BytesIO(json.dumps(tasks_data, indent=2).encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name=f'tasks_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )

@app.route('/api/reminders')
def get_reminders():
    """API endpoint to get upcoming reminders"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    now = datetime.utcnow()
    upcoming = now + timedelta(hours=24)
    
    tasks = Task.query.filter(
        Task.user_id == session['user_id'],
        Task.status != 'done',
        Task.reminder_date.between(now, upcoming)
    ).all()
    
    reminders = []
    for task in tasks:
        reminders.append({
            'id': task.id,
            'title': task.title,
            'reminder_date': task.reminder_date.isoformat(),
            'priority': task.priority
        })
    
    return jsonify(reminders)

if __name__ == '__main__':
    app.run(debug=False)
