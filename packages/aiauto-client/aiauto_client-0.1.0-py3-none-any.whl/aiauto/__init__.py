from .core import AIAutoController, TrialController, CallbackTopNArtifact, StudyWrapper
from .serialization import SourceCodeSerializer, create_study_with_source_serialization

__version__ = "0.1.0"

__all__ = [
    'AIAutoController',
    'TrialController', 
    'CallbackTopNArtifact',
    'StudyWrapper',
    'SourceCodeSerializer',
    'create_study_with_source_serialization',
]

# Optuna 호환성을 위한 간편 함수
def create_study(
    objective=None,
    study_name='aiauto_study', 
    direction='minimize',
    **kwargs
):
    """
    Optuna 호환 create_study 함수
    
    사용법:
        study = aiauto.create_study(
            objective=my_objective,
            study_name='my_study',
            direction='maximize'
        )
        study.optimize(n_trials=100)
    """
    controller = AIAutoController()
    
    if objective is not None:
        return controller.create_study_with_serialization(
            objective=objective,
            study_name=study_name,
            direction=direction,
            **kwargs
        )
    else:
        # objective가 없으면 일반 optuna study 반환 (기존 방식)
        import optuna
        return optuna.create_study(
            study_name=study_name,
            direction=direction,
            storage=controller.get_storage(),
            **kwargs
        )
