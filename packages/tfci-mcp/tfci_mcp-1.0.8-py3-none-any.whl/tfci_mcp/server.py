#!/usr/bin/env python3
"""
TFCI MCP (Model Context Protocol) Server for Time Series Prediction
"""

import json
import sys
import traceback
import os
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import load_config
from core.predictor import Predictor

class TFCIMCPServer:
    def __init__(self):
        self.predictor = None
        self.config = None

    def predict(self, config_path: str) -> Dict[str, Any]:
        """YAML 설정 파일로 예측 실행 및 DB 저장"""
        try:
            print(f"[INFO] TFCI MCP 예측 시작: {config_path}")
            
            # config 파일 존재 확인
            if not os.path.exists(config_path):
                return {
                    "status": "error", 
                    "message": f"Config 파일이 존재하지 않습니다: {config_path}"
                }
            
            print(f"[INFO] Config 파일 로드 중: {config_path}")
            # config 파일 로드
            config = load_config(config_path)
            print(f"[INFO] Config 로드 완료: {config}")
            
            print(f"[INFO] Predictor 초기화 중...")
            # 예측 실행
            predictor = Predictor(config)
            print(f"[INFO] Predictor 초기화 완료, 예측 실행 중...")
            predictor.run()
            print(f"[INFO] 예측 실행 완료")
            
            return {
                "status": "success", 
                "message": f"예측 완료: {config_path}"
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