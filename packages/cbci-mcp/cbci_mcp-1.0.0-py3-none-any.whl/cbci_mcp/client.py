import json
import subprocess
import sys
import time
import threading
import os
from typing import Dict, Any, Optional

class CBCIMCPClient:
    """CBCI MCP 클라이언트"""
    
    def __init__(self, server_script: str = None):
        if server_script is None:
            server_script = os.path.join(os.path.dirname(__file__), "server.py")
        self.server_script = server_script
        self.server_process = None
        self.log_thread = None
        self.ready = False

    def start_server(self):
        """서버 시작"""
        if self.server_process is not None:
            return
        
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, self.server_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # 로그 모니터링
            self.log_thread = threading.Thread(target=self._log_server, daemon=True)
            self.log_thread.start()
            
            time.sleep(1)  # 서버 초기화 대기
            
        except Exception as e:
            print(f"[ERROR] 서버 시작 실패: {e}", file=sys.stderr)
    
    def stop_server(self):
        """서버 종료"""
        if self.server_process:
            try:
                self.server_process.stdin.close()
                self.server_process.terminate()
                self.server_process.wait(timeout=3)
            except:
                self.server_process.kill()
            finally:
                self.server_process = None
                self.ready = False

    def _log_server(self):
        """서버 로그"""
        if self.server_process and self.server_process.stderr:
            for line in iter(self.server_process.stderr.readline, ''):
                if line.strip():
                    print(f"[SERVER] {line.strip()}", file=sys.stderr)

    def _request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """요청 전송"""
        if not self.server_process:
            return {"error": "서버가 시작되지 않았습니다"}
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        try:
            self.server_process.stdin.write(json.dumps(request, ensure_ascii=False) + "\n")
            self.server_process.stdin.flush()
            
            response_line = self.server_process.stdout.readline()
            if response_line:
                return json.loads(response_line.strip())
            else:
                return {"error": "서버 응답 없음"}
        except Exception as e:
            return {"error": f"요청 실패: {str(e)}"}

    # ========== 핵심 API ==========
    
    def setup(self, config: str = "config.yaml", questions: str = "questions.yaml", schema: str = "schema.yaml") -> Dict[str, Any]:
        """설정 로드"""
        # cbci_mcp 디렉토리에서 config 파일들 찾기
        base_dir = os.path.dirname(__file__)
        config_path = os.path.join(base_dir, config)
        questions_path = os.path.join(base_dir, questions)
        schema_path = os.path.join(base_dir, schema)
        
        # 파일 존재 확인
        missing_files = []
        if not os.path.exists(config_path):
            missing_files.append(config)
        if not os.path.exists(questions_path):
            missing_files.append(questions)
        if not os.path.exists(schema_path):
            missing_files.append(schema)
        
        if missing_files:
            return {"status": "error", "message": f"설정 파일 없음: {', '.join(missing_files)}"}
        
        params = {
            "config_path": config_path,
            "questions_path": questions_path,
            "schema_path": schema_path
        }
        response = self._request("setup", params)
        result = response.get("result", {})
        
        if result.get("status") == "success":
            self.ready = True
            return {"status": "success", "message": "CBCI 준비 완료"}
        else:
            return {"status": "error", "message": result.get("message", "설정 실패")}

    def ask(self, question: str) -> str:
        """질문하기"""
        if not self.ready:
            return "❌ setup()을 먼저 호출하세요"
            
        params = {"question": question}
        response = self._request("ask", params)
        result = response.get("result", {})
        
        if result.get("status") == "success":
            return result.get("answer", "답변을 생성할 수 없습니다")
        else:
            error_msg = result.get("message", "알 수 없는 오류")
            return f"❌ {error_msg}"

    def get_questions(self) -> list:
        """사용 가능한 질문 목록"""
        response = self._request("get_questions")
        result = response.get("result", {})
        
        if result.get("status") == "success":
            return result.get("questions", [])
        else:
            return [] 