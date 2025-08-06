#!/usr/bin/env python3
"""
TFCI MCP Client for Time Series Prediction
"""

import json
import subprocess
import sys
import time
import threading
from typing import Dict, Any

class TFCIMCPClient:
    def __init__(self, server_script: str = None):
        """
        TFCI MCP 클라이언트 초기화
        
        Args:
            server_script (str, optional): 서버 스크립트 경로. None이면 기본 경로 사용
        """
        if server_script is None:
            # 패키지 내부의 서버 스크립트 경로
            import os
            package_dir = os.path.dirname(os.path.abspath(__file__))
            server_script = os.path.join(package_dir, "server.py")
        
        self.server_script = server_script
        self.process = None
        self.server_logs = []

    def _log_server_output(self):
        """서버 출력을 실시간으로 로그에 저장"""
        while self.process and self.process.poll() is None:
            line = self.process.stdout.readline()
            if line:
                log_line = line.strip()
                self.server_logs.append(log_line)
                print(f"[SERVER] {log_line}")
            else:
                time.sleep(0.1)

    def start_server(self):
        """MCP 서버 시작"""
        try:
            self.process = subprocess.Popen(
                [sys.executable, self.server_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            print("[INFO] TFCI MCP 서버가 시작되었습니다.")
            
            # 서버 로그를 실시간으로 읽는 스레드 시작
            self.log_thread = threading.Thread(target=self._log_server_output)
            self.log_thread.daemon = True
            self.log_thread.start()
            
            # 서버가 시작될 때까지 잠시 대기
            time.sleep(2)
            return True
        except Exception as e:
            print(f"[ERROR] 서버 시작 실패: {e}")
            return False

    def stop_server(self):
        """MCP 서버 종료"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("[INFO] TFCI MCP 서버가 종료되었습니다.")

    def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """JSON-RPC 요청 전송"""
        if not self.process:
            return {"error": "서버가 시작되지 않았습니다."}

        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }

        try:
            # 요청 전송
            request_str = json.dumps(request, ensure_ascii=False) + "\n"
            self.process.stdin.write(request_str)
            self.process.stdin.flush()

            # 응답 수신 (완료될 때까지 대기)
            response_lines = []
            
            while True:
                if self.process.stdout.readable():
                    line = self.process.stdout.readline()
                    if line:
                        response_lines.append(line.strip())
                        # JSON 응답을 찾으면 중단
                        try:
                            json.loads(line.strip())
                            break
                        except json.JSONDecodeError:
                            continue
                else:
                    time.sleep(0.1)
            
            # 마지막 JSON 응답 찾기
            for line in reversed(response_lines):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
            
            return {"error": "서버 응답을 파싱할 수 없습니다."}

        except Exception as e:
            return {"error": f"요청 전송 실패: {e}"}

    def predict(self, config_path: str) -> Dict[str, Any]:
        """
        YAML 설정으로 예측 실행
        
        Args:
            config_path (str): 설정 파일 경로
            
        Returns:
            Dict[str, Any]: 예측 결과
        """
        print(f"[INFO] 예측 시작: {config_path}")
        result = self.send_request("predict", {"config_path": config_path})
        print(f"[INFO] 예측 완료: {result}")
        return result 