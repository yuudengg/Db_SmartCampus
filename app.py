import sqlite3
from flask import Flask, jsonify, request, session, redirect, url_for, g, flash
from datetime import datetime, date, timedelta # date, timedelta 추가

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_strong_secret_key_here' 
app.config['JSON_AS_ASCII'] = False 
DATABASE = 'db_project_table' 

# === [추가된 전역 변수] ===
# 일일 처리 로직이 하루에 한 번만 실행되도록 체크하는 변수
LAST_DAILY_PROCESS_DATE = None 
# =========================

# -----------------------------------------------------------
# DB 유틸리티 및 도우미 함수 
# -----------------------------------------------------------
def get_db_connection():
    """요청별 DB 연결 관리 및 외래 키 활성화"""
    if 'db' not in g:
        try:
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = sqlite3.Row 
            conn.execute('PRAGMA foreign_keys = ON') 
            g.db = conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            g.db = None
    return g.db

@app.teardown_appcontext
def close_db_connection(exception):
    """요청 종료 시 DB 연결 닫기"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def login_required(f):
    """로그인 확인 데코레이터"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and 'admin_id' not in session:
            return redirect(url_for('select_login_type'))
        return f(*args, **kwargs)
    return decorated_function

# === [추가된 헬퍼 함수 1: 벌점 유효 일수 계산 로직 (자동 감소 효과)] ===
def get_total_active_penalty_days(conn, user_id):
    """
    벌점 기간 및 벌점 부여 날짜를 이용해 유효 벌점 일수를 계산합니다.
    (벌점 시작일 이후 경과된 일수만큼 차감)
    """
    penalties = conn.execute("""
        SELECT penalty_period, penalty_date 
        FROM Penalty 
        WHERE user_id = ? AND released = 0
    """, (user_id,)).fetchall()
    
    today = datetime.now().date()
    total_effective_penalty = 0
    
    for p in penalties:
        # DB에 저장된 날짜는 TEXT (%Y-%m-%d)
        penalty_date = datetime.strptime(p['penalty_date'], '%Y-%m-%d').date()
        
        # 경과 일수 계산: 오늘 날짜 - 벌점 부여 날짜. (하루가 지나야 1일 감소 효과)
        days_passed = (today - penalty_date).days
        
        # 잔여 벌점 일수 계산 (0일 미만 방지)
        # 예: penalty_period가 3일이고, 경과 일수가 1일이면 2일 남음
        remaining = max(0, p['penalty_period'] - days_passed)
        total_effective_penalty += remaining
        
    return total_effective_penalty

# === [추가된 헬퍼 함수 2: 일일 처리 로직 (노쇼 확인 및 벌점 부과)] ===
def process_daily_tasks(conn):
    """
    하루에 한 번만 실행되는 노쇼 확인 및 벌점 부과 로직.
    - 예약 종료 시간 이후 '사용 확인'이 되지 않은 예약을 '노쇼' 처리
    - 노쇼 3회 누적 시 3일 이용 제한 부과 및 노쇼 카운트 초기화
    """
    
    # 1. 예약 종료 후 '사용 확인'이 되지 않은 예약을 '노쇼' 처리합니다.
    now = datetime.now()
    now_dt_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # 노쇼 처리 대상: 예약됨 상태, 사용 확인(usage_status)이 안 되었고, 예약 종료 시간이 현재보다 이른 경우
    # Note: 예약 종료 시간이 지난 경우에도 '노쇼' 대신 '예약됨'으로 표시될 수 있으므로, dashboard에서 이 함수를 주기적으로 호출해야 함.
    no_show_targets = conn.execute("""
        SELECT R.reservation_id, R.user_id 
        FROM Reservation R
        WHERE R.status = '예약됨' AND R.usage_status = 0
          AND (R.reservation_date || ' ' || R.end_time) < ?
    """, (now_dt_str,)).fetchall()

    for target in no_show_targets:
        user_id = target['user_id']
        
        # 1-1. '노쇼' 상태로 업데이트
        conn.execute("UPDATE Reservation SET status = '노쇼' WHERE reservation_id = ?", (target['reservation_id'],))
        
        # 1-2. 해당 사용자의 '노쇼' 횟수 체크 (status='노쇼'인 것만 카운트)
        no_show_count = conn.execute(
            "SELECT COUNT(*) AS count FROM Reservation WHERE user_id = ? AND status = '노쇼'", 
            (user_id,)
        ).fetchone()['count']
        
        # 1-3. 노쇼 횟수 3회 도달 시 이용 제한 부과 및 기존 '노쇼' 상태를 '노쇼-처리됨'으로 변경하여 카운트 초기화 효과
        if no_show_count >= 3:
            # 이용 제한 3일 추가 (Penalty 테이블에 추가)
            conn.execute("""
                INSERT INTO Penalty (user_id, reason, penalty_date, penalty_period, released)
                VALUES (?, ?, ?, ?, 0)
            """, (user_id, '자동 노쇼 3회 누적으로 인한 3일 이용 제한', now.strftime('%Y-%m-%d'), 3))
            
            # 카운트 초기화 효과: 이미 누적된 '노쇼' 기록들을 '노쇼-처리됨'으로 변경하여 다음 카운트에 포함되지 않도록 함
            conn.execute("UPDATE Reservation SET status = '노쇼-처리됨' WHERE user_id = ? AND status = '노쇼'", (user_id,))

    conn.commit()
# =========================================

# -----------------------------------------------------------
# 인증, 메인 및 회원가입 (변경 없음)
# -----------------------------------------------------------

@app.route('/')
def select_login_type():
    """메인 페이지: 사용자/관리자 로그인 선택"""
    if 'user_id' in session or 'admin_id' in session:
        return redirect(url_for('dashboard'))
        
    html = f"""
    <!DOCTYPE html>
    <title>공간 예약 시스템</title>
    <h1>공간 예약 시스템</h1>
    <h2>로그인 선택</h2>
    <ul>
        <li><a href="{url_for('user_login')}">사용자 로그인 (학생/교수)</a></li>
        <li><a href="{url_for('admin_login')}">관리자 로그인 (관리자 번호)</a></li>
    </ul>
    """
    return html

@app.route('/login/user', methods=['GET', 'POST'])
def user_login():
    """사용자 로그인 (학생/교수)"""
    if request.method == 'POST':
        login_id = request.form.get('login_id')
        password = request.form.get('password')
        conn = get_db_connection()
        
        if not conn: return "<h1>DB 연결 오류!</h1>", 500
        
        user = conn.execute(
            "SELECT user_id, name, role FROM User WHERE login_id = ? AND password = ?",
            (login_id, password)
        ).fetchone()
        
        if user:
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            error = "ID 또는 비밀번호가 올바르지 않습니다."
            
    error = locals().get('error', '')
    
    html = f"""
    <!DOCTYPE html>
    <title>사용자 로그인</title>
    <h1>사용자 로그인 (학생/교수)</h1>
    <a href="{url_for('select_login_type')}">메인으로 돌아가기</a>
    <p style="color:red">{error}</p>
    <form method="POST">
        <label for="login_id">ID:</label><br>
        <input type="text" id="login_id" name="login_id" required><br><br>
        <label for="password">PW:</label><br>
        <input type="password" id="password" name="password" required><br><br>
        <button type="submit">로그인</button>
    </form>
    <hr>
    <p>계정이 없으신가요? <a href="{url_for('register')}">회원가입</a></p>
    """
    return html

