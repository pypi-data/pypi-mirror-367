import json
import sys
import traceback
import os
import yaml
import pandas as pd
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

# DB 연결
try:
    import ibm_db
    import ibm_db_dbi
    IBM_DB_AVAILABLE = True
except ImportError:
    IBM_DB_AVAILABLE = False
    print("[ERROR] ibm_db 모듈이 필요합니다.", file=sys.stderr)

# OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[WARNING] openai 패키지가 없습니다.", file=sys.stderr)

class CBCIMCPServer:
    """LLM 파라미터 추출 기반 CBCI MCP 서버"""
    
    def __init__(self):
        self.config = {}
        self.db_config = {}
        self.questions = {}
        self.schema_info = ""
        self.db_connection = None
        self.openai_client = None
        self.initialized = False
        
    def setup(self, config_path: str, questions_path: str = None, schema_path: str = None) -> Dict[str, Any]:
        """설정 로드"""
        try:
            if not os.path.exists(config_path):
                return {"status": "error", "message": f"설정 파일 없음: {config_path}"}
            
            # 기본 경로 설정 (하위 호환성)
            if questions_path is None:
                questions_path = os.path.join(os.path.dirname(config_path), "questions.yaml")
            if schema_path is None:
                schema_path = os.path.join(os.path.dirname(config_path), "schema.yaml")
            
            # 1. 메인 설정 (DB 연결 정보 포함)
            self.config = self._load_yaml(config_path)
            self.db_config = self.config.get("database", {})
            
            # 2. DB 스키마
            if os.path.exists(schema_path):
                schema_data = self._load_yaml(schema_path)
                self.schema_info = self._build_schema_info(schema_data)
            else:
                return {"status": "error", "message": f"스키마 파일 없음: {schema_path}"}
            
            # 3. 질문 데이터베이스
            if os.path.exists(questions_path):
                self.questions = self._load_yaml(questions_path)
            else:
                return {"status": "error", "message": f"질문 파일 없음: {questions_path}"}
            
            # 4. OpenAI 초기화
            if OPENAI_AVAILABLE:
                api_key = self.config.get("openai", {}).get("api_key")
                if api_key:
                    self.openai_client = OpenAI(api_key=api_key)
            
            self.initialized = True
            return {"status": "success", "message": "CBCI 설정 완료"}
            
        except Exception as e:
            return {"status": "error", "message": f"설정 실패: {str(e)}"}
    
    def _load_yaml(self, file_path: str) -> dict:
        """YAML 로드"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def _build_schema_info(self, schema_data: dict) -> str:
        """스키마 정보를 텍스트로 구성"""
        tables = schema_data.get("tables", {})
        info = "데이터베이스 테이블:\n"
        for table, details in tables.items():
            info += f"- {table}: {details.get('description', '')}\n"
            for col, desc in details.get('columns', {}).items():
                info += f"  * {col}: {desc}\n"
        return info
    
    def _get_connection(self):
        """DB 연결 (재사용)"""
        if not IBM_DB_AVAILABLE:
            return None
            
        try:
            if self.db_connection is None or not self._test_connection():
                conn_str = f"DATABASE={self.db_config.get('database')};HOSTNAME={self.db_config.get('host')};PORT={self.db_config.get('port')};UID={self.db_config.get('user')};PWD={self.db_config.get('password')};"
                self.db_connection = ibm_db.connect(conn_str, "", "")
            return self.db_connection
        except Exception as e:
            print(f"[ERROR] DB 연결 실패: {e}", file=sys.stderr)
            return None
    
    def _test_connection(self) -> bool:
        """연결 상태 확인"""
        try:
            return self.db_connection and ibm_db.active(self.db_connection)
        except:
            return False
    
    def _execute_sql(self, sql: str) -> Optional[List[Dict]]:
        """최적화된 SQL 실행"""
        conn = self._get_connection()
        if not conn:
            return None
            
        try:
            dbi_conn = ibm_db_dbi.Connection(conn)
            df = pd.read_sql(sql, dbi_conn)
            
            # 데이터 타입 최적화
            for col in df.columns:
                if 'datetime' in str(df[col].dtype) or 'timestamp' in str(df[col].dtype).lower():
                    df[col] = df[col].astype(str)
            
            return df.to_dict('records')
        except Exception as e:
            print(f"[ERROR] SQL 실행 실패: {e}", file=sys.stderr)
            return None

    def _extract_parameters_with_llm(self, user_question: str) -> Dict[str, str]:
        """LLM을 사용해 질문에서 파라미터 추출"""
        if not self.openai_client:
            return {}

        try:
            prompt = f"""
