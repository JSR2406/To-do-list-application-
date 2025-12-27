# 🚀 Advanced Flask To-Do Application

A feature-rich, production-ready To-Do application built with Flask, featuring advanced task management, dark mode, categories, priorities, and comprehensive export capabilities.

## ✨ Features

### 🔐 **User Authentication**
- Secure registration and login with password hashing (pbkdf2:sha256)
- Session-based authentication
- User-specific data isolation

### 📋 **Advanced Task Management**
- **CRUD Operations**: Create, read, update, and delete tasks
- **Task Status**: Three states (Pending, Working, Done)
- **Priority Levels**: Urgent, High, Medium, Low
- **Due Dates & Reminders**: Set deadlines and get notifications
- **Categories**: Organize tasks with custom color-coded categories
- **Tags**: Add multiple tags to tasks for better organization
- **Task Completion Tracking**: Automatic timestamp when tasks are completed

### 🎨 **Modern UI/UX**
- **Dark Mode**: Toggle between light and dark themes
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Modern Typography**: Google Fonts (Inter) for premium look
- **Smooth Animations**: Micro-interactions and transitions
- **Gradient Backgrounds**: Beautiful color schemes
- **Glassmorphism Effects**: Modern design aesthetics

### 🔍 **Search & Filter**
- **Full-Text Search**: Search across task titles and descriptions
- **Category Filter**: View tasks by category
- **Priority Filter**: Filter by priority level
- **Status Filter**: Filter by task status
- **Tag Filter**: Filter by tags
- **Multi-Sort Options**: Sort by date, priority, title, or due date

### 📊 **Dashboard Analytics**
- Real-time statistics (Pending, In Progress, Completed)
- Priority breakdown (Urgent, High, Medium, Low)
- Overdue task counter
- Upcoming tasks (next 7 days)
- Visual stat cards with click-to-filter

### 📤 **Export Functionality**
- **CSV Export**: Download tasks as CSV for Excel/Sheets
- **JSON Export**: Export data in JSON format for backup/migration
- Includes all task details (title, description, status, priority, category, tags, dates)

### 🔔 **Reminders & Notifications**
- Set reminder dates for tasks
- API endpoint for upcoming reminders
- Background reminder checking

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd flask-todo-app
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Application

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Create an account** and start managing your tasks!

## 📖 Usage Guide

### Getting Started
1. **Register**: Create a new account with username and password
2. **Login**: Access your personal dashboard
3. **Add Tasks**: Create tasks with all the details you need
4. **Organize**: Use categories and tags to organize your work
5. **Track Progress**: Update task statuses as you work
6. **Export**: Download your tasks anytime for backup

### Task Management
- **Add Task**: Fill in title (required), description, priority, category, tags, due date, and reminder
- **Update Status**: Click status buttons to move tasks through your workflow
- **Edit Task**: Modify any task details anytime
- **Delete Task**: Remove completed or unwanted tasks
- **Filter & Search**: Find tasks quickly with powerful filters

### Categories
- Click "📁 Categories" to manage your categories
- Create custom categories with color coding
- Assign tasks to categories for better organization
- Delete categories (tasks remain, just uncategorized)

### Dark Mode
- Click the "🌙 Dark Mode" button to toggle themes
- Preference is saved per user
- Easy on the eyes for night work

### Export Data
- **CSV**: Perfect for spreadsheets and data analysis
- **JSON**: Great for backups or migrating to other systems
- Exports include all task metadata

## 📁 Project Structure

```
flask-todo-app/
├── app.py                    # Main application with all routes
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── instance/
│   └── todo.db              # SQLite database (auto-created)
└── templates/
    ├── base.html            # Base template with dark mode
    ├── login.html           # Login page
    ├── register.html        # Registration page
    ├── index.html           # Main dashboard
    ├── edit.html            # Task editing page
    └── categories.html      # Category management
```

## 🗄️ Database Schema

### User Model
- `id`: Primary key
- `username`: Unique username
- `password`: Hashed password
- `dark_mode`: Dark mode preference (boolean)
- `tasks`: Relationship to tasks
- `categories`: Relationship to categories

