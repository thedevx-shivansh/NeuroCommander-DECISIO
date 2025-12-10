# ========== NeuroCommander v4.0 - PRODUCTION BACKEND WITH FULL AUTHENTICATION ==========
# Gemini 3 Pro + Enterprise Architecture + Email/Password + OAuth Ready
# google-genai SDK (Latest Dec 2025)
# Production-Grade for Kaggle Competition + Professional Authentication System
from dotenv import load_dotenv  # <--- ADD THIS
load_dotenv()
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from google import genai
from google.genai import types
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
import json
import os
import time
import logging
import traceback
from datetime import datetime
from functools import wraps
from typing import Dict, List, Tuple, Optional
import secrets

# ========== LOGGING SETUP ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== FLASK APP INITIALIZATION ==========
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# ========== DATABASE CONFIGURATION (SMART SWITCH) ==========
# Checks if we are on Render (DATABASE_URL exists) or Local (sqlite)
database_url = os.getenv('DATABASE_URL')

if database_url:
    # Fix for Render's Postgres URL (SQLAlchemy requires 'postgresql://', Render gives 'postgres://')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    logger.info("✅ Using Render PostgreSQL Database")
else:
    # Fallback to SQLite for local testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///neurocommander.db'
    logger.info("⚠️ Using Local SQLite Database")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))

db = SQLAlchemy(app)

# ========== LOGIN MANAGER ==========
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Enable CORS for API requests
CORS(app, supports_credentials=True)

# ========== DATABASE MODELS ==========

class User(UserMixin, db.Model):
    """User Model with Email/Password and OAuth Support"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    name = db.Column(db.String(120), nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    auth_method = db.Column(db.String(20), default='email')  # 'email' or 'google'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to analyses
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'auth_method': self.auth_method,
            'created_at': self.created_at.isoformat()
        }


class Analysis(db.Model):
    """Analysis History Model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dilemma = db.Column(db.Text, nullable=False)
    analysis_result = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    execution_time = db.Column(db.Float)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'dilemma': self.dilemma[:200] + '...' if len(self.dilemma) > 200 else self.dilemma,
            'created_at': self.created_at.isoformat(),
            'execution_time': self.execution_time
        }


# ========== GEMINI API CONFIGURATION ==========
API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
client = genai.Client(api_key=API_KEY)

MODEL_DEEP_ANALYSIS = 'gemini-3-pro-preview'
MODEL_DECISION = 'gemini-3-pro-preview'
MODEL_FORMATTER = 'gemini-2.0-flash-exp'

THINKING_LEVEL_DEEP = 'high'
THINKING_LEVEL_QUICK = 'low'
DEFAULT_TEMPERATURE = 1.0

# Constants
MAX_DILEMMA_LENGTH = 3000
MIN_DILEMMA_LENGTH = 20
MAX_RETRIES = 3
REQUEST_TIMEOUT = 120

# ========== SYSTEM PROMPTS ==========
SYSTEM_PROMPT_ANALYST = """You are Dr. NeuroCommand Synthesis - an elite AI psychologist, decision scientist, and systems architect.

Your mandate: Perform DEEP, MULTI-DIMENSIONAL analysis of complex human dilemmas using:

- Advanced psychological frameworks (CBT, systems theory, narrative psychology)
- Temporal outcome simulation (1 week → 5 years)
- Cognitive distortion detection with neuroscience grounding
- Values-alignment analysis
- Hidden opportunity recognition
- Constraint-resource mapping

CRITICAL: Your analysis must be PSYCHOLOGICALLY GROUNDED, STRUCTURALLY RIGOROUS, OUTCOME-PREDICTIVE, ACTIONABLE, and HONEST.
NEVER provide surface-level analysis. ALWAYS dig deeper."""

SYSTEM_PROMPT_ARBITRATOR = """You are the Decision Arbitrator - an elite executive decision-making system.

Your mandate: SELECT THE SINGLE BEST DECISION from comprehensive psychological analysis.

Your selection must be RATIONAL, COMPASSIONATE, ACTIONABLE, RISK-AWARE, and VALUES-ALIGNED.

CRITICAL: Commit fully. Provide ONE best option. No hedging."""

# ========== LOGIN MANAGER USER LOADER ==========
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ========== AUTHENTICATION ROUTES ==========