다음 질문에서 파라미터를 추출해주세요:
질문: "{user_question}"

추출할 파라미터:
- 연도 (CRTR_YR): 4자리 숫자 (예: 2023)
- 지역명 (RGN_NM): 시도명 (서울, 부산, 대구, 인천, 광주, 대전, 울산, 세종, 경기, 강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주)
- 시군구명 (SGG_NM): 구/시/군 (예: 강남구, 수원시, 중구)
- 교육지원청명 (EDOF_NM): 교육지원청명 (예: 대전서부교육지원청)
- 학교유형 (SCHL_TYPE_NM): 유치원, 초등학교, 중학교, 고등학교, 전문대학, 일반대학, 대학원
- 학년 (GRADE): 1, 2, 3, 4, 5, 6, 전체
- 정렬방향 (SORT_ORDER): DESC(내림차순) 또는 ASC(오름차순), 상위/많은/최대=DESC, 하위/적은/최소=ASC

JSON 형태로만 답변해주세요:
{{"CRTR_YR": "값또는null", "RGN_NM": "값또는null", "SGG_NM": "값또는null", "EDOF_NM": "값또는null", "SCHL_TYPE_NM": "값또는null", "GRADE": "값또는null", "SORT_ORDER": "값또는null"}}
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.config.get("openai", {}).get("model", "gpt-4"),
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # JSON 추출
            if result_text.startswith('```json'):
                result_text = result_text[7:-3]
            elif result_text.startswith('```'):
                result_text = result_text[3:-3]
            
            try:
                params = json.loads(result_text)
                # null 값 필터링
                filtered_params = {k: v for k, v in params.items() if v and v != "null"}
                return filtered_params
            except json.JSONDecodeError:
                print(f"[ERROR] JSON 파싱 실패: {result_text}", file=sys.stderr)
                return {}

        except Exception as e:
            print(f"[ERROR] 파라미터 추출 실패: {e}", file=sys.stderr)
            return {}

    def _apply_parameters_to_sql(self, sql_template: str, params: Dict[str, str]) -> str:
        """SQL 템플릿에 파라미터 적용"""
        sql = sql_template
        sql_filters = self.questions.get("sql_filters", {})
        grade_columns = self.questions.get("grade_columns", {})
        
        # 1. SQL 필터 적용
        for filter_name, filter_template in sql_filters.items():
            placeholder = f"{{{{{filter_name}}}}}"
            
            if filter_name == "REGION_FILTER" and "RGN_NM" in params:
                filter_sql = filter_template.replace("{{RGN_NM}}", params["RGN_NM"])
                sql = sql.replace(placeholder, filter_sql)
            elif filter_name == "SGG_FILTER" and "SGG_NM" in params:
                filter_sql = filter_template.replace("{{SGG_NM}}", params["SGG_NM"])
                sql = sql.replace(placeholder, filter_sql)
            elif filter_name == "EDOF_FILTER" and "EDOF_NM" in params:
                filter_sql = filter_template.replace("{{EDOF_NM}}", params["EDOF_NM"])
                sql = sql.replace(placeholder, filter_sql)
            elif filter_name == "YEAR_FILTER" and "CRTR_YR" in params:
                filter_sql = filter_template.replace("{{CRTR_YR}}", params["CRTR_YR"])
                sql = sql.replace(placeholder, filter_sql)
            elif filter_name == "SCHOOL_TYPE_FILTER" and "SCHL_TYPE_NM" in params:
                filter_sql = filter_template.replace("{{SCHL_TYPE_NM}}", params["SCHL_TYPE_NM"])
                sql = sql.replace(placeholder, filter_sql)
            elif filter_name == "SORT_ORDER" and "SORT_ORDER" in params:
                sql = sql.replace(placeholder, params["SORT_ORDER"])
            else:
                # 해당 필터가 없으면 제거
                sql = sql.replace(placeholder, "")
        
        # 2. 학년별 컬럼 매핑 적용
        if "{{GRADE_COLUMN}}" in sql and "GRADE" in params:
            grade = params["GRADE"]
            if grade in grade_columns:
                grade_column = grade_columns[grade]
                sql = sql.replace("{{GRADE_COLUMN}}", grade_column)
            else:
                # 기본값: 전체
                sql = sql.replace("{{GRADE_COLUMN}}", grade_columns.get("전체", "SUM(GRDR1_STDNT_NOPE + GRDR2_STDNT_NOPE + GRDR3_STDNT_NOPE + GRDR4_STDNT_NOPE + GRDR5_STDNT_NOPE + GRDR6_STDNT_NOPE)"))
        
        # 3. 연도가 없으면 최신 연도로 대체
        if "{{YEAR_FILTER}}" in sql:
            sql = sql.replace("{{YEAR_FILTER}}", "AND A.CRTR_YR = (SELECT MAX(CRTR_YR) FROM DSTDM.T_PBAF3101S)")
        
        return sql

    def _find_question(self, user_input: str) -> Optional[Dict]:
        """효율적인 질문 매칭 (새로운 형식 지원)"""
        user_lower = user_input.lower()
        qa_pairs = self.questions.get("qa_pairs", [])
        
        best_match = None
        best_score = 0
        
        for qa in qa_pairs:
            if not qa.get("verified", False):
                continue
                
            keywords = qa.get("keywords", [])
            if not keywords:
                continue
            
            # 키워드 매칭
            matched_count = 0
            for keyword in keywords:
                if keyword.lower() in user_lower:
                    matched_count += 1
            
            # 매칭 점수 계산
            score = matched_count / len(keywords)
            
            # 추가 점수: 질문 자체와의 유사도 (파라미터 제외)
            question_base = qa.get("question", "").lower()
            question_base = re.sub(r'\d{4}년?', '', question_base)
            question_base = re.sub(r'[가-힣]+(?:구|시|군)', '', question_base)
            question_keywords = question_base.split()
            question_match = sum(1 for word in question_keywords if word in user_lower)
            question_score = question_match / len(question_keywords) if question_keywords else 0
            
            # 최종 점수 (키워드 매칭 70% + 질문 유사도 30%)
            final_score = (score * 0.7) + (question_score * 0.3)
            
            if final_score > best_score:
                best_score = final_score
                best_match = qa
        
        threshold = self.questions.get("matching", {}).get("similarity_threshold", 0.3)
        return best_match if best_score >= threshold else None
    
    def ask(self, question: str) -> Dict[str, Any]:
        """질문 처리 (새로운 워크플로우)"""
        try:
            if not self.initialized:
                return {"status": "error", "message": "setup()을 먼저 호출하세요"}
            
            # 1. 질문 매칭
            matched_qa = self._find_question(question)
            
            if matched_qa:
                # 2. LLM으로 파라미터 추출
                params = self._extract_parameters_with_llm(question)
                
                # 3. SQL 템플릿에 파라미터 적용
                sql_template = matched_qa.get("sql_template", "")
                if sql_template:
                    sql = self._apply_parameters_to_sql(sql_template, params)
                    
                    # 4. SQL 실행
                    data = self._execute_sql(sql)
                    
                    if data:
                        # 5. 답변 생성
                        template = matched_qa.get("answer_template", "")
                        answer = self._format_answer(template, data[0] if data else {})
                        
                        return {
                            "status": "success",
                            "question": question,
                            "answer": answer,
                            "qa_id": matched_qa.get("id"),
                            "rows": len(data),
                            "extracted_params": params
                        }
                    else:
                        return {"status": "error", "message": "데이터 조회 실패"}
                else:
                    return {"status": "error", "message": "SQL 템플릿 없음"}
            
            else:
                # 6. 일반 대화
                if self.openai_client:
                    return self._chat(question)
                else:
                    fallback = self.questions.get("matching", {}).get("fallback_message", "해당 질문을 처리할 수 없습니다.")
                    return {"status": "error", "message": fallback}
                    
        except Exception as e:
            print(f"[ERROR] 질문 처리 실패: {e}", file=sys.stderr)
            traceback.print_exc()
            return {"status": "error", "message": f"처리 중 오류: {str(e)}"}
    
    def _format_answer(self, template: str, data: Dict) -> str:
        """답변 포맷팅"""
        try:
            # NULL 값이나 빈 값 체크
            for key, value in data.items():
                if value is None:
                    return f"해당 조건에 맞는 데이터를 찾을 수 없습니다. 다른 조건으로 시도해보세요."
                if isinstance(value, (int, float)) and value == 0:
                    return f"해당 조건의 데이터가 0입니다. 다른 조건으로 시도해보세요."
            
            return template.format(**data)
        except Exception as e:
            return f"조회 결과: {data}"
    
    def _chat(self, question: str) -> Dict[str, Any]:
        """일반 대화"""
        try:
            model = self.config.get("openai", {}).get("model", "gpt-4")
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "교육 데이터 분석 전문 어시스턴트입니다."},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return {
                "status": "success", 
                "question": question,
                "answer": response.choices[0].message.content,
                "type": "chat"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"대화 실패: {str(e)}"}
    
    def get_questions(self) -> Dict[str, Any]:
        """사용 가능한 질문들"""
        if not self.initialized:
            return {"status": "error", "message": "setup()을 먼저 호출하세요"}
        
        qa_pairs = self.questions.get("qa_pairs", [])
        questions = [qa["question"] for qa in qa_pairs if qa.get("verified", False)]
        
        return {
            "status": "success",
            "questions": questions,
            "count": len(questions)
        }

