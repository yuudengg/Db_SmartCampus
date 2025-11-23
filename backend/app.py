import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, date, timedelta

# -----------------------------------------------------------
# 기본 설정
# -----------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_strong_secret_key_here'
app.config['JSON_AS_ASCII'] = False
DATABASE = 'db_project_table'

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = {
            "Access-Control-Allow-Origin": "https://smartcampus1.vercel.app",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS"
        }
        for k, v in headers.items():
            response.headers[k] = v
        return response


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "https://smartcampus1.vercel.app")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    return response


# ✅ React 연동 허용
CORS(
    app,
    resources={r"/api/*": {"origins": "https://smartcampus1.vercel.app"}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)


# -----------------------------------------------------------
# DB 연결 함수
# -----------------------------------------------------------
def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        print(f"DB 연결 실패: {e}")
        return None

# -----------------------------------------------------------
# 유틸 함수 (벌점/노쇼)
# -----------------------------------------------------------
def get_total_active_penalty_days(conn, user_id):
    penalties = conn.execute("""
        SELECT penalty_period, penalty_date 
        FROM Penalty 
        WHERE user_id = ? AND released = 0
    """, (user_id,)).fetchall()

    today = datetime.now().date()
    total_effective_penalty = 0

    for p in penalties:
        penalty_date = datetime.strptime(p['penalty_date'], '%Y-%m-%d').date()
        days_passed = (today - penalty_date).days
        remaining = max(0, p['penalty_period'] - days_passed)
        total_effective_penalty += remaining
    return total_effective_penalty


def process_daily_tasks(conn):
    now = datetime.now()
    now_dt_str = now.strftime('%Y-%m-%d %H:%M:%S')

    no_show_targets = conn.execute("""
        SELECT R.reservation_id, R.user_id 
        FROM Reservation R
        WHERE R.status = '예약됨' AND R.usage_status = 0
          AND (R.reservation_date || ' ' || R.end_time) < ?
    """, (now_dt_str,)).fetchall()

    for target in no_show_targets:
        user_id = target['user_id']
        conn.execute("UPDATE Reservation SET status = '노쇼' WHERE reservation_id = ?", (target['reservation_id'],))

        no_show_count = conn.execute(
            "SELECT COUNT(*) AS count FROM Reservation WHERE user_id = ? AND status = '노쇼'", 
            (user_id,)
        ).fetchone()['count']

        if no_show_count >= 3:
            conn.execute("""
                INSERT INTO Penalty (user_id, reason, penalty_date, penalty_period, released)
                VALUES (?, ?, ?, ?, 0)
            """, (user_id, '노쇼 3회 누적 자동 제한', now.strftime('%Y-%m-%d'), 3))
            conn.execute("UPDATE Reservation SET status = '노쇼-처리됨' WHERE user_id = ? AND status = '노쇼'", (user_id,))
    conn.commit()

@app.route("/")
def home():
    return jsonify({"msg": "✅ CORS OK"})

# -----------------------------------------------------------
# ✅ API: 사용자 로그인
# -----------------------------------------------------------
@app.route('/api/login/user', methods=['POST'])
def api_user_login():
    data = request.get_json()
    login_id = data.get('login_id')
    password = data.get('password')

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "DB 연결 실패"}), 500

    user = conn.execute(
        "SELECT user_id, name, role FROM User WHERE login_id = ? AND password = ?",
        (login_id, password)
    ).fetchone()

    if user:
        return jsonify({
            "success": True,
            "user_id": user["user_id"],
            "name": user["name"],
            "role": user["role"],
            "login_id": login_id
        }), 200
    else:
        return jsonify({"success": False, "message": "ID 또는 비밀번호가 올바르지 않습니다."}), 401


# -----------------------------------------------------------
# ✅ API: 관리자 로그인
# -----------------------------------------------------------
@app.route('/api/login/admin', methods=['POST'])
def api_admin_login():
    data = request.get_json()
    admin_id = data.get('admin_id')

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "DB 연결 실패"}), 500

    admin = conn.execute(
        "SELECT admin_id, name, department FROM Admin WHERE admin_id = ?",
        (admin_id,)
    ).fetchone()

    if admin:
        return jsonify({
            "success": True,
            "admin_id": admin["admin_id"],
            "name": admin["name"],
            "role": "관리자",
            "department": admin["department"]
        }), 200
    else:
        return jsonify({"success": False, "message": "관리자 번호가 올바르지 않습니다."}), 401


