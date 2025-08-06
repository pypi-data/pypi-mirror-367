#!/usr/bin/env python3
"""
TFCI MCP (Model Context Protocol) Server for Time Series Prediction
"""

import json
import sys
import traceback
import os
from typing import Any, Dict

# 디버깅 정보 출력
print(f"[DEBUG] Python executable: {sys.executable}")
print(f"[DEBUG] Python version: {sys.version}")
print(f"[DEBUG] Working directory: {os.getcwd()}")
print(f"[DEBUG] Python path: {sys.path[:3]}...")  # 처음 3개만 출력

# tfci 패키지 안전한 import
try:
    import tfci
    TFCI_AVAILABLE = True
    print(f"[DEBUG] ✅ tfci import 성공: {tfci.__file__}")
    print(f"[DEBUG] tfci version: {getattr(tfci, '__version__', '버전 정보 없음')}")
except ImportError as e:
    TFCI_AVAILABLE = False
    tfci = None
    print(f"[DEBUG] ❌ tfci import 실패: {e}")
    
    # sys.path 전체 출력
    print("[DEBUG] 전체 sys.path:")
    for i, path in enumerate(sys.path):
        print(f"[DEBUG]   {i}: {path}")

class TFCIMCPServer:
    def __init__(self):
        pass

    def predict(self, config_path: str) -> Dict[str, Any]:
        """YAML 설정 파일로 예측 실행 및 DB 저장"""
        try:
            print(f"[INFO] TFCI MCP 예측 시작: {config_path}")
            
            # tfci 패키지 사용 가능 여부 확인
            if not TFCI_AVAILABLE:
                return {
                    "status": "error", 
                    "message": f"tfci 패키지가 설치되지 않았습니다. Python: {sys.executable}"
                }
            
            # config 파일 존재 확인
            if not os.path.exists(config_path):
                return {
                    "status": "error", 
                    "message": f"Config 파일이 존재하지 않습니다: {config_path}"
                }
            
            print(f"[INFO] Config 파일로 예측 실행 중: {config_path}")
            # tfci.predict 함수 사용
            result = tfci.predict(config_path)
            print(f"[INFO] 예측 실행 완료: {result}")
            
            return {
                "status": "success", 
                "message": f"예측 완료: {config_path}",
                "result": result
            }
        except Exception as e:
            print(f"[ERROR] 예측 중 오류 발생: {e}")
            traceback.print_exc()
            return {
                "status": "error", 
                "message": str(e)
            }

def handle_request(server: TFCIMCPServer, request: Dict[str, Any]) -> Dict[str, Any]:
    """JSON-RPC 요청 처리"""
    try:
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        if method == "predict":
            config_path = params.get("config_path")
            if not config_path:
                return {"error": {"code": -32602, "message": "config_path is required"}}
            result = server.predict(config_path)
        else:
            return {"error": {"code": -32601, "message": f"Method {method} not found"}}

        return {"jsonrpc": "2.0", "result": result, "id": request_id}

    except Exception as e:
        return {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": request.get("id")}

def main():
    print("TFCI MCP Time Series Prediction Server 시작")
    
    if not TFCI_AVAILABLE:
        print("⚠️  경고: tfci 패키지가 설치되지 않았습니다.")
        print("   설치 방법: pip install tfci")
        print("   예측 기능을 사용하려면 tfci 패키지가 필요합니다.")
    else:
        print("✅ tfci 패키지 사용 가능")
    
    print("JSON-RPC 요청을 stdin으로 받습니다.")
    print("사용 가능한 메서드:")
    print("  - predict(config_path)")
    print("종료하려면 Ctrl+C를 누르세요.")
    print("-" * 50)

    server = TFCIMCPServer()

    try:
        while True:
            line = input()
            if not line:
                continue

            try:
                request = json.loads(line)
                response = handle_request(server, request)
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
            except json.JSONDecodeError:
                print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}))
                sys.stdout.flush()

    except KeyboardInterrupt:
        print("\n[INFO] TFCI MCP 서버가 종료되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] 서버 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 