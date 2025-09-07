from rest_framework import serializers

class TranscriptionRequestSerializer(serializers.Serializer):
    # Flags that mirror the previous endpoint's query/form options.
    align = serializers.BooleanField(default=False)
    perform_diarization = serializers.BooleanField(default=False)

class SummaryRequestSerializer(serializers.Serializer):
    # We accept an arbitrary transcript JSON object. The service will normalize it.
    transcript = serializers.JSONField()

class SummaryResponseSerializer(serializers.Serializer):
    note = serializers.JSONField()