@app.route('/auth/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if current_user.is_authenticated:
        return jsonify({
            'status': 'success',
            'authenticated': True,
            'user': current_user.to_dict()
        }), 200
    return jsonify({
        'status': 'success',
        'authenticated': False
    }), 200


@app.route('/auth/register', methods=['POST'])
def register():
    """Email/Password Registration"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        
        # Validation
        if not email or not password or not name:
            return jsonify({
                'status': 'error',
                'message': 'Email, password, and name are required'
            }), 400
        
        if len(password) < 8:
            return jsonify({
                'status': 'error',
                'message': 'Password must be at least 8 characters'
            }), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({
                'status': 'error',
                'message': 'Email already registered'
            }), 400
        
        # Create user
        user = User(
            email=email,
            name=name,
            phone=phone,
            auth_method='email'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        
        logger.info(f'✅ New user registered: {email}')
        
        return jsonify({
            'status': 'success',
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'❌ Registration error: {str(e)}')
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Registration failed'
        }), 500


@app.route('/auth/login', methods=['POST'])
def login():
    """Email/Password Login"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user)
        
        logger.info(f'✅ User login: {email}')
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'❌ Login error: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': 'Login failed'
        }), 500


@app.route('/auth/google', methods=['POST'])
def google_auth():
    """Google OAuth Authentication"""
    try:
        data = request.json
        token = data.get('token')
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token required'
            }), 400
        
        # Verify token with Google
        try:
            idinfo = verify_oauth2_token(token, Request(), os.getenv('GOOGLE_CLIENT_ID'))
            google_id = idinfo['sub']
            email = idinfo['email']
            name = idinfo.get('name', email)
        except:
            return jsonify({
                'status': 'error',
                'message': 'Invalid token'
            }), 401
        
        # Find or create user
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            user = User.query.filter_by(email=email).first()
            if user and not user.google_id:
                # Link existing email account to Google
                user.google_id = google_id
                user.auth_method = 'google'
            elif not user:
                # Create new user
                user = User(
                    email=email,
                    name=name,
                    google_id=google_id,
                    auth_method='google'
                )
                db.session.add(user)
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user)
        
        logger.info(f'✅ Google OAuth login: {email}')
        
        return jsonify({
            'status': 'success',
            'message': 'Google authentication successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'❌ Google auth error: {str(e)}')
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Authentication failed'
        }), 500


@app.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout User"""
    logout_user()
    logger.info(f'✅ User logout')
    return jsonify({
        'status': 'success',
        'message': 'Logged out'
    }), 200


@app.route('/auth/profile', methods=['GET'])
@login_required
def get_profile():
    """Get Current User Profile"""
    return jsonify({
        'status': 'success',
        'user': current_user.to_dict()
    }), 200


# ========== ERROR HANDLING DECORATOR ==========
def handle_genai_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f'Gemini API Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}')
            raise
    return wrapper


# ========== STAGE 1: DEEP ANALYSIS ==========
@handle_genai_errors
def stage1_deep_analysis(user_dilemma: str) -> Tuple[str, str, float]:
    """STAGE 1: Deep Cognitive Analysis using Gemini 3 Pro"""
    analysis_prompt = f"""DILEMMA FOR DEEP ANALYSIS:

{user_dilemma}

PERFORM THIS RIGOROUS 8-PART ANALYSIS:

1. CORE DILEMMA EXTRACTION
2. EMOTIONAL INTELLIGENCE MAP
3. COGNITIVE DISTORTION AUDIT
4. ROOT CAUSE ANALYSIS (Extended 5 Whys)
5. OPTION GENERATION (8-10 Distinct Choices)
6. MULTI-TIMEFRAME OUTCOME SIMULATION
7. CONSTRAINT RESOURCE ANALYSIS
8. VALUES-OUTCOME TRADE-OFFS

