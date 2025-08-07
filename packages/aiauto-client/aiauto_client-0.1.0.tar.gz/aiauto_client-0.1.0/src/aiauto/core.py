from os import makedirs, environ
import tempfile
from typing import Union, Callable, Dict, Any, Optional
import optuna

from .serialization import create_study_with_source_serialization, SourceCodeSerializer


class AIAutoController:
    # singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    # singleton pattern
    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):
            # singleton pattern
            # ---------------------

            # TODO token 인증
            token = environ.get('AIAUTO_TOKEN')

            # mode별 storage 설정
            mode = environ.get('AIAUTO_MODE', 'single_gpu')
            if mode == "distributed":
                # DDP/FSDP pruning callback 지원을 위해 RDBStorage 사용
                self.storage = optuna.storages.RDBStorage(
                    url="sqlite:///optuna.db",
                    engine_kwargs={"connect_args": {"timeout": 10}}
                )
            else:
                # 기본 GrpcStorageProxy (single GPU 등)
                self.storage = optuna.storages.GrpcStorageProxy(host="localhost", port=13000)

            # artifact storage
            # TODO 나중에 s3 던 다른 mount 된 경로 건 바꿔야 함
            makedirs('./artifacts', exist_ok=True)
            self.artifact_store = optuna.artifacts.FileSystemArtifactStore('./artifacts')
            # model 저장을 위한 임시 디렉토리
            self.tmp_dir = tempfile.mkdtemp(prefix=f'ai_auto_tmp_')

            # ---------------------
            # singleton pattern end
            cls._init = True

    def get_storage(self):
        return self.storage

    def get_artifact_store(self) -> Union[
        optuna.artifacts.FileSystemArtifactStore,
        optuna.artifacts.Boto3ArtifactStore,
        optuna.artifacts.GCSArtifactStore,
    ]:
        return self.artifact_store

    def get_artifact_tmp_dir(self):
        return self.tmp_dir

    def create_study_with_serialization(
        self,
        objective: Callable,
        study_name: str,
        direction: str = 'minimize',
        sampler: Optional[optuna.samplers.BaseSampler] = None,
        pruner: Optional[optuna.pruners.BasePruner] = None,
        **optuna_kwargs
    ) -> 'StudyWrapper':
        """
        소스코드 직렬화를 사용하여 Study 생성
        
        Args:
            objective: HPO에 사용할 objective 함수
            study_name: Study 이름
            direction: 최적화 방향 ('minimize' 또는 'maximize')
            sampler: Optuna sampler (기본값: TPESampler)
            pruner: Optuna pruner
            **optuna_kwargs: optuna.create_study에 전달할 추가 인자
            
        Returns:
            StudyWrapper 객체 (Optuna Study 호환)
        """
        study_config = {
            'study_name': study_name,
            'direction': direction,
            'sampler': sampler.__class__.__name__ if sampler else 'TPESampler',
            'pruner': pruner.__class__.__name__ if pruner else None,
        }
        
        # 소스코드 직렬화
        serialized_objective, processed_config = create_study_with_source_serialization(
            objective, study_config, **optuna_kwargs
        )
        
        # StudyWrapper 생성 (실제 gRPC 전송은 optimize 시점에)
        return StudyWrapper(
            serialized_objective=serialized_objective,
            study_config=processed_config,
            storage=self.storage,
            artifact_store=self.artifact_store
        )


class TrialController:
    def __init__(self, trial: optuna.trial.Trial):
        self.trial = trial
        self.logger = optuna.logging.get_logger("optuna")
        self.logs = []

    def get_trial(self) -> optuna.trial.Trial:
        return self.trial

    def log(self, value: str):
        # optuna dashboard 에 log 를 확인하는 기능이 없어서 user_attribute 에 log를 확인할 수 있게 추가
        self.logs.append(value)
        self.trial.set_user_attr('logs', ' '.join([f"[{i+1:05d}] {log}" for i, log in enumerate(self.logs)]))
        # 실제 log 를 trial_number 랑 같이 확인할 수 있게
        self.logger.info(f'\ntrial_number: {self.trial.number}, {value}')


