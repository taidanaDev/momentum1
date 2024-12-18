import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Task
from website import db
import datetime
import random

logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s : %(message)s'
)

views = Blueprint('views', __name__)

# Function to get a daily challenge
def get_daily_challenge():
    challenges = [
        {"title": "Drink 8 glasses of water", "description": "Stay hydrated today!"},
        {"title": "Walk 10,000 steps", "description": "Get moving and stay active!"},
        {"title": "Read for 30 minutes", "description": "Take some time to read a book."},
        {"title": "Meditate for 10 minutes", "description": "Clear your mind and relax."},
        {"title": "Write down 3 things you're grateful for", "description": "Practice gratitude."}
    ]
    return random.choice(challenges)
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        title = request.form.get('title')
        description = request.form.get('description')
        date = request.form.get('date')

        if not title or not date:
            flash("Title and date are required!", category='error')
        else:
            try:
                task_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
                new_task = Task(
                    title=title,
                    description=description,
                    date=task_date,
                    user_id=current_user.id
                )

                db.session.add(new_task)
                db.session.commit()
                flash('Task added successfully!', category='success')
            except ValueError:
                flash('Invalid date format! Please use YYYY-MM-DD.', category='error')

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    # Calculate progress
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.is_done)
    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    daily_challenge = get_daily_challenge()

    return render_template("home.html", user=current_user, tasks=tasks, 
                           progress_percentage=progress_percentage, 
                           daily_challenge=daily_challenge,)

@views.route('/delete-task', methods=['POST'])
@login_required
def delete_task():  
    taskId = request.form.get('taskId')
    task = Task.query.get(taskId)
    if task:
        if task.user_id == current_user.id:
            db.session.delete(task)
            db.session.commit()
            flash('Task deleted successfully!', category='success')
        else:
            flash('You do not have permission to delete this task.', category='error')

    return redirect(url_for('views.home'))

@views.route('/update-task-status', methods=['POST'])
@login_required
def update_task_status():
    task_id = request.form.get('taskId')
    is_done = request.form.get('isDone') == 'true'

    task = Task.query.get(task_id)
    if task:
        if task.user_id == current_user.id:
            task.is_done = not task.is_done
            db.session.commit()
            flash('Task status updated successfully!', category='success')
        else:
            flash('You do not have permission to update this task.', category='error')
    else:
        flash('Task not found.', category='error')

    return redirect(url_for('views.home'))