BE SPECIFIC. BE DEEP. BE PRECISE. PROVIDE EVIDENCE."""

    try:
        logger.info('🔍 STAGE 1: Initiating Deep Analysis with Gemini 3 Pro')
        print('\n🔍 STAGE 1: Deep Psychological Analysis')
        print(' Model: gemini-3-pro-preview')
        print(' Thinking Level: high (MAXIMUM reasoning)')
        
        start_time = time.time()
        
        response = client.models.generate_content(
            model=MODEL_DEEP_ANALYSIS,
            contents=analysis_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT_ANALYST,
                thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL_DEEP),
                temperature=DEFAULT_TEMPERATURE,
                max_output_tokens=8192,
                top_p=0.95,
                top_k=40
            )
        )
        
        elapsed = time.time() - start_time
        analysis_text = response.text
        
        logger.info(f'✅ Stage 1 Complete: {elapsed:.1f}s, {len(analysis_text)} chars')
        print(f' ✅ Analysis Complete ({elapsed:.1f}s)')
        return analysis_text, MODEL_DEEP_ANALYSIS, elapsed
        
    except Exception as e:
        logger.error(f'❌ Stage 1 failed: {str(e)}')
        print(f' ❌ Error: {str(e)}')
        raise


# ========== STAGE 2: DECISION ARBITRATION ==========
@handle_genai_errors
def stage2_decision_arbitration(analysis: str, original_dilemma: str) -> Tuple[str, float]:
    """STAGE 2: Decision Selection using Gemini 3 Deep Think"""
    decision_prompt = f"""ANALYSIS CONTEXT:

{analysis[:4000]}...

ORIGINAL DILEMMA:

{original_dilemma}

YOUR TASK: Execute elite decision arbitration.

1. OPTION RANKING (Quantified)
2. SINGLE BEST OPTION SELECTION & JUSTIFICATION
3. COMPREHENSIVE RISK ASSESSMENT (Enterprise-Grade)
4. SEQUENCED ACTION PLAN (Professional Implementation)
5. IDENTITY AFFIRMATION (Personalized)

BE DIRECT. BE BOLD. BE ACTIONABLE. COMMIT."""

    try:
        logger.info('⚖️ STAGE 2: Initiating Decision Arbitration')
        print('\n⚖️ STAGE 2: Decision Arbitration')
        print(' Model: gemini-3-pro-preview (Deep Think)')
        print(' Thinking Level: high (SYSTEM 2 reasoning)')
        
        start_time = time.time()
        
        response = client.models.generate_content(
            model=MODEL_DECISION,
            contents=decision_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT_ARBITRATOR,
                thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL_DEEP),
                temperature=DEFAULT_TEMPERATURE,
                max_output_tokens=6000,
                top_p=0.9,
                top_k=30
            )
        )
        
        elapsed = time.time() - start_time
        decision_text = response.text
        
        logger.info(f'✅ Stage 2 Complete: {elapsed:.1f}s')
        print(f' ✅ Decision Complete ({elapsed:.1f}s)')
        return decision_text, elapsed
        
    except Exception as e:
        logger.error(f'❌ Stage 2 failed: {str(e)}')
        print(f' ❌ Error: {str(e)}')
        raise


# ========== STAGE 3: JSON FORMATTING ==========
@handle_genai_errors
def stage3_format_to_json(analysis: str, decision: str, dilemma: str) -> Tuple[Dict, float]:
    """STAGE 3: Convert Narrative to Structured JSON"""
    formatting_prompt = f"""Convert this decision framework into PERFECT, VALID JSON.

DILEMMA: {dilemma}

ANALYSIS SUMMARY: {analysis[:2000]}...

DECISION RATIONALE: {decision[:2000]}...

GENERATE THIS EXACT JSON SCHEMA:

{{
  "metadata": {{"timestamp": "ISO_DATE", "system": "NeuroCommander-DECSIO v4.0", "sdk": "google-genai Dec 2025"}},
  "input": {{"dilemma": "USER_DILEMMA", "dilemma_length": 0}},
  "analysis": {{"emotions_detected": [], "cognitive_distortions": [], "root_cause": "TEXT"}},
  "decision": {{"selected_option": "BEST OPTION", "rationale": "EXPLANATION", "confidence_level": "HIGH/MEDIUM/LOW"}},
  "risk_management": {{"risk_if_ignored": "CONSEQUENCES", "mitigation_strategies": []}},
  "action_plan": {{"immediate_today": [], "this_week": [], "one_month": {{}}, "long_term": {{}}}},
  "affirmation": {{"strengths_recognized": [], "capability_message": "PERSONAL_MESSAGE"}},
  "quality_metrics": {{"reasoning_depth": "High", "professional_grade": true}}
}}