# -----------------------------------------------------------
# ✅ API: 회원가입 (학생/교수)
# -----------------------------------------------------------
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    name = data.get('name')
    login_id = data.get('login_id')
    password = data.get('password')
    role = data.get('role')

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "DB 연결 실패"}), 500

    try:
        cursor = conn.execute(
            "INSERT INTO User (name, role, login_id, password) VALUES (?, ?, ?, ?)",
            (name, role, login_id, password)
        )
        user_id = cursor.lastrowid

        if role == "학생":
            student_id = data.get("student_id")
            grade = data.get("grade")
            major = data.get("major")
            conn.execute(
                "INSERT INTO Student (student_id, user_id, grade, major) VALUES (?, ?, ?, ?)",
                (student_id, user_id, grade, major)
            )
        elif role == "교수":
            professor_id = data.get("professor_id")
            department = data.get("department")
            position = data.get("position")
            conn.execute(
                "INSERT INTO Professor (professor_id, user_id, department, position) VALUES (?, ?, ?, ?)",
                (professor_id, user_id, department, position)
            )

        conn.commit()
        return jsonify({"success": True, "message": "회원가입이 완료되었습니다."}), 201

    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({"success": False, "message": "이미 존재하는 아이디나 학번/교번입니다."}), 409
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"회원가입 오류: {e}"}), 500


# -----------------------------------------------------------
# ✅ API: 아이디 중복확인
# -----------------------------------------------------------
@app.route('/api/check-id', methods=['POST'])
def check_id():
    """아이디 중복 확인 API (React 전용)"""
    try:
        data = request.get_json(force=True)
        login_id = data.get('login_id')

        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "DB 연결 실패"}), 500

        existing_user = conn.execute(
            "SELECT user_id FROM User WHERE login_id = ?", (login_id,)
        ).fetchone()

        if existing_user:
            return jsonify({
                "exists": True,
                "message": "이미 사용 중인 아이디입니다."
            }), 200
        else:
            return jsonify({
                "exists": False,
                "message": "사용 가능한 아이디입니다."
            }), 200
    except Exception as e:
        print(f"❌ check-id error: {e}")
        return jsonify({
            "exists": False,
            "message": f"서버 오류 발생: {str(e)}"
        }), 500


# -----------------------------------------------------------
# ✅ API: 아이디 편집
# -----------------------------------------------------------
@app.route('/api/user/edit', methods=['PUT'])
def edit_user():
    try:
        data = request.get_json()
        login_id = data.get('login_id')
        password = data.get('password')
        name = data.get('name')
        user_id = data.get('user_id')

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row  # ✅ Row를 dict처럼 접근 가능하게 설정
        cursor = conn.cursor()

        existing_user = cursor.execute(
            "SELECT login_id, password, name, role FROM User WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        if not existing_user:
            return jsonify({"success": False, "message": "사용자를 찾을 수 없습니다."}), 404

        # ✅ sqlite3.Row → dict로 변환 (안전하게)
        existing_user = dict(existing_user)

        # ✅ 빈칸은 기존 값 유지
        login_id = login_id.strip() or existing_user.get("login_id")
        password = password.strip() or existing_user.get("password")
        name = name.strip() or existing_user.get("name")

        cursor.execute(
            "UPDATE User SET login_id = ?, password = ?, name = ? WHERE user_id = ?",
            (login_id, password, name, user_id)
        )
        conn.commit()

        updated_user = cursor.execute(
            "SELECT user_id, login_id, name, role FROM User WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        return jsonify({
            "success": True,
            "message": "정보가 수정되었습니다!",
            "user": dict(updated_user)
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"서버 오류: {e}"}), 500