@app.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    """관리자 로그인 (관리자 번호만)"""
    if request.method == 'POST':
        admin_id = request.form.get('admin_id')
        conn = get_db_connection()
        
        if not conn: return "<h1>DB 연결 오류!</h1>", 500
        
        admin = conn.execute(
            "SELECT admin_id, name FROM Admin WHERE admin_id = ?",
            (admin_id,)
        ).fetchone()
        
        if admin:
            session['admin_id'] = admin['admin_id']
            session['name'] = admin['name']
            session['role'] = '관리자'
            return redirect(url_for('dashboard'))
        else:
            error = "관리자 번호가 올바르지 않습니다."
            
    error = locals().get('error', '')
    
    html = f"""
    <!DOCTYPE html>
    <title>관리자 로그인</title>
    <h1>관리자 로그인</h1>
    <a href="{url_for('select_login_type')}">메인으로 돌아가기</a>
    <p style="color:red">{error}</p>
    <form method="POST">
        <label for="admin_id">관리자 번호:</label><br>
        <input type="text" id="admin_id" name="admin_id" required><br><br>
        <button type="submit">로그인</button>
    </form>
    """
    return html


@app.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입 페이지 (역할에 따른 필드 동적 제어)"""
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form.get('name')
        login_id = request.form.get('login_id')
        password = request.form.get('password')
        role = request.form.get('role')
        detail_id = request.form.get('detail_id') 
        dept = request.form.get('department') 
        
        try:
            # 1. User 테이블에 삽입
            cursor = conn.execute(
                "INSERT INTO User (name, role, login_id, password) VALUES (?, ?, ?, ?)",
                (name, role, login_id, password)
            )
            user_id = cursor.lastrowid
            
            # 2. Student 또는 Professor 테이블에 상세 정보 삽입
            if role == '학생':
                grade = request.form.get('grade')
                conn.execute(
                    "INSERT INTO Student (student_id, user_id, grade, major) VALUES (?, ?, ?, ?)",
                    (detail_id, user_id, grade, dept)
                )
            elif role == '교수':
                position = request.form.get('position')
                conn.execute(
                    "INSERT INTO Professor (professor_id, user_id, position, department) VALUES (?, ?, ?, ?)",
                    (detail_id, user_id, position, dept)
                )
            
            conn.commit()
            return f"<h1>회원가입 성공!</h1><p>{name}님 ({role})의 계정이 생성되었습니다. <a href='{url_for('user_login')}'>로그인</a> 해주세요.</p>"
            
        except sqlite3.IntegrityError:
            conn.rollback()
            error = "이미 존재하는 ID 또는 학번/교번입니다."
        except Exception as e:
            conn.rollback()
            error = f"회원가입 중 오류 발생: {e}"

    error = locals().get('error', '')
    
    html = f"""
    <!DOCTYPE html>
    <title>회원가입</title>
    <script>
        function updateFields() {{
            const role = document.getElementById('role').value;
            const studentFields = document.getElementById('student_fields');
            const professorFields = document.getElementById('professor_fields');
            const detailLabel = document.getElementById('detail_label');
            
            detailLabel.textContent = (role === '학생') ? '학번:' : '교번:';

            if (role === '학생') {{
                studentFields.style.display = 'block';
                professorFields.style.display = 'none';
                document.getElementById('grade').required = true;
                document.getElementById('position').required = false;
            }} else if (role === '교수') {{
                studentFields.style.display = 'none';
                professorFields.style.display = 'block';
                document.getElementById('grade').required = false;
                document.getElementById('position').required = true;
            }}
        }}
    </script>
    <h1>회원가입 (학생/교수)</h1>
    <p style="color:red">{error}</p>
    <form method="POST">
        <label>이름:</label><br><input type="text" name="name" required><br><br>
        
        <label>회원 구분:</label><br>
        <select name="role" id="role" onchange="updateFields()" required>
            <option value="학생">학생</option>
            <option value="교수">교수</option>
        </select><br><br>
        
        <label>로그인 ID:</label><br><input type="text" name="login_id" required><br><br>
        <label>비밀번호:</label><br><input type="password" name="password" required><br><br>
        
        <label id="detail_label">학번:</label><br><input type="text" name="detail_id" required><br><br>
        <label>학과 / 부서:</label><br><input type="text" name="department" required><br><br>

        <div id="student_fields">
            <label>학년:</label><br><input type="number" name="grade" id="grade" min="1" max="4" required><br><br>
        </div>
        
        <div id="professor_fields" style="display:none;">
            <label>직위:</label><br><input type="text" name="position" id="position"><br><br>
        </div>
        
        <button type="submit">가입하기</button>
    </form>
    <hr>
    <p><a href="{url_for('user_login')}">로그인 화면으로</a></p>
    <script>updateFields();</script>
    """
    return html

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('select_login_type'))

# -----------------------------------------------------------
# 정보 수정 라우트 (변경 없음)
# -----------------------------------------------------------

@app.route('/profile/user', methods=['GET', 'POST'])
@login_required
def user_profile():
    """사용자(학생/교수) 정보 수정"""
    if 'user_id' not in session: 
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    user_id = session['user_id']
    role = session['role']
    message = ""
    
    # POST handling: 정보 수정
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_login_id = request.form.get('login_id')
        new_password = request.form.get('password')
        new_dept = request.form.get('department')
        
        try:
            # 1. 로그인 ID 중복 체크 (현재 사용자 제외)
            check_id = conn.execute("SELECT user_id FROM User WHERE login_id = ? AND user_id != ?", (new_login_id, user_id)).fetchone()
            if check_id:
                raise ValueError("입력하신 ID는 이미 다른 사용자가 사용 중입니다.")

            # 2. User 테이블 업데이트 (이름, ID, 비밀번호)
            conn.execute(
                "UPDATE User SET name = ?, login_id = ?, password = ? WHERE user_id = ?",
                (new_name, new_login_id, new_password, user_id)
            )
            
            # 3. 상세 정보 테이블 업데이트
            if role == '학생':
                new_grade = request.form.get('grade')
                conn.execute(
                    "UPDATE Student SET major = ?, grade = ? WHERE user_id = ?",
                    (new_dept, new_grade, user_id)
                )
            elif role == '교수':
                new_position = request.form.get('position')
                conn.execute(
                    "UPDATE Professor SET department = ?, position = ? WHERE user_id = ?",
                    (new_dept, new_position, user_id)
                )

            conn.commit()
            
            # 세션 정보 업데이트
            session['name'] = new_name 
            
            message = "✅ 회원 정보가 성공적으로 수정되었습니다."

        except ValueError as e:
            conn.rollback()
            message = f"❌ 정보 수정 실패: {e}"
        except Exception as e:
            conn.rollback()
            message = f"❌ 정보 수정 중 오류 발생: {e}"


    # GET handling / Data fetching: 현재 정보 불러오기
    user = conn.execute("SELECT name, login_id, password FROM User WHERE user_id = ?", (user_id,)).fetchone()
    
    detail = None
    if role == '학생':
        detail = conn.execute("SELECT student_id, major, grade FROM Student WHERE user_id = ?", (user_id,)).fetchone()
    elif role == '교수':
        detail = conn.execute("SELECT professor_id, department, position FROM Professor WHERE user_id = ?", (user_id,)).fetchone()

    if not user or not detail:
        return "사용자 정보를 불러올 수 없습니다.", 404

    # HTML 렌더링
    html = f"""
    <!DOCTYPE html>
    <title>{role} 정보 수정</title>
    <h1>{role} 정보 수정</h1>
    <a href="{url_for('dashboard')}">대시보드로 돌아가기</a>
    <p style="color:{'green' if '성공' in message else 'red'};">{message}</p>
    <form method="POST">
        <h2>기본 정보 (수정 가능)</h2>
        <label>이름:</label><br>
        <input type="text" name="name" value="{user['name']}" required><br><br>
        
        <label>로그인 ID:</label><br>
        <input type="text" name="login_id" value="{user['login_id']}" required><br><br>
        
        <label>비밀번호:</label><br>
        <input type="password" name="password" value="{user['password']}" required><br><br>
        
        <h2>{role} 상세 정보</h2>
    """
    
    if role == '학생':
        html += f"""
        <label>학번 (수정불가):</label><br>
        <input type="text" value="{detail['student_id']}" disabled><br><br>
        
        <label>학과:</label><br>
        <input type="text" name="department" value="{detail['major']}" required><br><br>
        
        <label>학년:</label><br>
        <input type="number" name="grade" min="1" max="4" value="{detail['grade']}" required><br><br>
        """
    elif role == '교수':
        html += f"""
        <label>교번 (수정불가):</label><br>
        <input type="text" value="{detail['professor_id']}" disabled><br><br>
        
        <label>부서:</label><br>
        <input type="text" name="department" value="{detail['department']}" required><br><br>
        
        <label>직위:</label><br>
        <input type="text" name="position" value="{detail['position']}" required><br><br>
        """
    
    html += """
        <button type="submit">정보 수정 완료</button>
    </form>
    """
    return html

@app.route('/profile/admin', methods=['GET', 'POST'])
@login_required
def admin_profile():
    """관리자 정보 수정"""
    if 'admin_id' not in session:
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    admin_id = session['admin_id']
    message = ""

    # POST handling: 정보 수정
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_department = request.form.get('department') 

        try:
            # Admin 테이블 업데이트 (이름, 부서명)
            cursor = conn.execute(
                "UPDATE Admin SET name = ?, department = ? WHERE admin_id = ?",
                (new_name, new_department, admin_id)
            )
            conn.commit()
            
            if cursor.rowcount > 0:
                 # 세션 정보 업데이트
                session['name'] = new_name 
                message = "✅ 관리자 정보가 성공적으로 수정되었습니다."
            else:
                 message = "❌ 정보 수정 실패: 관리자 정보를 찾을 수 없거나 변경 사항이 없습니다."

        except Exception as e:
            conn.rollback()
            message = f"❌ 정보 수정 중 오류 발생: {e}" 

    # GET handling / Data fetching: 현재 정보 불러오기
    admin = conn.execute(
        "SELECT admin_id, name, department FROM Admin WHERE admin_id = ?", 
        (admin_id,)
    ).fetchone()

    if not admin:
        return "관리자 정보를 불러올 수 없습니다.", 404

    # HTML 렌더링
    html = f"""
    <!DOCTYPE html>
    <title>관리자 정보 수정</title>
    <h1>관리자 정보 수정</h1>
    <a href="{url_for('dashboard')}">대시보드로 돌아가기</a>
    <p style="color:{'green' if '성공' in message else 'red'};">{message}</p>
    <form method="POST">
        <label>관리자 번호 (수정불가):</label><br>
        <input type="text" value="{admin['admin_id']}" disabled><br><br>
        
        <label>이름:</label><br>
        <input type="text" name="name" value="{admin['name']}" required><br><br>
        
        <label>부서명:</label><br>
        <input type="text" name="department" value="{admin['department']}" required><br><br> 
        
        <button type="submit">정보 수정 완료</button>
    </form>
    """
    return html


# -----------------------------------------------------------
# 관리자 기능 라우트
# -----------------------------------------------------------

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_user_management():
    """관리자: 사용자 목록 조회 및 이용 제한 부과 (벌점) - 누적 일수 직접 지정 기능으로 수정"""
    if 'admin_id' not in session: return redirect(url_for('dashboard'))
    conn = get_db_connection()
    message = ""

    # POST handling: Set Total Restriction Days
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'set_total_penalty':
            user_id_to_manage = request.form.get('user_id')
            total_days_str = request.form.get('total_days')
            
            try:
                total_days = int(total_days_str)
                if total_days < 0:
                    raise ValueError("벌점 일수는 0일 이상이어야 합니다.")

                user_name_row = conn.execute("SELECT name FROM User WHERE user_id = ?", (user_id_to_manage,)).fetchone()
                if not user_name_row:
                    message = "❌ 사용자 정보를 찾을 수 없습니다."
                    raise Exception("User not found.")
                user_name = user_name_row['name']

                # 1. 기존 활성 벌점 모두 해제 (released = 1)
                conn.execute("""
                    UPDATE Penalty SET released = 1 
                    WHERE user_id = ? AND released = 0
                """, (user_id_to_manage,))

                if total_days > 0:
                    # 2. 새로운 총 벌점을 하나의 레코드로 추가 (벌점 부여일은 오늘 날짜로)
                    conn.execute("""
                        INSERT INTO Penalty (user_id, reason, penalty_date, penalty_period, released)
                        VALUES (?, ?, ?, ?, 0)
                    """, (user_id_to_manage, f'관리자 누적 벌점 강제 조정 ({total_days}일 설정)', datetime.now().strftime('%Y-%m-%d'), total_days))
                    conn.commit()
                    message = f"✅ {user_name} 사용자의 누적 벌점 (이용 제한 일수)이 **{total_days}일**로 성공적으로 설정되었습니다."
                else:
                    conn.commit()
                    message = f"✅ {user_name} 사용자의 모든 이용 제한이 **성공적으로 해제(0일 설정)**되었습니다."

            except ValueError as e:
                conn.rollback()
                message = f"❌ 벌점 설정 실패: {e}"
            except Exception as e:
                conn.rollback()
                message = f"❌ 벌점 설정 중 오류 발생: {e}"

    # GET handling: Fetch all users and their total active penalty days
    users = []
    try:
        cursor = conn.execute("""
            SELECT U.user_id, U.login_id, U.name, U.role
            FROM User U
            ORDER BY U.user_id
        """)
        
        for row in cursor.fetchall():
            user = dict(row)
            # === [수정된 부분: 유효 벌점 일수를 계산하는 함수 사용] ===
            user['total_penalty_days'] = get_total_active_penalty_days(conn, user['user_id'])
            users.append(user)
        # ==========================================================
            
    except Exception as e:
        message = f"❌ 사용자 리스트 조회 오류: {e}"

    # HTML Rendering
    html = f"""
    <!DOCTYPE html>
    <title>사용자 관리</title>
    <h1>사용자 관리 (이용 제한 설정/해제)</h1>
    <a href="{url_for('dashboard')}">대시보드로 돌아가기</a>
    <p style="color:{'green' if '✅' in message else 'red'};">{message}</p>
    
    <h2>사용자 목록 및 이용 제한 설정</h2>
    <p>**누적 벌점을 직접 입력하고 설정/해제할 수 있습니다.** (1일 이상이면 예약 불가능)</p>
    <p>0을 입력하고 설정 시 모든 활성 벌점은 해제됩니다.</p>
    <table border="1">
        <tr><th>User ID</th><th>로그인 ID</th><th>이름</th><th>역할</th><th>누적 벌점 (제한 일수)</th><th>이용 제한 설정/해제</th></tr>
    """
    
    for u in users:
        # 1일 이상이면 예약 불가 상태
        is_restricted = u['total_penalty_days'] > 0
        penalty_color = 'red' if is_restricted else 'green'
        
        # 관리자 본인에게는 벌점 부과 버튼을 표시하지 않음
        set_penalty_form = ""
        if u['user_id'] != session.get('user_id'): 
            set_penalty_form = f"""
            <form method="POST" style="display:inline;" onsubmit="return confirm('{u['name']} 사용자의 누적 벌점 일수를 설정하시겠습니까?');">
                <input type="hidden" name="action" value="set_total_penalty">
                <input type="hidden" name="user_id" value="{u['user_id']}">
                
                <label>총 제한 일수:</label>
                <input type="number" name="total_days" value="{u['total_penalty_days']}" min="0" required style="width:50px;">
                <button type="submit" style="color:red;">설정/해제</button>
            </form>
            """
        else:
            set_penalty_form = "N/A"
        
        html += f"""
        <tr>
            <td>{u['user_id']}</td>
            <td>{u['login_id']}</td>
            <td>{u['name']}</td>
            <td>{u['role']}</td>
            <td style="color:{penalty_color}; font-weight:bold;">{u['total_penalty_days']}일 ({'예약 불가' if is_restricted else '예약 가능'})</td>
            <td>{set_penalty_form}</td>
        </tr>
        """
    html += "</table>"
    return html


@app.route('/admin/space', methods=['GET', 'POST'])
@login_required
def admin_space_management():
    """관리자: 장소 목록 조회, 사용 중지 설정 및 취소"""
    if 'admin_id' not in session: return redirect(url_for('dashboard'))
    conn = get_db_connection()
    message = ""

    # POST handling: 사용 중지 설정 또는 취소
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'set_maintenance':
            space_id = request.form.get('space_id')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            
            if not all([space_id, start_date, end_date]):
                message = "❌ 사용 중지 시작일과 종료일을 모두 입력해야 합니다."
            else:
                try:
                    # Space_stop 테이블에 사용 중지 기록 추가 (admin_id 제거)
                    cursor = conn.execute("""
                        INSERT INTO Space_stop (space_id, start_date, end_date)
                        VALUES (?, ?, ?)
                    """, (space_id, start_date, end_date))
                    conn.commit()
                    
                    space_name = conn.execute("SELECT space_name FROM Space WHERE space_id = ?", (space_id,)).fetchone()['space_name']
                    message = f"✅ 공간 '{space_name}'에 대해 {start_date}부터 {end_date}까지 사용 중지가 설정되었습니다."

                except Exception as e:
                    conn.rollback()
                    message = f"❌ 사용 중지 설정 중 오류 발생: {e}"
                    
        elif action == 'cancel_maintenance':
            # stop_id로 변경
            stop_id = request.form.get('stop_id') 
            
            try:
                # Space_stop 테이블에서 해당 레코드를 삭제 (released 컬럼 없음)
                cursor = conn.execute("""
                    DELETE FROM Space_stop 
                    WHERE stop_id = ?
                """, (stop_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    message = f"✅ 사용 중지 번호 {stop_id}번이 성공적으로 해제(삭제)되었습니다."
                else:
                    message = f"❌ 사용 중지 해제 실패: {stop_id}번을 찾을 수 없습니다."
                    
            except Exception as e:
                conn.rollback()
                message = f"❌ 사용 중지 해제 중 오류 발생: {e}"

    # GET handling: Fetch all spaces and active maintenance list
    spaces = []
    active_maintenance = []
    
    try:
        # 모든 공간 목록 조회
        spaces_cursor = conn.execute("SELECT space_id, space_name, location, capacity, space_type FROM Space ORDER BY space_name")
        spaces = [dict(row) for row in spaces_cursor.fetchall()]

        # 현재 유효한 사용 중지 리스트 조회 (stop_id 사용, released 컬럼 없음)
        # 테이블에 존재하는 모든 레코드가 유효한 사용 중지 기록임.
        active_maintenance_cursor = conn.execute("""
            SELECT M.stop_id, S.space_name, M.start_date, M.end_date
            FROM Space_stop M
            JOIN Space S ON M.space_id = S.space_id
            ORDER BY M.start_date DESC
        """)
        active_maintenance = [dict(row) for row in active_maintenance_cursor.fetchall()]
        
    except Exception as e:
        message = f"❌ 공간/사용 중지 리스트 조회 오류: {e}"

    # HTML Rendering
    html = f"""
    <!DOCTYPE html>
    <title>장소 관리</title>
    <h1>장소 관리 (사용 중지 설정/해제)</h1>
    <a href="{url_for('dashboard')}">대시보드로 돌아가기</a>
    <p style="color:{'green' if '✅' in message else 'red'};">{message}</p>
    
    <h2>1. 장소 목록 및 사용 중지 설정</h2>
    <table border="1">
        <tr><th>ID</th><th>공간 이름</th><th>위치</th><th>수용 인원</th><th>사용 중지 설정</th></tr>
    """
    
    for s in spaces:
        html += f"""
        <tr>
            <td>{s['space_id']}</td>
            <td>{s['space_name']}</td>
            <td>{s['location']}</td>
            <td>{s['capacity']}명</td>
            <td>
                <form method="POST" style="display:inline;" onsubmit="return confirm('{s['space_name']}을 사용 중지 설정하시겠습니까?');">
                    <input type="hidden" name="action" value="set_maintenance">
                    <input type="hidden" name="space_id" value="{s['space_id']}">
                    시작일: <input type="date" name="start_date" required style="width:120px;">
                    종료일: <input type="date" name="end_date" required style="width:120px;">
                    <button type="submit" style="color:red;">중지 설정</button>
                </form>
            </td>
        </tr>
        """
    html += "</table>"

    html += """
    <h2>2. 사용 중지 리스트 및 해제 (남아있는 기록은 모두 유효한 사용 중지 기간임)</h2>
    <p>**해제 버튼을 누르면 해당 사용 중지 기록이 삭제되어 예약이 가능해집니다.**</p>
    <table border="1">
        <tr><th>번호 (stop_id)</th><th>공간 이름</th><th>시작일</th><th>종료일</th><th>상태</th><th>관리</th></tr>
    """
    
    for i, m in enumerate(active_maintenance, 1):
        # released 컬럼이 없으므로, 조회된 모든 레코드는 '사용 중지 중'임
        status_text = '**사용 중지 중**'
        status_color = 'red'
        
        cancel_button = f"""
            <form method="POST" style="display:inline;" onsubmit="return confirm('사용 중지 번호 {m['stop_id']}번을 정말 해제(삭제)하시겠습니까?');">
                <input type="hidden" name="action" value="cancel_maintenance">
                <input type="hidden" name="stop_id" value="{m['stop_id']}">
                <button type="submit" style="color:blue;">사용 중지 해제 (삭제)</button>
            </form>
            """
        
        html += f"""
        <tr>
            <td>{m['stop_id']}</td>
            <td>{m['space_name']}</td>
            <td>{m['start_date']}</td>
            <td>{m['end_date']}</td>
            <td style="color:{status_color};">{status_text}</td>
            <td>{cancel_button}</td>
        </tr>
        """
    html += "</table>"
    return html


@app.route('/admin/reservations', methods=['GET', 'POST'])
@login_required
def admin_reservation_management():
    """관리자: 예약 리스트 조회 및 강제 취소 (오류 수정: 과거 예약 취소 불가 및 상태 표시)"""
    if 'admin_id' not in session: return redirect(url_for('dashboard'))
    conn = get_db_connection()
    message = ""
    now = datetime.now() # 현재 시간
    now_dt_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # POST handling: Cancel Reservation (Admin cancels)
    if request.method == 'POST':
        reservation_id = request.form.get('cancel_id')
        if reservation_id:
            try:
                # 1. 예약 정보 조회
                reservation = conn.execute(
                    "SELECT reservation_date, end_time, status FROM Reservation WHERE reservation_id = ?", 
                    (reservation_id,)
                ).fetchone()

                if reservation:
                    if reservation['status'] not in ('예약됨', '사용 완료'):
                         message = f"❌ 예약 취소 실패: 예약번호 {reservation_id}번은 현재 상태가 '{reservation['status']}'이므로 취소할 수 없습니다."
                    else:
                        # 2. 예약 종료 시점 확인 (YYYY-MM-DD HH:MM:SS 포맷으로 비교)
                        res_end_dt_str = f"{reservation['reservation_date']} {reservation['end_time']}"
                        
                        if res_end_dt_str > now_dt_str: 
                            # 3. 예약이 아직 종료되지 않은 경우에만 취소 허용
                            cursor = conn.execute("""
                                UPDATE Reservation 
                                SET status = '관리자 취소' 
                                WHERE reservation_id = ? AND status IN ('예약됨', '사용 완료')
                            """, (reservation_id,))
                            conn.commit()
                            
                            if cursor.rowcount > 0:
                                message = f"✅ 예약번호 {reservation_id}번이 성공적으로 취소되었습니다. (관리자 취소)"
                            else:
                                # 이 경우는 거의 없겠지만, 만약을 대비
                                message = f"❌ 예약 취소 실패: 예약번호 {reservation_id}번을 찾을 수 없거나 이미 취소되었거나 이미 완료된 예약입니다."
                        else:
                            message = f"❌ 예약 취소 실패: 예약번호 {reservation_id}번은 이미 종료된 예약이므로 취소할 수 없습니다. (현재 시각: {now.strftime('%Y-%m-%d %H:%M')})"
                else:
                    message = f"❌ 예약 취소 실패: 예약번호 {reservation_id}번을 찾을 수 없습니다."

            except Exception as e:
                conn.rollback()
                message = f"❌ 예약 취소 중 오류 발생: {e}"

    # GET handling: Fetch all reservations
    reservations = []
    try:
        cursor = conn.execute("""
            SELECT R.reservation_id, U.name AS user_name, S.space_name, 
                   R.reservation_date, R.start_time, R.end_time, R.purpose, R.status
            FROM Reservation R
            JOIN User U ON R.user_id = U.user_id
            JOIN Space S ON R.space_id = S.space_id
            ORDER BY R.reservation_date DESC, R.start_time DESC
        """)
        reservations = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        message = f"❌ 예약 리스트 조회 오류: {e}"

    # HTML Rendering
    html = f"""
    <!DOCTYPE html>
    <title>예약 관리</title>
    <h1>예약 관리 (전체 리스트)</h1>
    <a href="{url_for('dashboard')}">대시보드로 돌아가기</a>
    <p style="color:{'green' if '✅' in message else 'red'};">{message}</p>
    
    <h2>총 {len(reservations)}건 조회됨</h2>
    <table border="1">
        <tr><th>예약번호</th><th>사용자 이름</th><th>공간 이름</th><th>날짜</th><th>시간</th><th>사용 목적</th><th>상태</th><th>관리</th></tr>
    """
    
    for r in reservations:
        effective_status = r['status']
        can_cancel = False
        
        # 예약 종료 시점 확인 (YYYY-MM-DD HH:MM:SS)
        res_end_dt_str = f"{r['reservation_date']} {r['end_time']}"

        if r['status'] in ('예약됨', '사용 완료'):
            if res_end_dt_str > now_dt_str:
                # 미래 예약 (취소 가능)
                status_color = 'blue'
                can_cancel = True
            else:
                # 과거 예약 (기간 만료로 간주, 취소 불가)
                effective_status = '기간 만료' if r['status'] == '예약됨' else r['status']
                status_color = 'gray'
                can_cancel = False
        elif '취소' in r['status']:
            status_color = 'gray'
        elif r['status'] in ('노쇼', '노쇼-처리됨'): # 노쇼 상태 추가
            status_color = 'red'
        else:
            status_color = 'green' # 노쇼 등 기타 상태
            
        cancel_button = ""
        if can_cancel:
            cancel_button = f"""
            <form method="POST" style="display:inline;" onsubmit="return confirm('예약번호 {r['reservation_id']}번을 정말 취소하시겠습니까?');">
                <input type="hidden" name="cancel_id" value="{r['reservation_id']}">
                <button type="submit" style="color:red;">강제 취소</button>
            </form>
            """
        
        html += f"""
        <tr>
            <td>{r['reservation_id']}</td>
            <td>{r['user_name']}</td>
            <td>{r['space_name']}</td>
            <td>{r['reservation_date']}</td>
            <td>{r['start_time'][:5]} ~ {r['end_time'][:5]}</td>
            <td>{r['purpose']}</td>
            <td style="color:{status_color}">**{effective_status}**</td>
            <td>{cancel_button}</td>
        </tr>
        """
    html += "</table>"
    return html

# -----------------------------------------------------------
# 대시보드 및 기능 (벌점 상세 현황 조회 링크 삭제)
# -----------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    """대시보드 페이지 (벌점 기반 예약 가능 여부 로직 업데이트)"""
    if 'admin_id' in session:
        return f"""
            <!DOCTYPE html><title>관리자 대시보드</title>
            <h1>관리자 대시보드 - {session['name']}님</h1>
            <p>관리자 번호: {session['admin_id']}</p>
            <hr>
            <h2>주요 관리 기능</h2>
            <ul>
                <li><a href="{url_for('admin_profile')}"><strong>관리자 정보 수정</strong></a></li> 
                <li><a href="{url_for('admin_user_management')}"><strong>사용자 관리 (이용 제한 설정/해제)</strong></a></li> 
                <li><a href="{url_for('admin_reservation_management')}"><strong>예약 관리 (예약 취소)</strong></a></li> 
                <li><a href="{url_for('admin_space_management')}"><strong>장소 관리 (사용 중지 설정/해제)</strong></a></li> 
            </ul>
            <hr>
            <p><a href="{url_for('logout')}">로그아웃</a></p>
        """

    conn = get_db_connection()
    user_id = session['user_id']
    
    # === [추가된 부분: 일일 노쇼 및 벌점 처리 로직 실행] ===
    global LAST_DAILY_PROCESS_DATE
    today_date = datetime.now().date().isoformat()
    # 서버가 켜진 상태에서 하루에 한 번만 실행
    if LAST_DAILY_PROCESS_DATE != today_date:
        try:
            # DB 연결을 다시 얻어와서 사용 (process_daily_tasks가 commit을 하기 때문)
            temp_conn = get_db_connection()
            process_daily_tasks(temp_conn)
            LAST_DAILY_PROCESS_DATE = today_date
        except Exception as e:
            if conn: conn.rollback()
            print(f"Daily processing failed: {e}")
    # =========================================================

    user_info = {"name": session['name'], "role": session['role'], "detail": "정보 조회 중...", "penalty": 0} 

    if conn:
        try:
            if session['role'] == '학생':
                detail = conn.execute("SELECT student_id, grade, major FROM Student WHERE user_id = ?", (user_id,)).fetchone()
                user_info["detail"] = f"학번: {detail['student_id']}, {detail['major']} {detail['grade']}학년" if detail else "상세 정보 없음"
            elif session['role'] == '교수':
                detail = conn.execute("SELECT professor_id, position, department FROM Professor WHERE user_id = ?", (user_id,)).fetchone()
                user_info["detail"] = f"교번: {detail['professor_id']}, {detail['department']} {detail['position']}" if detail else "상세 정보 없음"
            
            # === [수정된 부분: 유효 벌점 일수를 계산하는 함수 사용 (자동 감소 효과 적용)] ===
            user_info["penalty"] = get_total_active_penalty_days(conn, user_id)
            
            # [기존 요청 사항] 노쇼 횟수 조회 (status='노쇼'인 것만 카운트)
            no_show_count = conn.execute(
                "SELECT COUNT(*) AS count FROM Reservation WHERE user_id = ? AND status = '노쇼'", (user_id,)
            ).fetchone()['count']
            user_info["no_show"] = no_show_count
            
        except Exception as e:
            user_info["detail"] = f"정보 조회 오류: {e}"
            
    is_restricted = user_info['penalty'] > 0 # 예약 제한 로직: 벌점 총합이 1일이라도 있으면 제한
            
    html = f"""
    <!DOCTYPE html>
    <title>대시보드</title>
    <h1>{user_info['name']}님 환영합니다! ({user_info['role']})</h1>
    <p><strong>{user_info['detail']}</strong></p>
    <p style="font-size: 1.2em; color:{'red' if is_restricted else 'green'};">
        **현재 누적 벌점: {user_info['penalty']}일** ({'1일 이상이므로 예약 불가' if is_restricted else '예약 가능'})
    </p>
    
    <p>
        **누적 노쇼 횟수: {user_info['no_show']}회**
    </p>
    
    <hr>
    <h2>주요 기능</h2>
    <ul>
        <li><a href="{url_for('user_profile')}"><strong>내 정보 수정</strong></a></li>
        <li><a href="{url_for('my_reservations')}">나의 예약 현황 및 취소</a></li>
        <li><a href="{url_for('reservation_form')}">공간 예약하기</a></li>
    </ul>
    <hr>
    <p><a href="{url_for('logout')}">로그아웃</a></p>
    """
    return html

# -----------------------------------------------------------
# 예약/취소/벌점 기능 (test4.py 스타일로 reservation_form 수정)
# -----------------------------------------------------------

@app.route('/reservations/mine', methods=['GET', 'POST'])
@login_required
def my_reservations():
    """나의 예약 현황 페이지 및 예약 취소 처리, 사용 확인 처리"""
    if 'user_id' not in session: return redirect(url_for('dashboard')) 
    user_id = session['user_id']
    conn = get_db_connection()
    reservations = []
    message = ""

    now = datetime.now()
    # 현재 시각을 분 단위로 맞춤 (초, 마이크로초 무시)
    now_dt = now.replace(second=0, microsecond=0) 

    if request.method == 'POST':
        action = request.form.get('action')
        # POST 폼에서 전달되는 ID는 'id'로 통일하여 사용
        reservation_id = request.form.get('id') 

        if action == 'cancel_reservation' and reservation_id:
            # === [수정된 부분: 취소 전 사용 확인 여부 체크] ===
            # 1. 사용 확인 여부 체크: usage_status = 1 이면 취소 불가
            check_usage = conn.execute(
                "SELECT usage_status FROM Reservation WHERE reservation_id = ? AND user_id = ?", 
                (reservation_id, user_id)
            ).fetchone()

            if check_usage and check_usage['usage_status'] == 1:
                message = f"❌ 예약 취소 실패: 예약번호 {reservation_id}번은 이미 **사용 확인이 완료**되어 취소할 수 없습니다."
            else:
                try:
                    # 사용자가 예약을 취소하면 노쇼가 아닌 '취소됨'으로 표시
                    cursor = conn.execute("""
                        UPDATE Reservation 
                        SET status = '취소됨' 
                        WHERE reservation_id = ? AND user_id = ? AND status = '예약됨' AND usage_status = 0
                    """, (reservation_id, user_id))
                    conn.commit()
                    
                    if cursor.rowcount > 0:
                        message = f"✅ 예약번호 {reservation_id}번이 성공적으로 취소되었습니다."
                    else:
                         message = f"❌ 예약 취소 실패: 예약번호 {reservation_id}번을 찾을 수 없거나 이미 취소되었거나 사용 확인이 완료되었습니다."
                             
                except Exception as e:
                    conn.rollback()
                    message = f"예약 취소 중 오류 발생: {e}"
            # ========================================================
            
        elif action == 'confirm_usage' and reservation_id:
            # === [추가된 부분: 사용 확인 로직] ===
            res_info = conn.execute(
                "SELECT reservation_date, start_time, end_time, status, usage_status FROM Reservation WHERE reservation_id = ? AND user_id = ?",
                (reservation_id, user_id)
            ).fetchone()
            
            if res_info is None:
                message = f"❌ 사용 확인 실패: 예약번호 {reservation_id}번을 찾을 수 없습니다."
            elif res_info['status'] != '예약됨':
                message = f"❌ 사용 확인 실패: 예약 상태가 '{res_info['status']}'이므로 확인할 수 없습니다."
            elif res_info['usage_status'] == 1:
                message = f"❌ 사용 확인 실패: 예약번호 {reservation_id}번은 이미 **사용 확인이 완료**되었습니다."
            else:
                # 시간대 체크를 위한 데이터 가공
                res_date = res_info['reservation_date']
                start_time = res_info['start_time'][:5]
                end_time = res_info['end_time'][:5]
                
                # HH:MM:00 형식으로 datetime 객체 생성 (비교를 위해)
                res_start_dt_str = f"{res_date} {start_time}"
                res_end_dt_str = f"{res_date} {end_time}"
                
                res_start_dt = datetime.strptime(res_start_dt_str, '%Y-%m-%d %H:%M')
                res_end_dt = datetime.strptime(res_end_dt_str, '%Y-%m-%d %H:%M')
                
                # 예약 시작 시간 <= 현재 시간 < 예약 종료 시간 (예약 시간대 안에 있는지 확인)
                if res_start_dt <= now_dt < res_end_dt:
                    try:
                        conn.execute("""
                            UPDATE Reservation 
                            SET usage_status = 1, status = '사용 완료' 
                            WHERE reservation_id = ? AND user_id = ? AND status = '예약됨' AND usage_status = 0
                        """, (reservation_id, user_id))
                        conn.commit()
                        message = f"✅ 예약번호 {reservation_id}번의 **사용 확인이 성공적으로 완료**되었습니다. 상태: 사용 완료."
                    except Exception as e:
                        conn.rollback()
                        message = f"❌ 사용 확인 중 오류 발생: {e}"
                else:
                    message = f"❌ 사용 확인 실패: 예약 확인은 **예약 시간대** ({res_start_dt_str} ~ {res_end_dt_str})에만 누를 수 있습니다. 현재 시각: {now_dt.strftime('%Y-%m-%d %H:%M')}."
            # ========================================================

    if conn:
        try:
            # === [수정된 부분: usage_status 컬럼 추가 조회] ===
            cursor = conn.execute("""
                SELECT R.reservation_id, R.reservation_date, R.start_time, R.end_time, R.status, R.purpose, R.usage_status,
                       S.space_name, S.location 
                FROM Reservation R
                JOIN Space S ON R.space_id = S.space_id
                WHERE R.user_id = ?
                ORDER BY R.reservation_date DESC, R.start_time DESC
            """, (user_id,))
            reservations = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            reservations = f"예약 조회 오류: {e}"

    html = f"""
    <!DOCTYPE html>
    <title>나의 예약 현황</title>
    <h1>나의 예약 현황 및 취소</h1>
    <a href="{url_for('dashboard')}">대시보드로 돌아가기</a>
    <p style="color:{'green' if '✅' in message else 'red'};">{message}</p>
    <p>**[사용 확인]** 버튼은 예약된 시간대({now_dt.strftime('%Y-%m-%d %H:%M')} 기준)에만 누를 수 있습니다. 시간대를 지나 사용 확인을 하지 않으면 노쇼 처리됩니다.</p>
    <h2>총 {len(reservations)}건 조회됨</h2>
    <table border="1">
        <tr><th>ID</th><th>공간 이름</th><th>위치</th><th>날짜</th><th>시간</th><th>사용 목적</th><th>상태</th><th>확인/취소</th></tr>
    """
    if isinstance(reservations, str):
         html += f'<tr><td colspan="8" style="color:red">{reservations}</td></tr>'
    else:
        now_dt_str = now.strftime('%Y-%m-%d %H:%M:%S')

        for r in reservations:
            effective_status = r['status']
            can_cancel = False
            can_confirm = False
            
            res_end_dt_str = f"{r['reservation_date']} {r['end_time']}"
            res_start_dt_str = f"{r['reservation_date']} {r['start_time']}"
            
            # DB의 시간은 HH:MM:SS 이지만, Python 비교를 위해 HH:MM까지 사용
            res_start_dt = datetime.strptime(res_start_dt_str[:16], '%Y-%m-%d %H:%M') 
            res_end_dt = datetime.strptime(res_end_dt_str[:16], '%Y-%m-%d %H:%M')     

            status_color = 'gray' 

            if r['usage_status'] == 1:
                effective_status = '사용 완료'
                status_color = 'blue'
            elif r['status'] == '예약됨':
                if res_end_dt_str > now_dt_str:
                    # 미래 예약 (취소 가능, 사용 확인 가능 시간)
                    status_color = 'blue'
                    can_cancel = True
                    
                    # 예약 시작 시간 <= 현재 시간 < 예약 종료 시간 (사용 확인 가능 시간)
                    if res_start_dt <= now_dt.replace(second=0, microsecond=0) < res_end_dt:
                        can_confirm = True
                        effective_status = '예약됨 (확인 가능)'
                    else:
                        can_confirm = False
                        effective_status = '예약됨'
                        
                else:
                    # 과거 예약 (기간 만료, 노쇼 처리 대상)
                    effective_status = '기간 만료 (확인 필요)'
                    status_color = 'red'
                    can_cancel = False
                    can_confirm = False
            elif '취소' in r['status']:
                status_color = 'gray'
            elif r['status'] in ('노쇼', '노쇼-처리됨'):
                status_color = 'red'

            action_buttons = ""
            
            if r['usage_status'] == 1:
                action_buttons = "사용 확인 완료"
            elif can_confirm:
                action_buttons += f"""
                <form method="POST" style="display:inline; margin-right: 5px;" onsubmit="return confirm('지금 {r['space_name']}의 사용을 확인하시겠습니까?');">
                    <input type="hidden" name="action" value="confirm_usage">
                    <input type="hidden" name="id" value="{r['reservation_id']}">
                    <button type="submit" style="color:blue;">사용 확인</button>
                </form>
                """
            
            if can_cancel:
                 action_buttons += f"""
                <form method="POST" style="display:inline;" onsubmit="return confirm('예약번호 {r['reservation_id']}번을 정말 취소하시겠습니까?');">
                    <input type="hidden" name="action" value="cancel_reservation">
                    <input type="hidden" name="id" value="{r['reservation_id']}">
                    <button type="submit" style="color:red;">취소하기</button>
                </form>
                """
            
            if not action_buttons:
                action_buttons = "-"


            html += f"""
            <tr>
                <td>{r['reservation_id']}</td>
                <td>{r['space_name']}</td>
                <td>{r['location']}</td>
                <td>{r['reservation_date']}</td>
                <td>{r['start_time'][:5]} ~ {r['end_time'][:5]}</td>
                <td>{r['purpose']}</td>
                <td style="color:{status_color}">**{effective_status}**</td>
                <td>{action_buttons}</td>
            </tr>
            """
    html += "</table>"
    return html


@app.route('/penalty/status')
@login_required
def penalty_status():
    """벌점 상세 현황 페이지"""
    if 'user_id' not in session: return redirect(url_for('dashboard'))
    user_id = session['user_id']
    conn = get_db_connection()
    penalties = []
    
    # === [수정된 부분: 유효 벌점 일수를 계산하는 함수 사용] ===
    total_penalty = get_total_active_penalty_days(conn, user_id)
    # ========================================================
    
    if conn:
        try:
            cursor = conn.execute("""
                SELECT reason, penalty_date, penalty_period, released 
                FROM Penalty
                WHERE user_id = ?
                ORDER BY penalty_date DESC
            """, (user_id,))
            penalties = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            penalties = f"벌점 조회 오류: {e}"

    html = f"""
    <!DOCTYPE html>
    <title>벌점 현황</title>
    <h1>벌점 상세 현황</h1>
    <a href="{url_for('dashboard')}">대시보드로 돌아가기</a>
    <p style="font-size: 1.5em; color:{'red' if total_penalty > 0 else 'green'};">
        **총 누적 벌점 (현재 유효): {total_penalty}일** ({'예약 불가 상태' if total_penalty > 0 else '예약 가능 상태'})
    </p>
    <table border="1">
        <tr><th>날짜</th><th>사유</th><th>벌점 기간 (일)</th><th>해제 여부</th></tr>
    """
    if isinstance(penalties, str):
         html += f'<tr><td colspan="4" style="color:red">{penalties}</td></tr>'
    else:
        for p in penalties:
            released_text = 'Yes' if p['released'] else 'No (유효)'
            released_color = 'gray' if p['released'] else 'red'
            html += f"""
            <tr>
                <td>{p['penalty_date']}</td>
                <td>{p['reason']}</td>
                <td>{p['penalty_period']}</td>
                <td style="color:{released_color}">**{released_text}**</td>
            </tr>
            """
    html += "</table>"
    return html

@app.route('/reservations/new', methods=['GET', 'POST'])
@login_required
def reservation_form():
    """공간 예약 페이지 (test4.py 스타일: 공간 목록을 먼저 보여주고 각 공간별로 예약 폼 제공)"""
    if 'user_id' not in session: return redirect(url_for('dashboard'))
    conn = get_db_connection()
    spaces = []
    message = ""
    now_date = datetime.now().strftime('%Y-%m-%d') # Default date for form

    # --- 1. POST 요청 처리 (예약 생성) ---
    if request.method == 'POST':
        # form에서 넘어오는 시간은 HH:MM 형식이므로, DB에 맞게 :00을 붙여줌.
        space_id = request.form.get('space_id')
        res_date = request.form.get('reservation_date')
        start_time_input = request.form.get('start_time') # HH:MM
        end_time_input = request.form.get('end_time') # HH:MM
        purpose = request.form.get('purpose') 
        
        start_time = start_time_input + ':00' 
        end_time = end_time_input + ':00'

        if not conn: message = "DB 연결 오류로 예약을 진행할 수 없습니다."
        elif not all([space_id, res_date, start_time, end_time, purpose]):
            message = "모든 필수 예약 정보를 입력해야 합니다."
        else:
            # ************************************************************
            # [추가된 부분] 0. 예약 시간 유효성 검사: 이미 지난 시각인지 확인
            now = datetime.now()
            # 초/마이크로초를 0으로 설정하여 현재 시각을 기준으로 분 단위 비교
            now_dt_minute = now.replace(second=0, microsecond=0) 

            reservation_start_dt = None
            try:
                # 사용자가 입력한 날짜와 시간(HH:MM)을 결합하여 datetime 객체 생성
                reservation_start_dt_str = f"{res_date} {start_time_input}" 
                reservation_start_dt = datetime.strptime(reservation_start_dt_str, '%Y-%m-%d %H:%M')
            except ValueError:
                # 날짜/시간 형식이 잘못된 경우 (이 경우는 'if not all'에 걸릴 가능성이 높지만 안전장치)
                message = "❌ 잘못된 날짜 또는 시간 형식입니다."
            
            # 유효한 datetime 객체가 생성되었고, 예약 시작 시간이 현재 시간보다 이른 경우
            if reservation_start_dt and reservation_start_dt < now_dt_minute:
                message = f"❌ 예약하려는 시작 시각({res_date} {start_time_input})은 이미 지나갔으므로 예약할 수 없습니다. 현재 시각: {now.strftime('%Y-%m-%d %H:%M')}."
            # ************************************************************
            elif start_time >= end_time:
                message = "❌ 시작 시간이 종료 시간보다 빠르거나 같아야 합니다."
            else:
                try:
                    # 1. 벌점 체크 (기존 로직)
                    # === [수정된 부분: 유효 벌점 일수를 계산하는 함수 사용] ===
                    total_penalty = get_total_active_penalty_days(conn, session['user_id'])
                    # ========================================================
                    
                    if total_penalty > 0:
                        message = f"❌ 현재 누적된 벌점(이용 제한 일수: {total_penalty}일)이 있으므로 예약할 수 없습니다. 벌점 상세 현황을 확인해주세요."
                    else:
                        # 2. 장소 사용 중지 확인 (기존 로직)
                        is_maintenance = conn.execute(
                            """
                            SELECT COUNT(*) FROM Space_stop
                            WHERE space_id = ?
                              AND ? BETWEEN start_date AND end_date
                            """, (space_id, res_date)
                        ).fetchone()[0]

                        if is_maintenance > 0:
                            space_name = conn.execute("SELECT space_name FROM Space WHERE space_id = ?", (space_id,)).fetchone()['space_name']
                            message = f"❌ 공간 '{space_name}'은(는) 해당 날짜에 관리자에 의해 사용이 중지되었습니다."
                        else:
                            # 3. 예약 충돌 확인 (기존 로직)
                            is_available = conn.execute(
                                f"""
                                SELECT COUNT(*) FROM Reservation
                                WHERE space_id = ? AND reservation_date = ? AND status IN ('예약됨', '사용 완료')
                                  AND start_time < ? AND end_time > ? 
                                """, (space_id, res_date, end_time, start_time)
                            ).fetchone()[0]

                            if is_available > 0:
                                space_name = conn.execute("SELECT space_name FROM Space WHERE space_id = ?", (space_id,)).fetchone()['space_name']
                                message = f"❌ 공간 '{space_name}'은(는) 선택한 시간에 이미 예약되었습니다."
                            else:
                                # 4. 최종 예약 (기존 로직)
                                # usage_status는 기본값 0으로 저장됨 (사용 확인 전)
                                conn.execute("""
                                    INSERT INTO Reservation (user_id, space_id, reservation_date, start_time, end_time, purpose, status)
                                    VALUES (?, ?, ?, ?, ?, ?, '예약됨')
                                """, (session['user_id'], space_id, res_date, start_time, end_time, purpose, )) 
                                conn.commit()
                                space_name = conn.execute("SELECT space_name FROM Space WHERE space_id = ?", (space_id,)).fetchone()['space_name']
                                message = f"✅ {space_name}에 대한 예약이 성공적으로 완료되었습니다!"
                except Exception as e:
                    conn.rollback()
                    message = f"예약 중 오류 발생: {e}"


    # --- 2. GET 요청 처리 (전체 공간 목록 조회) ---
    if conn:
        try:
            # 모든 공간 목록 조회
            cursor = conn.execute(
                "SELECT space_id, space_name, location, capacity, space_type FROM Space ORDER BY space_name"
            )
            spaces = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            spaces = f"공간 조회 오류: {e}"


    # --- 3. HTML 렌더링 (test4.py 스타일) ---
    html = f"""
    <!DOCTYPE html>
    <title>공간 예약</title>
    <h1>공간 예약하기 (공간별 날짜/시간 선택)</h1>
    <a href="{url_for('dashboard')}">대시보드로 돌아가기</a>
    <hr>
    
    <h2 style="color:{'green' if '✅' in message else 'red'};">{message}</h2>
    
    <h2>전체 공간 목록</h2>
    <p>각 공간의 예약 폼에 날짜와 시간을 지정하여 예약 확정 버튼을 눌러주세요. 예약 시 벌점 및 충돌 여부를 확인합니다.</p>
    <table border="1">
        <tr><th>공간 이름 (타입)</th><th>위치</th><th>최대 인원</th><th>날짜/시간 및 예약</th></tr>
    """
    
    if isinstance(spaces, str):
         html += f'<tr><td colspan="4" style="color:red">{spaces}</td></tr>'
    elif not spaces:
        html += '<tr><td colspan="4">현재 등록된 공간이 없습니다.</td></tr>'
    else:
        for s in spaces:
            # 각 공간별로 예약 폼을 포함 (test4.py 스타일)
            html += f"""
            <tr>
                <td>{s['space_name']} ({s['space_type']})</td>
                <td>{s['location']}</td>
                <td>{s['capacity']}명</td>
                <td>
                    <form method="POST" action="{url_for("reservation_form")}" onsubmit="return confirm('{s['space_name']}을(를) 예약하시겠습니까?');">
                        <input type="hidden" name="space_id" value="{s['space_id']}">
                        
                        날짜: <input type="date" name="reservation_date" value="{now_date}" required style="width:120px;"><br>
                        시작 시간: <input type="time" name="start_time" value="09:00" required style="width:100px;">
                         종료 시간: <input type="time" name="end_time" value="18:00" required style="width:100px;"><br>
                        
                        사용 목적: <input type="text" name="purpose" required style="width:300px;"><br>
                        
                        <button type="submit" style="margin-top:5px;">예약 확정</button>
                    </form>
                </td>
            </tr>
            """
    html += "</table>"
    return html

# -----------------------------------------------------------
# 메인 실행
# -----------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)