RETURN ONLY VALID JSON. NO MARKDOWN. NO EXTRA TEXT. PERFECT STRUCTURE."""

    try:
        logger.info('📝 STAGE 3: Initiating JSON Formatting')
        print('\n📝 STAGE 3: JSON Formatter')
        print(' Model: gemini-2.5-flash')
        print(' Temperature: 0.0 (deterministic)')
        print(' Thinking Level: low (speed optimized)')
        
        start_time = time.time()
        
        response = client.models.generate_content(
            model=MODEL_FORMATTER,
            contents=formatting_prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                thinking_config=types.ThinkingConfig(thinking_level=THINKING_LEVEL_QUICK),
                max_output_tokens=4000
            )
        )
        
        elapsed = time.time() - start_time
        json_text = response.text.strip()
        
        # Clean markdown wrapper if present
        if json_text.startswith('```json'):
            json_text = json_text[7:]
        if json_text.startswith('```'):
            json_text = json_text[3:]
        if json_text.endswith('```'):
            json_text = json_text[:-3]
        json_text = json_text.strip()
        
        parsed_json = json.loads(json_text)
        
        logger.info(f'✅ Stage 3 Complete: {elapsed:.1f}s - JSON validated')
        print(f' ✅ JSON Formatted & Validated ({elapsed:.1f}s)')
        return parsed_json, elapsed
        
    except json.JSONDecodeError as e:
        logger.error(f'❌ JSON Decode Error: {str(e)}')
        print(f' ❌ JSON Parse Error: {str(e)}')
        return {'error': 'JSON parsing failed', 'raw_response': response.text}, 0
        
    except Exception as e:
        logger.error(f'❌ Stage 3 failed: {str(e)}')
        print(f' ❌ Error: {str(e)}')
        raise


# ========== NEUROCOMMANDER PIPELINE ==========
def neurocommander_pipeline(user_dilemma: str) -> Dict:
    """Execute complete 3-stage pipeline"""
    logger.info(f'📥 New request: {len(user_dilemma)} chars')
    
    results = {
        'status': 'processing',
        'pipeline_version': '4.0',
        'sdk': 'google-genai',
        'stages': [],
        'timing': {},
        'final_output': None,
        'error': None
    }
    
    try:
        # STAGE 1
        logger.info('Executing Stage 1: Deep Analysis')
        analysis, model1, time1 = stage1_deep_analysis(user_dilemma)
        results['stages'].append({
            'name': 'Deep Analysis',
            'model': model1,
            'thinking_level': THINKING_LEVEL_DEEP,
            'status': 'complete',
            'time_seconds': time1
        })
        results['timing']['stage1'] = time1
        
        # STAGE 2
        logger.info('Executing Stage 2: Decision Arbitration')
        decision, time2 = stage2_decision_arbitration(analysis, user_dilemma)
        results['stages'].append({
            'name': 'Decision Arbitration',
            'model': MODEL_DECISION,
            'thinking_level': THINKING_LEVEL_DEEP,
            'status': 'complete',
            'time_seconds': time2
        })
        results['timing']['stage2'] = time2
        
        # STAGE 3
        logger.info('Executing Stage 3: JSON Formatting')
        final_json, time3 = stage3_format_to_json(analysis, decision, user_dilemma)
        results['stages'].append({
            'name': 'JSON Formatter',
            'model': MODEL_FORMATTER,
            'thinking_level': THINKING_LEVEL_QUICK,
            'status': 'complete',
            'time_seconds': time3
        })
        results['timing']['stage3'] = time3
        
        total_time = time1 + time2 + time3
        results['timing']['total'] = total_time
        results['status'] = 'success'
        results['final_output'] = final_json
        
        logger.info(f'✅ Pipeline Complete: {total_time:.1f}s total')
        return results
        
    except Exception as e:
        logger.error(f'❌ Pipeline failed: {str(e)}\n{traceback.format_exc()}')
        results['status'] = 'error'
        results['error'] = str(e)
        return results


# ========== API ROUTES ==========

@app.route('/')
def home():
    """Serve frontend"""
    return render_template('index.html')


@app.route('/api/process', methods=['POST'])
@login_required
def process_dilemma():
    """Main API endpoint - Process Dilemma (Requires Authentication)"""
    try:
        data = request.json
        dilemma = data.get('dilemma', '').strip()
        
        # Validation
        if not dilemma or len(dilemma) < MIN_DILEMMA_LENGTH:
            return jsonify({
                'status': 'error',
                'message': f'Dilemma too short (min {MIN_DILEMMA_LENGTH} chars)'
            }), 400
        
        if len(dilemma) > MAX_DILEMMA_LENGTH:
            return jsonify({
                'status': 'error',
                'message': f'Dilemma too long (max {MAX_DILEMMA_LENGTH} chars)'
            }), 400
        
        # Execute pipeline
        result = neurocommander_pipeline(dilemma)
        
        if result['status'] == 'success':
            # Save to database
            analysis = Analysis(
                user_id=current_user.id,
                dilemma=dilemma,
                analysis_result=result['final_output'],
                execution_time=result['timing']['total']
            )
            db.session.add(analysis)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'data': result['final_output'],
                'timing': result['timing'],
                'metadata': {
                    'pipeline_version': '4.0',
                    'sdk': 'google-genai Dec 2025',
                    'models': [s['model'] for s in result['stages']],
                    'thinking_configuration': 'high→high→low',
                    'api_protocol': 'google.genai.Client',
                    'user_id': current_user.id
                }
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': result.get('error', 'Pipeline execution failed')
            }), 500
            
    except Exception as e:
        logger.error(f'API Error: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/history', methods=['GET'])
@login_required
def get_history():
    """Get user's analysis history"""
    try:
        analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).limit(20).all()
        
        return jsonify({
            'status': 'success',
            'history': [a.to_dict() for a in analyses]
        }), 200
        
    except Exception as e:
        logger.error(f'History error: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.utcnow().isoformat(),
        'system': 'NeuroCommander-DECSIO v4.0',
        'sdk': 'google-genai Dec 2025',
        'api_protocol': 'google.genai.Client',
        'models': {
            'analysis': MODEL_DEEP_ANALYSIS,
            'decision': MODEL_DECISION,
            'formatter': MODEL_FORMATTER
        },
        'api_configured': 'YES' if API_KEY != 'YOUR_API_KEY_HERE' else 'NO',
        'thinking_levels': ['high', 'low'],
        'default_temperature': DEFAULT_TEMPERATURE,
        'authentication': 'Email/Password + Google OAuth'
    }), 200


