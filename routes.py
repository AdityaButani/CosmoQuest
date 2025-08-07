from flask import render_template, request, jsonify, session, redirect, url_for
from app import app, quest_data_cache
from api_service import generate_quest_content, search_topic_context
import logging
import json
import uuid

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
        
        # Generate unique session ID for quest data storage
        quest_session_id = str(uuid.uuid4())
        session['quest_session_id'] = quest_session_id
        
        # Store minimal data in session
        session['topic'] = topic
        session['current_quest'] = 1
        session['completed_quests'] = []
        
        # Get context from web search
        logging.info(f"Searching for context on topic: {topic}")
        context = search_topic_context(topic)
        
        # Initialize quest cache for this session
        quest_data_cache[quest_session_id] = {'context': context}
        
        # Generate initial quest content
        logging.info(f"Generating quest content for: {topic}")
        quest_data = generate_quest_content(topic, 1, context)
        
        if quest_data:
            quest_data_cache[quest_session_id]['quest_1'] = quest_data
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
    
    quest_session_id = session.get('quest_session_id')
    if not quest_session_id or quest_session_id not in quest_data_cache:
        return redirect(url_for('index'))
    
    quest_key = f'quest_{quest_num}'
    
    # Generate quest content if not already generated
    if quest_key not in quest_data_cache[quest_session_id]:
        try:
            logging.info(f"Generating quest {quest_num} for topic: {session.get('topic', 'unknown')}")
            quest_data = generate_quest_content(
                session['topic'], 
                quest_num, 
                quest_data_cache[quest_session_id].get('context', '')
            )
            if quest_data:
                quest_data_cache[quest_session_id][quest_key] = quest_data
                logging.info(f"Quest {quest_num} data generated and saved to cache")
            else:
                logging.error(f"Failed to generate quest {quest_num} data")
                return render_template('quest.html', error="Failed to generate quest content")
        except Exception as e:
            logging.error(f"Error generating quest {quest_num}: {str(e)}")
            return render_template('quest.html', error="An error occurred while loading the quest")
    
    quest_data = quest_data_cache[quest_session_id].get(quest_key, {})
    
    # Debug logging for visual suggestions
    logging.info(f"Quest {quest_num} data keys: {list(quest_data.keys())}")
    if 'visual_suggestions' in quest_data:
        logging.info(f"Visual suggestions count: {len(quest_data['visual_suggestions'])}")
        logging.info(f"Visual suggestions: {quest_data['visual_suggestions']}")
    else:
        logging.warning(f"No visual_suggestions in quest {quest_num} data")
    
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
        
        logging.info(f"Quiz submission for quest {quest_num}")
        logging.info(f"Raw form data: {dict(request.form)}")
        
        if quest_num < 2 or quest_num > 5:
            return jsonify({'error': 'Invalid quest number for quiz'}), 400
        
        # Parse answers - handle both JSON string and direct form data
        try:
            if answers and answers != '{}':
                user_answers = json.loads(answers)
            else:
                # Fallback: collect answers directly from form data
                user_answers = {}
                for key, value in request.form.items():
                    if key.startswith('q') and key != 'quest_num':
                        user_answers[key] = value
        except json.JSONDecodeError:
            # Fallback: collect answers directly from form data
            user_answers = {}
            for key, value in request.form.items():
                if key.startswith('q') and key != 'quest_num':
                    user_answers[key] = value
        
        logging.info(f"Parsed user answers: {user_answers}")
        
        # Get quest data from cache
        quest_session_id = session.get('quest_session_id')
        if not quest_session_id or quest_session_id not in quest_data_cache:
            return jsonify({'error': 'Session expired. Please start a new quest.'}), 400
        
        quest_key = f'quest_{quest_num}'
        quest_data = quest_data_cache[quest_session_id].get(quest_key, {})
        
        logging.info(f"Quest data found: {'yes' if quest_data else 'no'}")
        if quest_data:
            logging.info(f"Quiz in quest data: {'yes' if 'quiz' in quest_data else 'no'}")
            if 'quiz' in quest_data:
                logging.info(f"Quiz type: {quest_data['quiz'].get('type', 'unknown')}")
        
        if 'quiz' not in quest_data:
            # Try regenerating the quest if it's missing
            logging.warning(f"Quest data missing for quest {quest_num}. Attempting to regenerate...")
            try:
                quest_data = generate_quest_content(
                    session.get('topic', ''), 
                    quest_num, 
                    quest_data_cache[quest_session_id].get('context', '')
                )
                if quest_data and 'quiz' in quest_data:
                    quest_data_cache[quest_session_id][quest_key] = quest_data
                    logging.info(f"Successfully regenerated quest {quest_num} data")
                else:
                    logging.error(f"Failed to regenerate quest {quest_num} data")
                    return jsonify({'error': 'Quiz data not found and could not be regenerated'}), 400
            except Exception as e:
                logging.error(f"Error regenerating quest {quest_num}: {str(e)}")
                return jsonify({'error': 'Quiz data not found'}), 400
        
        quiz_data = quest_data['quiz']
        correct_answers = quiz_data.get('correct_answers', {})
        
        # Handle different quiz formats
        quiz_type = quiz_data.get('type', 'regular')
        total_questions = 0
        correct_count = 0
        
        if quiz_type == 'matching' and 'correct_matches' in quiz_data:
            # New matching format with left_items and right_items
            correct_matches = quiz_data.get('correct_matches', {})
            left_items = quiz_data.get('left_items', [])
            
            logging.info(f"Matching quiz - left_items: {left_items}")
            logging.info(f"Matching quiz - correct_matches: {correct_matches}")
            
            total_questions = len(left_items)
            for i, left_item in enumerate(left_items):
                question_key = f'q{i+1}'
                user_answer = user_answers.get(question_key, '')
                correct_answer = correct_matches.get(left_item, '')
                
                logging.info(f"Question {i+1}: '{left_item}' -> User: '{user_answer}' vs Correct: '{correct_answer}'")
                
                if str(user_answer).lower().strip() == str(correct_answer).lower().strip():
                    correct_count += 1
        else:
            # Regular quiz format
            total_questions = len(correct_answers)
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