@app.route('/api/admin/edit', methods=['PUT'])
def edit_admin():
    try:
        data = request.get_json(force=True)
        print("📩 받은 데이터:", data)

        admin_id = data.get('admin_id')
        if not admin_id:
            return jsonify({"success": False, "message": "admin_id가 누락되었습니다."}), 400

        name = data.get('name', '').strip()
        department = data.get('department', '').strip()

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        existing_admin = cursor.execute(
            "SELECT name, department FROM Admin WHERE admin_id = ?",
            (admin_id,)
        ).fetchone()

        if not existing_admin:
            return jsonify({"success": False, "message": "해당 관리자를 찾을 수 없습니다."}), 404

        existing_admin = dict(existing_admin)

        # ✅ 빈칸이면 기존 값 유지
        name = name or existing_admin.get("name")
        department = department or existing_admin.get("department")

        cursor.execute(
            "UPDATE Admin SET name = ?, department = ? WHERE admin_id = ?",
            (name, department, admin_id)
        )
        conn.commit()

        updated_admin = cursor.execute(
            "SELECT admin_id, name, department FROM Admin WHERE admin_id = ?",
            (admin_id,)
        ).fetchone()

        return jsonify({
            "success": True,
            "message": "정보가 성공적으로 수정되었습니다!",
            "admin": dict(updated_admin)
        }), 200

    except Exception as e:
        print("🚨 edit_admin 오류:", e)
        return jsonify({"success": False, "message": f"서버 오류: {e}"}), 500


# -----------------------------------------------------------
# ✅ API: 사용자 관리
# -----------------------------------------------------------
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    """관리자: 모든 사용자 목록 조회"""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                user_id AS id,
                name,
                role,
                0 AS noShow,     -- (노쇼 기능 미구현이면 임시로 0)
                0 AS isStop      -- (정지 여부 기본값 false)
            FROM User
        """)
        rows = cursor.fetchall()
        users = [dict(row) for row in rows]

        return jsonify({"success": True, "data": users}), 200

    except Exception as e:
        print("🚨 사용자 목록 조회 오류:", e)
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        conn.close()


# -----------------------------------------------------------
# ✅ API: 관리자 공간 관리
# -----------------------------------------------------------
@app.route('/api/admin/spaces/edit', methods=['PUT'])
def edit_space_info():
    """관리자: 공간 정보 및 사용중지 기간 수정"""
    try:
        data = request.get_json(force=True)
        print("📩 받은 데이터:", data)

        space_id = data.get("space_id")
        space_name = data.get("space_name", "").strip()
        capacity = data.get("capacity")
        start_date = data.get("disable_start", "").strip()
        end_date = data.get("disable_end", "").strip()

        if not space_id:
            return jsonify({"success": False, "message": "space_id가 누락되었습니다."}), 400

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # ✅ 1️⃣ Space 테이블 수정
        cursor.execute("""
            UPDATE Space
            SET 
                space_name = COALESCE(NULLIF(?, ''), space_name),
                capacity = COALESCE(?, capacity)
            WHERE space_id = ?
        """, (space_name, capacity, space_id))

        # ✅ 2️⃣ Space_Stop 테이블 처리
        # 이미 중지 기간이 존재하면 수정, 없으면 삽입
        if start_date and end_date:
            existing_stop = cursor.execute(
                "SELECT stop_id FROM Space_Stop WHERE space_id = ?",
                (space_id,)
            ).fetchone()

            if existing_stop:
                cursor.execute("""
                    UPDATE Space_Stop 
                    SET start_date = ?, end_date = ?
                    WHERE space_id = ?
                """, (start_date, end_date, space_id))
            else:
                cursor.execute("""
                    INSERT INTO Space_Stop (space_id, start_date, end_date)
                    VALUES (?, ?, ?)
                """, (space_id, start_date, end_date))
        else:
            # 만약 start/end가 비어있으면 사용중지 해제 (기존 기록 삭제)
            cursor.execute("DELETE FROM Space_Stop WHERE space_id = ?", (space_id,))

        conn.commit()

        # ✅ 3️⃣ 수정된 최신 정보 반환
        updated = cursor.execute("""
            SELECT 
                s.space_id, s.space_name, s.capacity, s.location,
                ss.start_date AS disable_start, ss.end_date AS disable_end
            FROM Space s
            LEFT JOIN Space_Stop ss ON s.space_id = ss.space_id
            WHERE s.space_id = ?
        """, (space_id,)).fetchone()

        return jsonify({
            "success": True,
            "message": "공간 정보가 수정되었습니다!",
            "data": dict(updated)
        }), 200

    except Exception as e:
        print("🚨 공간 수정 오류:", e)
        return jsonify({"success": False, "message": f"서버 오류: {e}"}), 500

    finally:
        conn.close()


@app.route('/api/spaces/stop', methods=['POST'])
def save_space_stop():
    """관리자: 공간 사용중지 기간 저장"""
    try:
        data = request.get_json()
        stops = data.get('stops', [])

        conn = get_db_connection()
        cursor = conn.cursor()

        for stop in stops:
            space_id = stop.get('space_id')
            start_date = stop.get('start_date')
            end_date = stop.get('end_date')

            # 기존 중지 내역 삭제 (중복 방지)
            cursor.execute("DELETE FROM Space_Stop WHERE space_id = ?", (space_id,))
            # 새로 삽입
            cursor.execute("""
                INSERT INTO Space_Stop (space_id, start_date, end_date)
                VALUES (?, ?, ?)
            """, (space_id, start_date, end_date))

        conn.commit()
        return jsonify({"success": True, "message": "사용 중지 기간이 저장되었습니다!"}), 200

    except Exception as e:
        conn.rollback()
        print("🚨 공간 중지 저장 오류:", e)
        return jsonify({"success": False, "message": f"서버 오류: {e}"}), 500

    finally:
        conn.close()


@app.route('/api/spaces/stop-list', methods=['GET'])
def get_space_stop_list():
    """관리자: 사용중지된 공간 목록 조회"""
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                ss.stop_id AS id,
                s.space_name AS spaceName,
                ss.start_date AS startDate,
                ss.end_date AS endDate
            FROM Space_Stop ss
            JOIN Space s ON ss.space_id = s.space_id
            ORDER BY ss.start_date DESC
        """)

        stops = [dict(row) for row in cursor.fetchall()]
        return jsonify({"success": True, "data": stops}), 200

    except Exception as e:
        print("🚨 사용중지 목록 조회 오류:", e)
        return jsonify({"success": False, "message": f"서버 오류: {e}"}), 500
    finally:
        conn.close()


