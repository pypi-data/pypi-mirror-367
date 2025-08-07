from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OdinMessage(_message.Message):
    __slots__ = ("trace_id", "session_id", "sender_id", "receiver_id", "role", "raw_output", "healed_output", "timestamp", "semantic_drift_score", "healing_metadata", "context", "metrics")
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SENDER_ID_FIELD_NUMBER: _ClassVar[int]
    RECEIVER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    RAW_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    HEALED_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SEMANTIC_DRIFT_SCORE_FIELD_NUMBER: _ClassVar[int]
    HEALING_METADATA_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    trace_id: str
    session_id: str
    sender_id: str
    receiver_id: str
    role: str
    raw_output: str
    healed_output: str
    timestamp: int
    semantic_drift_score: float
    healing_metadata: HealingMetadata
    context: ConversationContext
    metrics: PerformanceMetrics
    def __init__(self, trace_id: _Optional[str] = ..., session_id: _Optional[str] = ..., sender_id: _Optional[str] = ..., receiver_id: _Optional[str] = ..., role: _Optional[str] = ..., raw_output: _Optional[str] = ..., healed_output: _Optional[str] = ..., timestamp: _Optional[int] = ..., semantic_drift_score: _Optional[float] = ..., healing_metadata: _Optional[_Union[HealingMetadata, _Mapping]] = ..., context: _Optional[_Union[ConversationContext, _Mapping]] = ..., metrics: _Optional[_Union[PerformanceMetrics, _Mapping]] = ...) -> None: ...

class HealingMetadata(_message.Message):
    __slots__ = ("method", "confidence", "source_document_id", "notes", "applied_rules", "iteration_count")
    METHOD_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    APPLIED_RULES_FIELD_NUMBER: _ClassVar[int]
    ITERATION_COUNT_FIELD_NUMBER: _ClassVar[int]
    method: str
    confidence: float
    source_document_id: str
    notes: str
    applied_rules: _containers.RepeatedScalarFieldContainer[str]
    iteration_count: int
    def __init__(self, method: _Optional[str] = ..., confidence: _Optional[float] = ..., source_document_id: _Optional[str] = ..., notes: _Optional[str] = ..., applied_rules: _Optional[_Iterable[str]] = ..., iteration_count: _Optional[int] = ...) -> None: ...

class ConversationContext(_message.Message):
    __slots__ = ("conversation_id", "turn_number", "conversation_type", "topic", "key_themes", "emotional_state")
    CONVERSATION_ID_FIELD_NUMBER: _ClassVar[int]
    TURN_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CONVERSATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    KEY_THEMES_FIELD_NUMBER: _ClassVar[int]
    EMOTIONAL_STATE_FIELD_NUMBER: _ClassVar[int]
    conversation_id: str
    turn_number: int
    conversation_type: str
    topic: str
    key_themes: _containers.RepeatedScalarFieldContainer[str]
    emotional_state: str
    def __init__(self, conversation_id: _Optional[str] = ..., turn_number: _Optional[int] = ..., conversation_type: _Optional[str] = ..., topic: _Optional[str] = ..., key_themes: _Optional[_Iterable[str]] = ..., emotional_state: _Optional[str] = ...) -> None: ...

class PerformanceMetrics(_message.Message):
    __slots__ = ("response_time_ms", "coherence_score", "relevance_score", "token_count", "complexity_score", "model_version")
    RESPONSE_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    COHERENCE_SCORE_FIELD_NUMBER: _ClassVar[int]
    RELEVANCE_SCORE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_COUNT_FIELD_NUMBER: _ClassVar[int]
    COMPLEXITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    MODEL_VERSION_FIELD_NUMBER: _ClassVar[int]
    response_time_ms: int
    coherence_score: float
    relevance_score: float
    token_count: int
    complexity_score: float
    model_version: str
    def __init__(self, response_time_ms: _Optional[int] = ..., coherence_score: _Optional[float] = ..., relevance_score: _Optional[float] = ..., token_count: _Optional[int] = ..., complexity_score: _Optional[float] = ..., model_version: _Optional[str] = ...) -> None: ...

class OdinMessageBatch(_message.Message):
    __slots__ = ("messages", "batch_id", "batch_timestamp", "batch_metadata")
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    BATCH_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    BATCH_METADATA_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[OdinMessage]
    batch_id: str
    batch_timestamp: int
    batch_metadata: str
    def __init__(self, messages: _Optional[_Iterable[_Union[OdinMessage, _Mapping]]] = ..., batch_id: _Optional[str] = ..., batch_timestamp: _Optional[int] = ..., batch_metadata: _Optional[str] = ...) -> None: ...

class OdinReflection(_message.Message):
    __slots__ = ("original", "healed", "mediator_id", "action_taken", "explanation", "confidence_score", "reflection_timestamp", "iteration_count", "correction_tags")
    ORIGINAL_FIELD_NUMBER: _ClassVar[int]
    HEALED_FIELD_NUMBER: _ClassVar[int]
    MEDIATOR_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_TAKEN_FIELD_NUMBER: _ClassVar[int]
    EXPLANATION_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_SCORE_FIELD_NUMBER: _ClassVar[int]
    REFLECTION_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ITERATION_COUNT_FIELD_NUMBER: _ClassVar[int]
    CORRECTION_TAGS_FIELD_NUMBER: _ClassVar[int]
    original: OdinMessage
    healed: OdinMessage
    mediator_id: str
    action_taken: str
    explanation: str
    confidence_score: float
    reflection_timestamp: int
    iteration_count: int
    correction_tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, original: _Optional[_Union[OdinMessage, _Mapping]] = ..., healed: _Optional[_Union[OdinMessage, _Mapping]] = ..., mediator_id: _Optional[str] = ..., action_taken: _Optional[str] = ..., explanation: _Optional[str] = ..., confidence_score: _Optional[float] = ..., reflection_timestamp: _Optional[int] = ..., iteration_count: _Optional[int] = ..., correction_tags: _Optional[_Iterable[str]] = ...) -> None: ...
