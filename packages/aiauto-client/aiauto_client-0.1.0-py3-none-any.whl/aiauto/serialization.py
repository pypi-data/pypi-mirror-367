"""
Source Code Serialization Module

이 모듈은 Python 버전 간 호환성을 위해 CloudPickle 대신 
inspect.getsource를 사용한 소스코드 직렬화 방식을 제공합니다.
"""

import inspect
import types
from typing import Callable, Dict, Any, Tuple


class SourceCodeSerializer:
    """Objective 함수를 소스코드로 직렬화하는 클래스"""
    
    @staticmethod
    def serialize_objective(objective_func: Callable) -> Dict[str, Any]:
        """
        Objective 함수를 소스코드로 직렬화
        
        Args:
            objective_func: 직렬화할 objective 함수
            
        Returns:
            직렬화된 데이터 딕셔너리
            - source_code: 함수의 소스코드 문자열
            - func_name: 함수 이름
            - dependencies: 필요한 import 구문들
        """
        try:
            # 함수 소스코드 추출
            source_code = inspect.getsource(objective_func)
            func_name = objective_func.__name__
            
            # 함수가 정의된 모듈의 정보 추출
            module = inspect.getmodule(objective_func)
            dependencies = []
            
            if module and hasattr(module, '__file__'):
                # 모듈에서 import 구문들 추출 (간단한 방식)
                with open(module.__file__, 'r') as f:
                    module_source = f.read()
                
                # import 구문 추출 (개선된 파싱 필요시 ast 모듈 사용)
                lines = module_source.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        # 기본적인 import 구문만 추출
                        if not any(skip in line for skip in ['client', '__', 'relative']):
                            dependencies.append(line)
            
            return {
                'source_code': source_code,
                'func_name': func_name,
                'dependencies': dependencies,
                'serialization_method': 'source_code'
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to serialize objective function: {e}")
    
    @staticmethod
    def deserialize_objective(serialized_data: Dict[str, Any]) -> Callable:
        """
        직렬화된 데이터로부터 objective 함수를 복원
        
        Args:
            serialized_data: serialize_objective에서 생성된 데이터
            
        Returns:
            복원된 objective 함수
        """
        try:
            source_code = serialized_data['source_code']
            func_name = serialized_data['func_name']
            dependencies = serialized_data.get('dependencies', [])
            
            # 실행 네임스페이스 생성
            exec_namespace = {'__builtins__': __builtins__}
            
            # 의존성 import 실행
            for dep in dependencies:
                try:
                    exec(dep, exec_namespace)
                except Exception as import_error:
                    # import 실패는 경고만 하고 계속 진행
                    print(f"Warning: Failed to import dependency '{dep}': {import_error}")
            
            # 소스코드 실행
            exec(source_code, exec_namespace)
            
            # 함수 객체 추출
            if func_name not in exec_namespace:
                raise NameError(f"Function '{func_name}' not found in executed namespace")
            
            objective_func = exec_namespace[func_name]
            
            if not callable(objective_func):
                raise TypeError(f"'{func_name}' is not callable")
            
            return objective_func
            
        except Exception as e:
            raise RuntimeError(f"Failed to deserialize objective function: {e}")


def create_study_with_source_serialization(
    objective: Callable,
    study_config: Dict[str, Any],
    **optuna_kwargs
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    소스코드 직렬화를 사용하여 study 생성 준비
    
    Args:
        objective: HPO에 사용할 objective 함수
        study_config: study 설정 (name, direction, sampler, pruner 등)
        **optuna_kwargs: optuna.create_study에 전달할 추가 인자들
        
    Returns:
        Tuple[serialized_objective, study_config]
        - serialized_objective: 직렬화된 objective 함수 데이터
        - study_config: study 설정 데이터
    """
    # Objective 함수 직렬화
    serialized_objective = SourceCodeSerializer.serialize_objective(objective)
    
    # Study 설정 정리
    processed_config = {
        'study_name': study_config.get('study_name', 'unnamed_study'),
        'direction': study_config.get('direction', 'minimize'),
        'sampler': study_config.get('sampler', 'TPESampler'),
        'pruner': study_config.get('pruner', None),
        'optuna_kwargs': optuna_kwargs
    }
    
    return serialized_objective, processed_config