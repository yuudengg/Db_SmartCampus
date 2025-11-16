import sqlite3
from flask import Flask, jsonify, request, session, redirect, url_for, g, flash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_strong_secret_key_here' 
app.config['JSON_AS_ASCII'] = False 
DATABASE = 'db_project_table' 

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
    """관리자: 사용자 목록 조회 및 이용 제한 부과 (벌점)"""
    if 'admin_id' not in session: return redirect(url_for('dashboard'))
    conn = get_db_connection()
    message = ""
    penalty_days = 3 # 고정된 제한 기간

    # POST handling: Impose Restriction (Add 3-day penalty)
    if request.method == 'POST':
        user_id_to_penalize = request.form.get('user_id')
        if user_id_to_penalize:
            try:
                # 3일 이용 제한 부과 (Penalty 테이블에 추가)
                conn.execute("""
                    INSERT INTO Penalty (user_id, reason, penalty_date, penalty_period, released)
                    VALUES (?, ?, ?, ?, 0)
                """, (user_id_to_penalize, '관리자 이용 제한 부과 (노쇼 또는 기타)', datetime.now().strftime('%Y-%m-%d'), penalty_days))
                conn.commit()
                
                user_name = conn.execute("SELECT name FROM User WHERE user_id = ?", (user_id_to_penalize,)).fetchone()['name']
                message = f"✅ {user_name} 사용자에게 {penalty_days}일 이용 제한이 성공적으로 부과되었습니다. (벌점 총합이 1일 이상이 되면 예약이 불가능합니다.)"

            except Exception as e:
                conn.rollback()
                message = f"❌ 이용 제한 부과 중 오류 발생: {e}"

    # GET handling: Fetch all users and their total active penalty days
    users = []
    try:
        cursor = conn.execute("""
            SELECT U.user_id, U.login_id, U.name, U.role, 
                   COALESCE(SUM(P.penalty_period), 0) AS total_penalty_days 
            FROM User U
            LEFT JOIN Penalty P ON U.user_id = P.user_id AND P.released = 0
            GROUP BY U.user_id
            ORDER BY U.user_id
        """)
        users = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        message = f"❌ 사용자 리스트 조회 오류: {e}"

    # HTML Rendering
    html = f"""
    <!DOCTYPE html>
    <title>사용자 관리</title>
    <h1>사용자 관리 (이용 제한 부과)</h1>
    <a href="{url_for('dashboard')}">대시보드로 돌아가기</a>
    <p style="color:{'green' if '✅' in message else 'red'};">{message}</p>
    
    <h2>사용자 목록 및 이용 제한 부과</h2>
    <p>이용 제한 부과 버튼을 누르면 해당 사용자에게 **{penalty_days}일**간 벌점이 부과되며, **총 벌점이 1일 이상이면 예약이 불가능**합니다.</p>
    <table border="1">
        <tr><th>User ID</th><th>로그인 ID</th><th>이름</th><th>역할</th><th>누적 벌점 (제한 일수)</th><th>이용 제한 부과</th></tr>
    """
    
    for u in users:
        # 1일 이상이면 예약 불가 상태
        is_restricted = u['total_penalty_days'] > 0
        penalty_color = 'red' if is_restricted else 'green'
        
        # 관리자 본인에게는 벌점 부과 버튼을 표시하지 않음
        if u['user_id'] != session.get('user_id'): 
            penalize_button = f"""
            <form method="POST" style="display:inline;" onsubmit="return confirm('{u['name']} 사용자에게 정말 {penalty_days}일 이용 제한을 부과하시겠습니까? 이 사용자는 벌점 부과 후 예약이 불가능해집니다.');">
                <input type="hidden" name="user_id" value="{u['user_id']}">
                <button type="submit" style="color:red;">{penalty_days}일 제한 부과</button>
            </form>
            """
        else:
            penalize_button = "N/A"
        
        html += f"""
        <tr>
            <td>{u['user_id']}</td>
            <td>{u['login_id']}</td>
            <td>{u['name']}</td>
            <td>{u['role']}</td>
            <td style="color:{penalty_color}; font-weight:bold;">{u['total_penalty_days']}일 ({'예약 불가' if is_restricted else '예약 가능'})</td>
            <td>{penalize_button}</td>
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
    """관리자: 예약 리스트 조회 및 강제 취소 (변경 없음)"""
    if 'admin_id' not in session: return redirect(url_for('dashboard'))
    conn = get_db_connection()
    message = ""

    # POST handling: Cancel Reservation (Admin cancels)
    if request.method == 'POST':
        reservation_id = request.form.get('cancel_id')
        if reservation_id:
            try:
                cursor = conn.execute("""
                    UPDATE Reservation 
                    SET status = '관리자 취소' 
                    WHERE reservation_id = ? AND status = '예약됨'
                """, (reservation_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    message = f"✅ 예약번호 {reservation_id}번이 성공적으로 취소되었습니다. (관리자 취소)"
                else:
                    message = f"❌ 예약 취소 실패: 예약번호 {reservation_id}번을 찾을 수 없거나 이미 취소된 예약입니다."
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
        status_color = 'blue' if r['status'] == '예약됨' else 'gray' if '취소' in r['status'] else 'green'
        can_cancel = r['status'] == '예약됨'
        
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
            <td style="color:{status_color}">**{r['status']}**</td>
            <td>{cancel_button}</td>
        </tr>
        """
    html += "</table>"
    return html