@app.route('/api/spaces/stop/<int:stop_id>', methods=['DELETE'])
def delete_space_stop(stop_id):
    """관리자: 사용중지 해제 (삭제)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Space_Stop WHERE stop_id = ?", (stop_id,))
        conn.commit()
        return jsonify({"success": True, "message": "공간 사용중지가 해제되었습니다."}), 200
    except Exception as e:
        conn.rollback()
        print("🚨 사용중지 해제 오류:", e)
        return jsonify({"success": False, "message": f"서버 오류: {e}"}), 500
    finally:
        conn.close()


# -----------------------------------------------------------
# ✅ API: 관리자 예약 관리
# -----------------------------------------------------------
@app.route('/api/admin/reservations', methods=['GET'])
def get_all_reservations():
    """관리자: 모든 예약 목록 조회"""
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                r.reservation_id AS id,
                u.name AS userName,
                s.space_name AS spaceName,
                r.reservation_date AS date,
                r.start_time || ' ~ ' || r.end_time AS time,
                r.purpose AS purpose,
                r.status AS status
            FROM Reservation r
            JOIN User u ON r.user_id = u.user_id
            JOIN Space s ON r.space_id = s.space_id
            ORDER BY r.reservation_date DESC, r.start_time ASC
        """)

        data = [dict(row) for row in cursor.fetchall()]
        return jsonify({"success": True, "data": data}), 200

    except Exception as e:
        print("🚨 예약 목록 조회 오류:", e)
        return jsonify({"success": False, "message": f"서버 오류: {e}"}), 500

    finally:
        conn.close()


