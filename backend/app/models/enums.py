import enum


class UserRole(str, enum.Enum):
    STUDENT = "student"
    COUNSELOR = "counselor"
    ADMIN = "admin"


class MessageRole(str, enum.Enum):
    STUDENT = "student"
    ASSISTANT = "assistant"
    COUNSELOR = "counselor"


class AgentKind(str, enum.Enum):
    CONVERSATION = "conversation"
    MOOD_ANALYSIS = "mood_analysis"
    MEMORY_PATTERN = "memory_pattern"
    THERAPEUTIC = "therapeutic"
    CRISIS_DETECTION = "crisis_detection"


class RiskTier(str, enum.Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SeverityBand(str, enum.Enum):
    MINIMAL = "minimal"
    MILD = "mild"
    MODERATE = "moderate"
    MODERATELY_SEVERE = "moderately_severe"
    SEVERE = "severe"


class WellnessTrend(str, enum.Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    UNKNOWN = "unknown"


class CaseStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"