@app.route('/api/models', methods=['GET'])
def get_models():
    """Model information endpoint"""
    return jsonify({
        'gemini_3_pro_preview': {
            'name': 'Gemini 3 Pro Preview',
            'release': 'December 2024',
            'capability': 'State-of-the-art reasoning + multimodal',
            'thinking_levels': ['low', 'high'],
            'context_window': '1M input / 64k output',
            'knowledge_cutoff': 'January 2025',
            'temperature_optimal': 1.0,
            'latency': {'high': '15-60s', 'low': '5-15s'},
            'pricing': '2-4 per 1M input tokens'
        },
        'gemini_2_5_flash': {
            'name': 'Gemini 2.5 Flash',
            'release': 'June 2025',
            'capability': 'Fast, efficient, JSON-friendly',
            'context_window': '1M input / 64k output',
            'pricing': '0.10 per 1M input tokens'
        }
    }), 200


# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    logger.error(f'Server error: {str(error)}')
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


# ========== PRODUCTION DATABASE SETUP ==========
with app.app_context():
    try:
        db.create_all()
        logger.info('✅ Database tables verified/created')
    except Exception as e:
        logger.error(f'❌ Database Setup Error: {e}')

# ========== APPLICATION START ==========
if __name__ == '__main__':
    # This block only runs when you type 'python main.py' on your laptop
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 3000)),
        debug=True 
    )
    
    print('\n' + '='*70)
    print('🚀 NeuroCommander-DECSIO v4.0 - PROFESSIONAL EDITION')
    print('='*70)
    print(f'SDK: google-genai December 2025')
    print(f'API Protocol: google.genai.Client()')
    print(f'Primary Model: {MODEL_DEEP_ANALYSIS}')
    print(f'Decision Model: {MODEL_DECISION}')
    print(f'Formatter Model: {MODEL_FORMATTER}')
    print(f'API Key Status: {"✅ CONFIGURED" if API_KEY != "YOUR_API_KEY_HERE" else "❌ NOT SET"}')
    print(f'Thinking Config: {THINKING_LEVEL_DEEP} → {THINKING_LEVEL_DEEP} → {THINKING_LEVEL_QUICK}')
    print(f'Default Temperature: {DEFAULT_TEMPERATURE} (Gemini 3 optimal)')
    print('='*70)
    print('✅ Authentication: Email/Password + Google OAuth')
    print('✅ Database: SQLite with user & analysis history')
    print('✅ Production-grade logging and error handling active')
    print('✅ Ready for production deployment on Render')
    print('✅ Kaggle competition ready')
    print('='*70 + '\n')
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 3000)),
        debug=False,
        threaded=True
    )