@app.route('/api/admin/reservations/edit', methods=['PUT'])
def admin_edit_reservation():
    """관리자: 예약 수정"""
    try:
        data = request.get_json()
        reservation_id = data.get("id")
        new_date = data.get("date")
        new_time = data.get("time")
        purpose = data.get("purpose")

        if not reservation_id:
            return jsonify({"success": False, "message": "예약 ID가 없습니다."}), 400

        # 시간 문자열 분리 ("10:00 ~ 12:00")
        if new_time and " ~ " in new_time:
            start_time, end_time = [t.strip() for t in new_time.split("~")]
        else:
            start_time, end_time = None, None

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Reservation
            SET reservation_date = COALESCE(?, reservation_date),
                start_time = COALESCE(?, start_time),
                end_time = COALESCE(?, end_time),
                purpose = COALESCE(?, purpose)
            WHERE reservation_id = ?
        """, (new_date, start_time, end_time, purpose, reservation_id))
        conn.commit()

        updated = cursor.execute("""
            SELECT 
                r.reservation_id AS id,
                u.name AS userName,
                s.space_name AS spaceName,
                r.reservation_date AS date,
                r.start_time || ' ~ ' || r.end_time AS time,
                r.purpose AS purpose,
                r.status AS status
            FROM Reservation r
            JOIN User u ON r.user_id = u.user_id
            JOIN Space s ON r.space_id = s.space_id
            WHERE r.reservation_id = ?
        """, (reservation_id,)).fetchone()

        return jsonify({"success": True, "message": "예약 수정 완료", "data": dict(updated)}), 200

    except Exception as e:
        print("🚨 예약 수정 오류:", e)
        return jsonify({"success": False, "message": f"서버 오류: {e}"}), 500
    finally:
        conn.close()


@app.route('/api/admin/reservations/cancel', methods=['PUT'])
def admin_cancel_reservation():
    """관리자: 예약 취소"""
    try:
        data = request.get_json()
        reservation_id = data.get("id")

        if not reservation_id:
            return jsonify({"success": False, "message": "예약 ID가 없습니다."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Reservation
            SET status = '예약취소'
            WHERE reservation_id = ?
        """, (reservation_id,))
        conn.commit()

        return jsonify({"success": True, "message": "예약이 취소되었습니다."}), 200

    except Exception as e:
        print("🚨 예약 취소 오류:", e)
        return jsonify({"success": False, "message": f"서버 오류: {e}"}), 500

    finally:
        conn.close()


# -----------------------------------------------------------
# ✅ API: 예약 목록 조회
# -----------------------------------------------------------
@app.route('/api/reservation', methods=['POST'])
def api_reservation():
    """React용 장소 예약 API"""
    data = request.get_json()
    print("📩 받은 데이터:", data)

    user_id = data.get('user_id')
    space_id = data.get('space_id')
    reservation_date = data.get('reservation_date')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    purpose = data.get('purpose')

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # 1️⃣ 공간 사용중지 기간 확인
        stop = cursor.execute("""
            SELECT COUNT(*) AS cnt
            FROM Space_Stop
            WHERE space_id = ?
              AND date(?) BETWEEN start_date AND end_date
        """, (space_id, reservation_date)).fetchone()

        if stop["cnt"] > 0:
            return jsonify({
                "success": False,
                "message": "해당 날짜는 사용중지된 공간입니다!"
            }), 403

        # 2️⃣ 예약 가능한지 확인 (시간 겹침 체크)
        conflict = cursor.execute("""
            SELECT COUNT(*) AS cnt 
            FROM Reservation
            WHERE space_id = ? AND reservation_date = ?
              AND status IN ('예약됨', '사용 완료')
              AND start_time < ? AND end_time > ?
        """, (space_id, reservation_date, end_time, start_time)).fetchone()

        if conflict["cnt"] > 0:
            return jsonify({
                "success": False,
                "message": "이미 예약된 시간대입니다!"
            }), 409

        # 3️⃣ 예약 저장
        cursor.execute("""
            INSERT INTO Reservation (user_id, space_id, reservation_date, start_time, end_time, purpose, status)
            VALUES (?, ?, ?, ?, ?, ?, '예약됨')
        """, (user_id, space_id, reservation_date, start_time, end_time, purpose))
        conn.commit()

        print("✅ 예약 성공:", data)
        return jsonify({"success": True, "message": "예약이 완료되었습니다!"}), 201

    except Exception as e:
        conn.rollback()
        print("🚨 예약 중 오류:", e)
        return jsonify({"success": False, "message": f"서버 오류: {e}"}), 500

    finally:
        conn.close()