# -----------------------------------------------------------
# 대시보드 및 기능 (변경 없음)
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
                <li><a href="{url_for('admin_user_management')}"><strong>사용자 관리 (이용 제한 부과)</strong></a></li> 
                <li><a href="{url_for('admin_reservation_management')}"><strong>예약 관리 (예약 취소)</strong></a></li> 
                <li><a href="{url_for('admin_space_management')}"><strong>장소 관리 (사용 중지 설정/해제)</strong></a></li> 
            </ul>
            <hr>
            <p><a href="{url_for('logout')}">로그아웃</a></p>
        """

    conn = get_db_connection()
    user_id = session['user_id']
    user_info = {"name": session['name'], "role": session['role'], "detail": "정보 조회 중...", "penalty": 0}

    if conn:
        try:
            if session['role'] == '학생':
                detail = conn.execute("SELECT student_id, grade, major FROM Student WHERE user_id = ?", (user_id,)).fetchone()
                user_info["detail"] = f"학번: {detail['student_id']}, {detail['major']} {detail['grade']}학년" if detail else "상세 정보 없음"
            elif session['role'] == '교수':
                detail = conn.execute("SELECT professor_id, position, department FROM Professor WHERE user_id = ?", (user_id,)).fetchone()
                user_info["detail"] = f"교번: {detail['professor_id']}, {detail['department']} {detail['position']}" if detail else "상세 정보 없음"
            
            total_penalty = conn.execute(
                "SELECT SUM(penalty_period) AS total_days FROM Penalty WHERE user_id = ? AND released = 0", (user_id,)
            ).fetchone()['total_days']
            user_info["penalty"] = total_penalty if total_penalty else 0
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
    <hr>
    <h2>주요 기능</h2>
    <ul>
        <li><a href="{url_for('user_profile')}"><strong>내 정보 수정</strong></a></li>
        <li><a href="{url_for('my_reservations')}">나의 예약 현황 및 취소</a></li>
        <li><a href="{url_for('reservation_form')}">공간 예약하기</a></li>
        <li><a href="{url_for('penalty_status')}">벌점 상세 현황 조회</a></li>
    </ul>
    <hr>
    <p><a href="{url_for('logout')}">로그아웃</a></p>
    """
    return html

# -----------------------------------------------------------
# 예약/취소/벌점 기능 (변경 없음)
# -----------------------------------------------------------

