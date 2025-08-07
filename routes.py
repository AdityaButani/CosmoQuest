from flask import render_template, request, jsonify, session, redirect, url_for
from app import app
from api_service import generate_quest_content, search_topic_context
import logging
import json

@app.route('/')
def index():
    """Main landing page where users enter their topic"""
    return render_template('index.html')

@app.route('/generate-quest', methods=['POST'])
def generate_quest():
    """Generate a new quest based on user input"""
    try:
        topic = request.form.get('topic', '').strip()
        if not topic:
            return jsonify({'error': 'Please enter a valid topic'}), 400
        
        # Clear any existing quest from session
        session.clear()
        
        # Store topic in session
        session['topic'] = topic
        session['current_quest'] = 1
        session['completed_quests'] = []
        
        # Get context from web search
        logging.info(f"Searching for context on topic: {topic}")
        context = search_topic_context(topic)
        session['context'] = context
        
        # Generate initial quest content
        logging.info(f"Generating quest content for: {topic}")
        quest_data = generate_quest_content(topic, 1, context)
        
        if quest_data:
            session['quest_1'] = quest_data
            return redirect(url_for('quest_page', quest_num=1))
        else:
            return jsonify({'error': 'Failed to generate quest content. Please try again.'}), 500
            
    except Exception as e:
        logging.error(f"Error generating quest: {str(e)}")
        return jsonify({'error': 'An error occurred while generating your quest. Please try again.'}), 500

@app.route('/quest/<int:quest_num>')
def quest_page(quest_num):
    """Display a specific quest page"""
    if 'topic' not in session:
        return redirect(url_for('index'))
    
    if quest_num < 1 or quest_num > 5:
        return redirect(url_for('index'))
    
    # Check if quest is accessible (sequential unlock)
    if quest_num > 1 and quest_num - 1 not in session.get('completed_quests', []):
        return redirect(url_for('quest_page', quest_num=session.get('current_quest', 1)))
    
    quest_key = f'quest_{quest_num}'
    
    # Generate quest content if not already generated
    if quest_key not in session:
        try:
            quest_data = generate_quest_content(
                session['topic'], 
                quest_num, 
                session.get('context', '')
            )
            if quest_data:
                session[quest_key] = quest_data
            else:
                return render_template('quest.html', error="Failed to generate quest content")
        except Exception as e:
            logging.error(f"Error generating quest {quest_num}: {str(e)}")
            return render_template('quest.html', error="An error occurred while loading the quest")
    
    quest_data = session.get(quest_key, {})
    
    return render_template('quest.html', 
                         quest_num=quest_num,
                         quest_data=quest_data,
                         topic=session['topic'],
                         completed_quests=session.get('completed_quests', []),
                         total_quests=5)

@app.route('/complete-quest', methods=['POST'])
def complete_quest():
    """Mark a quest as completed and unlock the next one"""
    try:
        quest_num = int(request.form.get('quest_num', 0))
        
        if quest_num < 1 or quest_num > 5:
            return jsonify({'error': 'Invalid quest number'}), 400
        
        completed_quests = session.get('completed_quests', [])
        if quest_num not in completed_quests:
            completed_quests.append(quest_num)
            session['completed_quests'] = completed_quests
        
        # Update current quest to next available
        if quest_num < 5:
            session['current_quest'] = quest_num + 1
            next_quest_url = url_for('quest_page', quest_num=quest_num + 1)
        else:
            # All quests completed
            next_quest_url = url_for('quest_page', quest_num=5)
        
        return jsonify({
            'success': True,
            'completed_quests': completed_quests,
            'next_quest_url': next_quest_url,
            'message': f'Quest {quest_num} completed!' if quest_num < 5 else 'Congratulations! You\'ve completed all quests!'
        })
        
    except Exception as e:
        logging.error(f"Error completing quest: {str(e)}")
        return jsonify({'error': 'Failed to complete quest'}), 500

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    """Process quiz submission and return results"""
    try:
        quest_num = int(request.form.get('quest_num', 0))
        answers = request.form.get('answers', '{}')
        
        if quest_num < 2 or quest_num > 5:
            return jsonify({'error': 'Invalid quest number for quiz'}), 400
        
        # Parse answers
        try:
            user_answers = json.loads(answers)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid answer format'}), 400
        
        # Get quest data to check correct answers
        quest_key = f'quest_{quest_num}'
        quest_data = session.get(quest_key, {})
        
        if 'quiz' not in quest_data:
            return jsonify({'error': 'Quiz data not found'}), 400
        
        quiz_data = quest_data['quiz']
        correct_answers = quiz_data.get('correct_answers', {})
        
        # Calculate score
        total_questions = len(correct_answers)
        correct_count = 0
        
        for q_id, correct_answer in correct_answers.items():
            user_answer = user_answers.get(q_id, '')
            if str(user_answer).lower().strip() == str(correct_answer).lower().strip():
                correct_count += 1
        
        score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        return jsonify({
            'success': True,
            'score': correct_count,
            'total': total_questions,
            'percentage': round(score_percentage, 1),
            'passed': score_percentage >= 60,  # 60% passing grade
            'correct_answers': correct_answers
        })
        
    except Exception as e:
        logging.error(f"Error processing quiz: {str(e)}")
        return jsonify({'error': 'Failed to process quiz submission'}), 500

@app.route('/reset-quest')
def reset_quest():
    """Reset the current quest session"""
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('index.html'), 500