### Task Model
- `id`: Primary key
- `title`: Task title
- `description`: Task description (optional)
- `status`: Task status (pending/working/done)
- `priority`: Priority level (low/medium/high/urgent)
- `due_date`: Due date and time (optional)
- `reminder_date`: Reminder date and time (optional)
- `created_at`: Creation timestamp
- `completed_at`: Completion timestamp (optional)
- `user_id`: Foreign key to User
- `category_id`: Foreign key to Category (optional)
- `tags`: Comma-separated tags (optional)

### Category Model
- `id`: Primary key
- `name`: Category name
- `color`: Hex color code
- `user_id`: Foreign key to User
- `tasks`: Relationship to tasks

## 🔧 Technologies Used

- **Backend**: Flask 3.0.0
- **Database**: SQLite with Flask-SQLAlchemy 3.1.1
- **Security**: Werkzeug 3.0.1 (password hashing)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Fonts**: Google Fonts (Inter)
- **Icons**: Unicode Emojis

## 🎨 Design Features

- **Color Palette**: Carefully curated gradients and colors
- **Typography**: Modern Inter font family
- **Animations**: Smooth transitions and hover effects
- **Responsive**: Mobile-first design approach
- **Accessibility**: Semantic HTML and proper contrast ratios
- **Dark Mode**: Complete theme with adjusted colors

## 🔒 Security Features

- Password hashing using pbkdf2:sha256
- Session-based authentication
- CSRF protection via Flask's secret key
- User data isolation (users can only see their own data)
- SQL injection protection via SQLAlchemy ORM
- Input validation on forms

## 📊 API Endpoints

### Public Routes
- `GET /login` - Login page
- `POST /login` - Login submission
- `GET /register` - Registration page
- `POST /register` - Registration submission

### Protected Routes (require login)
- `GET /` - Main dashboard
- `POST /add` - Add new task
- `GET /edit/<task_id>` - Edit task page
- `POST /edit/<task_id>` - Update task
- `GET /update/<task_id>/<status>` - Update task status
- `GET /delete/<task_id>` - Delete task
- `GET /categories` - Category management
- `POST /categories` - Create category
- `GET /category/delete/<category_id>` - Delete category
- `GET /toggle-dark-mode` - Toggle dark mode
- `GET /export/csv` - Export tasks as CSV
- `GET /export/json` - Export tasks as JSON
- `GET /api/reminders` - Get upcoming reminders (JSON API)
- `GET /logout` - Logout

## 🚀 Advanced Features

### Filter & Sort Options
- **Search**: Full-text search across titles and descriptions
- **Category**: Filter by specific category
- **Priority**: Filter by priority level
- **Status**: Filter by task status
- **Tag**: Filter by specific tag
- **Sort**: Multiple sort options (date, priority, title, due date)

### Statistics Dashboard
- Total pending tasks
- Tasks in progress
- Completed tasks
- Urgent priority count
- High priority count
- Overdue tasks
- Upcoming tasks (next 7 days)

### Default Categories
New users automatically get 4 default categories:
- 🔵 Work (Blue)
- 🟢 Personal (Green)
- 🟡 Shopping (Yellow)
- 🔴 Health (Red)

## 🎯 Future Enhancements

Potential features for future versions:
- [ ] Email notifications for reminders
- [ ] Recurring tasks
- [ ] Task templates
- [ ] Collaboration (shared tasks)
- [ ] File attachments
- [ ] Task comments
- [ ] Activity log
- [ ] Mobile app (React Native/Flutter)
- [ ] Calendar view
- [ ] Kanban board view
- [ ] Time tracking
- [ ] Productivity analytics

## 🐛 Troubleshooting

### Database Issues
If you encounter database errors, delete the `instance/todo.db` file and restart the application. It will create a fresh database.

### Port Already in Use
If port 5000 is already in use, modify the last line in `app.py`:
```python
app.run(debug=True, port=5001)  # Use different port
```

### Dark Mode Not Saving
Make sure cookies are enabled in your browser for session management.

## 📝 License

This project is open source and available for educational purposes.

## 👨‍💻 Development

Built with ❤️ using Flask and modern web technologies.

### Contributing
Feel free to fork, modify, and use this project for your own purposes!

### Support
For issues or questions, please check the code comments or create an issue.

---

**Happy Task Managing! 🎉**