@app.route('/reservations/mine', methods=['GET', 'POST'])
@login_required
def my_reservations():
    """나의 예약 현황 페이지 및 예약 취소 처리"""
    if 'user_id' not in session: return redirect(url_for('dashboard')) 
    user_id = session['user_id']
    conn = get_db_connection()
    reservations = []
    message = ""

    if request.method == 'POST':
        reservation_id = request.form.get('cancel_id')
        if reservation_id:
            try:
                cursor = conn.execute("""
                    UPDATE Reservation 
                    SET status = '취소됨' 
                    WHERE reservation_id = ? AND user_id = ? AND status = '예약됨'
                """, (reservation_id, user_id))
                conn.commit()
                
                if cursor.rowcount > 0:
                    message = f"✅ 예약번호 {reservation_id}번이 성공적으로 취소되었습니다."
                else:
                    check_res = conn.execute("SELECT user_id, status FROM Reservation WHERE reservation_id = ?", (reservation_id,)).fetchone()
                    if check_res is None:
                         message = f"❌ 예약 취소 실패: 예약번호 {reservation_id}번을 찾을 수 없습니다."
                    elif check_res['user_id'] != user_id:
                         message = f"❌ 예약 취소 실패: 해당 예약은 본인의 예약이 아닙니다."
                    else:
                         message = f"❌ 예약 취소 실패: 예약 상태가 '{check_res['status']}'이므로 취소할 수 없습니다."
                         
            except Exception as e:
                conn.rollback()
                message = f"예약 취소 중 오류 발생: {e}"

    if conn:
        try:
            cursor = conn.execute("""
                SELECT R.reservation_id, R.reservation_date, R.start_time, R.end_time, R.status, R.purpose,
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
    <p style="color:blue;">{message}</p>
    <h2>총 {len(reservations)}건 조회됨</h2>
    <table border="1">
        <tr><th>ID</th><th>공간 이름</th><th>위치</th><th>날짜</th><th>시간</th><th>사용 목적</th><th>상태</th><th>취소</th></tr>
    """
    if isinstance(reservations, str):
         html += f'<tr><td colspan="8" style="color:red">{reservations}</td></tr>'
    else:
        for r in reservations:
            status_color = 'blue' if r['status'] == '예약됨' else 'gray' if '취소' in r['status'] else 'green'
            can_cancel = r['status'] == '예약됨'
            
            cancel_button = ""
            if can_cancel:
                cancel_button = f"""
                <form method="POST" style="display:inline;" onsubmit="return confirm('예약번호 {r['reservation_id']}번을 정말 취소하시겠습니까?');">
                    <input type="hidden" name="cancel_id" value="{r['reservation_id']}">
                    <button type="submit" style="color:red;">취소하기</button>
                </form>
                """
            
            html += f"""
            <tr>
                <td>{r['reservation_id']}</td>
                <td>{r['space_name']}</td>
                <td>{r['location']}</td>
                <td>{r['reservation_date']}</td>
                <td>{r['start_time'][:5]} ~ {r['end_time'][:5]}</td>
                <td>{r['purpose']}</td>
                <td style="color:{status_color}">**{r['status']}**</td>
                <td>{cancel_button}</td>
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
    total_penalty = 0
    
    if conn:
        try:
            total_penalty_row = conn.execute(
                "SELECT SUM(penalty_period) AS total_days FROM Penalty WHERE user_id = ? AND released = 0", (user_id,)
            ).fetchone()
            total_penalty = total_penalty_row['total_days'] if total_penalty_row and total_penalty_row['total_days'] else 0
            
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
    """공간 예약 페이지 (장소 사용 중지 확인 로직 수정)"""
    if 'user_id' not in session: return redirect(url_for('dashboard'))
    conn = get_db_connection()
    spaces = []
    message = ""

    # --- 1. POST 요청 처리 (예약 생성) ---
    if request.method == 'POST':
        space_id = request.form.get('space_id')
        res_date = request.form.get('reservation_date')
        start_time = request.form.get('start_time') + ':00'
        end_time = request.form.get('end_time') + ':00'     
        purpose = request.form.get('purpose') 
        
        if not conn: message = "DB 연결 오류로 예약을 진행할 수 없습니다."
        elif not all([space_id, res_date, start_time, end_time, purpose]):
            message = "모든 필수 예약 정보를 입력해야 합니다."
        else:
            try:
                total_penalty = conn.execute(
                    "SELECT SUM(penalty_period) AS total FROM Penalty WHERE user_id = ? AND released = 0", (session['user_id'],)
                ).fetchone()['total'] or 0
                
                # 예약 제한 로직: 벌점 총합이 1일 이상이면 예약 불가
                if total_penalty > 0:
                    message = f"❌ 현재 누적된 벌점(이용 제한 일수: {total_penalty}일)이 있으므로 예약할 수 없습니다. 벌점 상세 현황을 확인해주세요."
                else:
                    # 장소 사용 중지 확인 로직 수정 (released 조건 제거)
                    is_maintenance = conn.execute(
                        """
                        SELECT COUNT(*) FROM Space_stop
                        WHERE space_id = ?
                          AND ? BETWEEN start_date AND end_date
                        """, (space_id, res_date)
                    ).fetchone()[0]

                    if is_maintenance > 0:
                        message = "❌ 선택한 공간은 해당 날짜에 관리자에 의해 사용이 중지되었습니다."
                    else:
                        # 예약 충돌 확인
                        is_available = conn.execute(
                            f"""
                            SELECT COUNT(*) FROM Reservation
                            WHERE space_id = ? AND reservation_date = ? AND status = '예약됨'
                              AND start_time < ? AND end_time > ? 
                            """, (space_id, res_date, end_time, start_time)
                        ).fetchone()[0]

                        if is_available > 0:
                            message = "선택한 공간이 해당 시간에 이미 예약되었습니다."
                        else:
                            # 최종 예약
                            conn.execute("""
                                INSERT INTO Reservation (user_id, space_id, reservation_date, start_time, end_time, purpose, status)
                                VALUES (?, ?, ?, ?, ?, ?, '예약됨')
                            """, (session['user_id'], space_id, res_date, start_time, end_time, purpose, )) 
                            conn.commit()
                            message = "✅ 예약이 성공적으로 완료되었습니다!"
            except Exception as e:
                conn.rollback()
                message = f"예약 중 오류 발생: {e}"


    # --- 2. GET 요청 처리 (공간 목록 조회) ---
    search_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    search_start = request.args.get('start', '09:00:00')
    search_end = request.args.get('end', '18:00:00')

    if conn:
        try:
            # 사용 중지되지 않고, 예약 충돌도 없는 공간만 조회 (Space_stop 사용, released 조건 제거)
            available_spaces_query = f"""
                SELECT space_id, space_name, location, capacity, space_type 
                FROM Space 
                WHERE space_id NOT IN (
                    -- 1. 예약 충돌 확인
                    SELECT DISTINCT space_id FROM Reservation
                    WHERE reservation_date = ? AND status = '예약됨'
                      AND start_time < ? AND end_time > ? 
                )
                AND space_id NOT IN (
                    -- 2. 장소 사용 중지 확인 (검색 날짜가 중지 기간 안에 있는 경우)
                    SELECT DISTINCT space_id FROM Space_stop
                    WHERE ? BETWEEN start_date AND end_date
                )
                ORDER BY location, space_name
            """
            
            params = [
                search_date, search_end, search_start, # 예약 충돌 체크
                search_date # 장소 사용 중지 체크
            ]
            
            cursor = conn.execute(available_spaces_query, params)
            spaces = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            spaces = f"공간 조회 오류: {e}"


    # --- 3. HTML 렌더링 ---
    html = f"""
    <!DOCTYPE html>
    <title>공간 예약</title>
    <h1>공간 예약하기</h1>
    <a href="{url_for('dashboard')}">대시보드로 돌아가기</a>
    <hr>
    
    <h2>1. 예약 시간 설정 및 가용 공간 검색</h2>
    <form method="GET" action="{url_for('reservation_form')}">
        날짜: <input type="date" name="date" value="{search_date}" required>
        시작 시간: <input type="time" name="start" value="{search_start[:5]}" required>
         종료 시간: <input type="time" name="end" value="{search_end[:5]}" required>
        <button type="submit">공간 검색</button>
    </form>
    
    <p>검색 기간: {search_date} {search_start[:5]} ~ {search_end[:5]}</p>
    
    <h2 style="color:{'green' if '성공' in message else 'red'};">{message}</h2>
    
    <table border="1">
        <tr><th>ID</th><th>공간 이름</th><th>위치</th><th>최대 인원</th><th>타입</th></tr>
    """
    
    if isinstance(spaces, str):
         html += f'<tr><td colspan="5" style="color:red">{spaces}</td></tr></table>'
    elif not spaces:
        html += '<tr><td colspan="5">검색된 시간에 예약 가능한 공간이 없습니다. (예약 충돌 또는 사용 중지 확인)</td></tr></table>'
    else:
        html += '</table><hr><h2>2. 공간 선택 및 예약</h2>'
        html += f'<form method="POST" action="{url_for("reservation_form")}" onsubmit="return confirm(\'선택한 공간을 예약하시겠습니까? (예약 전 벌점 상태를 다시 확인해주세요.)\');">'
        
        html += f'<input type="hidden" name="reservation_date" value="{search_date}">'
        html += f'<input type="hidden" name="start_time" value="{search_start[:5]}">'
        html += f'<input type="hidden" name="end_time" value="{search_end[:5]}">'

        html += '<table border="1"><tr><th>선택</th><th>공간 이름</th><th>위치</th><th>최대 인원</th><th>타입</th></tr>'
        for s in spaces:
            html += f"""
            <tr>
                <td><input type="radio" name="space_id" value="{s['space_id']}" required></td>
                <td>{s['space_name']}</td>
                <td>{s['location']}</td>
                <td>{s['capacity']}명</td>
                <td>{s['space_type']}</td>
            </tr>
            """
        html += "</table><br>"
        
        html += '<label>사용 목적:</label><br>'
        html += '<input type="text" name="purpose" required><br><br>' 
        html += '<button type="submit">선택한 공간 예약 확정</button>'
        html += '</form>'

    return html

# -----------------------------------------------------------
# 메인 실행
# -----------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)