@app.route('/api/spaces/stop-periods', methods=['GET'])
def get_space_stop_periods():
    """모든 공간의 사용중지 기간 반환"""
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT space_id, start_date, end_date
            FROM Space_Stop
        """)
        data = [dict(row) for row in cursor.fetchall()]

        return jsonify({"success": True, "data": data}), 200

    except Exception as e:
        print("🚨 사용중지 기간 조회 오류:", e)
        return jsonify({"success": False, "message": f"서버 오류: {e}"}), 500
    finally:
        conn.close()


@app.route('/api/spaces/classroom', methods=['GET'])
def get_classrooms():
    """강의실 목록을 반환하는 API"""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.execute("""
            SELECT 
                s.space_id, s.space_name, s.location, s.capacity,
                ss.start_date AS disable_start,
                ss.end_date AS disable_end
            FROM Space s
            LEFT JOIN Space_Stop ss ON s.space_id = ss.space_id
            WHERE s.space_type = '강의실'
            ORDER BY s.location, s.space_name
        """)
        spaces = [dict(row) for row in cursor.fetchall()]
        return jsonify({"success": True, "data": spaces}), 200
    except Exception as e:
        print("🚨 강의실 조회 오류:", e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/spaces/studyroom', methods=['GET'])
def get_studyrooms():
    """스터디룸 목록을 반환하는 API"""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.execute("""
            SELECT 
                s.space_id, s.space_name, s.location, s.capacity,
                ss.start_date AS disable_start,
                ss.end_date AS disable_end
            FROM Space s
            LEFT JOIN Space_Stop ss ON s.space_id = ss.space_id
            WHERE s.space_type = '스터디룸'
            ORDER BY s.location, s.space_name
        """)
        spaces = [dict(row) for row in cursor.fetchall()]
        return jsonify({"success": True, "data": spaces}), 200
    except Exception as e:
        print("🚨 스터디룸 조회 오류:", e)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/reservations/<int:user_id>', methods=['GET'])
def get_user_reservations(user_id):
    """특정 사용자의 예약 목록 조회"""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT r.reservation_id AS id,
                   u.name AS userName,
                   s.space_name AS spaceName,
                   r.reservation_date AS date,
                   r.start_time || ' ~ ' || r.end_time AS time,
                   r.purpose,
                   r.status
            FROM Reservation r
            JOIN User u ON r.user_id = u.user_id
            JOIN Space s ON r.space_id = s.space_id
            WHERE r.user_id = ? AND r.status != '예약취소'
            ORDER BY r.reservation_date DESC, r.start_time
        """, (user_id,))

        rows = cursor.fetchall()
        reservations = [dict(row) for row in rows]

        return jsonify({
            "success": True,
            "data": reservations
        }), 200

    except Exception as e:
        print("🚨 예약 조회 중 오류:", e)
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        conn.close()

@app.route('/api/reservation/cancel/<int:reservation_id>', methods=['PUT'])
def cancel_reservation(reservation_id):
    """예약 취소 API — status를 '취소됨'으로 변경"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1️⃣ 해당 예약 존재 확인
        cursor.execute("SELECT * FROM Reservation WHERE reservation_id = ?", (reservation_id,))
        reservation = cursor.fetchone()

        if not reservation:
            return jsonify({"success": False, "message": "해당 예약을 찾을 수 없습니다."}), 404

        # 2️⃣ 상태를 '취소됨'으로 변경
        cursor.execute(
            "UPDATE Reservation SET status = '취소됨' WHERE reservation_id = ?",
            (reservation_id,)
        )
        conn.commit()

        return jsonify({"success": True, "message": "예약이 취소되었습니다."}), 200

    except Exception as e:
        conn.rollback()
        print("🚨 예약 취소 중 오류:", e)
        return jsonify({"success": False, "message": f"서버 오류: {e}"}), 500

    finally:
        conn.close()


# -----------------------------------------------------------
# 서버 실행
# -----------------------------------------------------------
if __name__ == "__main__":
    from waitress import serve
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"✅ Flask server starting on port {port}...")
    serve(app, host="0.0.0.0", port=port)

