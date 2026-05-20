from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import json
import os

# Swagger UI에 표시될 API 메타데이터 작성
app = FastAPI(
    title="Course Records API",
    description="JSON 기반 수강기록 관리 REST API",
    version="1.0.0"
)

FILE_PATH = "courses.json"

# 1. 정규표현식(Regex)을 활용한 엄격한 데이터 검증
class Course(BaseModel):
    course_name: str = Field(..., min_length=1, max_length=50, description="과목명 (1~50자)")
    year: str = Field(..., pattern=r"^\d{4}$", description="이수연도 (4자리 숫자, 예: 2026)")
    semester: str = Field(..., pattern=r"^(1|2|여름|겨울)$", description="이수학기 (1, 2, 여름, 겨울 중 택 1)")
    grade: str = Field(..., pattern=r"^(A\+|A0|B\+|B0|C\+|C0|D\+|D0|F|P|NP)$", description="성적 (예: A+, B0, P)")

# 파일 읽기 헬퍼 함수 (파일 손상, 미존재 에러 방어)
def read_courses_from_file():
    if not os.path.exists(FILE_PATH):
        return []
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return [] # 파일 안의 JSON 형식이 깨졌을 경우 빈 리스트 반환

# 2. GET /courses: 전체 수강기록 조회
@app.get("/courses")
def get_courses():
    courses = read_courses_from_file()
    return courses

# 3. POST /courses: 새로운 수강기록 추가
@app.post("/courses")
def add_course(course: Course):
    try:
        # 기존 데이터 안전하게 불러오기
        data = read_courses_from_file()
        
        # Pydantic 모델을 딕셔너리로 변환하여 리스트에 추가 (Pydantic v2 기준)
        new_course = course.model_dump()
        data.append(new_course)
        
        # 파일에 덮어쓰기
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return {"message": "과목이 성공적으로 추가되었습니다.", "data": new_course}
    
    except Exception as e:
        # 예기치 못한 서버 내부 에러 발생 시 앱 강제 종료 방지
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생하여 데이터를 저장하지 못했습니다.")