# 용량 제한으로 상위 N개의 trial artifact 만 유지
class CallbackTopNArtifact:
    def __init__(
        self,
        artifact_store: Union[
            optuna.artifacts.FileSystemArtifactStore,
            optuna.artifacts.Boto3ArtifactStore,
            optuna.artifacts.GCSArtifactStore,
        ],
        artifact_attr_name: str = 'artifact_id',
        n_keep: int = 5,
    ):
        self.artifact_store = artifact_store
        self.check_attr_name = artifact_attr_name
        self.n_keep = n_keep

    def __call__(self, study: optuna.study.Study, trial: optuna.trial.FrozenTrial):
        # COMPLETE 상태이고 artifact를 가진 trial들만 정렬
        finished_with_artifacts = [
            t for t in study.trials
            if t.state == optuna.trial.TrialState.COMPLETE and self.check_attr_name in t.user_attrs
        ]

        # 방향에 따라 정렬 (maximize면 내림차순, minimize면 오름차순)
        reverse_sort = study.direction == optuna.study.StudyDirection.MAXIMIZE
        finished_with_artifacts.sort(key=lambda t: t.value, reverse=reverse_sort)

        # 상위 n_keep개 초과하는 trial들의 artifact 삭제
        for old_trial in finished_with_artifacts[self.n_keep:]:
            artifact_id = old_trial.user_attrs.get(self.check_attr_name)
            if artifact_id:
                try:
                    self.artifact_store.remove(artifact_id)
                    # user_attr에서도 제거
                    study._storage.set_trial_user_attr(old_trial._trial_id, self.check_attr_name, None)
                except Exception as e:
                    print(f"Warning: Failed to remove artifact {artifact_id}: {e}")


class StudyWrapper:
    """
    Optuna Study 호환성을 제공하는 래퍼 클래스
    
    이 클래스는 소스코드 직렬화된 objective 함수를 관리하고
    실제 HPO 실행을 위해 gRPC 백엔드와 통신합니다.
    """
    
    def __init__(
        self,
        serialized_objective: Dict[str, Any],
        study_config: Dict[str, Any],
        storage,
        artifact_store
    ):
        self.serialized_objective = serialized_objective
        self.study_config = study_config
        self.storage = storage
        self.artifact_store = artifact_store
        self._local_study = None  # 로컬 테스트용
        
    def optimize(
        self,
        n_trials: int = 100,
        n_jobs: int = 1,
        callbacks: Optional[list] = None,
        **kwargs
    ):
        """
        HPO 최적화 실행
        
        실제 구현에서는 gRPC를 통해 백엔드로 전송하지만,
        현재는 로컬에서 역직렬화하여 테스트합니다.
        """
        print("🚀 Starting HPO optimization with source code serialization...")
        print(f"📊 Study: {self.study_config['study_name']}")
        print(f"🎯 Direction: {self.study_config['direction']}")
        print(f"🔢 Trials: {n_trials}")
        
        try:
            # 소스코드 역직렬화로 objective 함수 복원
            objective_func = SourceCodeSerializer.deserialize_objective(
                self.serialized_objective
            )
            print("✅ Objective function deserialized successfully")
            
            # 로컬 Study 생성 (실제로는 gRPC 통신)
            self._local_study = optuna.create_study(
                study_name=self.study_config['study_name'],
                direction=self.study_config['direction'],
                storage=self.storage,
                load_if_exists=True
            )
            
            # 최적화 실행
            self._local_study.optimize(
                objective_func,
                n_trials=n_trials,
                n_jobs=n_jobs,
                callbacks=callbacks or [],
                **kwargs
            )
            
            print(f"🎉 Optimization completed! Best value: {self.best_value}")
            
        except Exception as e:
            print(f"❌ Optimization failed: {e}")
            raise
    
    @property
    def best_trial(self):
        """최고 성능 Trial 반환"""
        if self._local_study:
            return self._local_study.best_trial
        return None
    
    @property
    def best_value(self):
        """최고 성능 값 반환"""
        if self._local_study:
            return self._local_study.best_value
        return None
    
    @property
    def best_params(self):
        """최고 성능 하이퍼파라미터 반환"""
        if self._local_study:
            return self._local_study.best_params
        return None
    
    @property
    def trials(self):
        """모든 Trial 목록 반환"""
        if self._local_study:
            return self._local_study.trials
        return []