def handle_request(server: CBCIMCPServer, request: Dict[str, Any]) -> Dict[str, Any]:
    """요청 처리"""
    try:
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "setup":
            config_path = params.get("config_path", "")
            questions_path = params.get("questions_path", "")
            schema_path = params.get("schema_path", "")
            result = server.setup(config_path, questions_path, schema_path)
        elif method == "ask":
            question = params.get("question", "")
            result = server.ask(question)
        elif method == "get_questions":
            result = server.get_questions()
        else:
            result = {"status": "error", "message": f"지원하지 않는 메소드: {method}"}
            
        return {"jsonrpc": "2.0", "id": request.get("id"), "result": result}
        
    except Exception as e:
        return {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32603, "message": f"내부 오류: {str(e)}"}}

def main():
    """서버 시작"""
    server = CBCIMCPServer()
    print("CBCI MCP Server 시작", file=sys.stderr)
    
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
                
            try:
                request = json.loads(line.strip())
                response = handle_request(server, request)
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
            except json.JSONDecodeError:
                error = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON 파싱 오류"}}
                print(json.dumps(error, ensure_ascii=False))
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        print("\n서버 종료", file=sys.stderr)
    except Exception as e:
        print(f"서버 오류: {e}", file=sys.stderr)

if __name__ == "__main__":
    main() 