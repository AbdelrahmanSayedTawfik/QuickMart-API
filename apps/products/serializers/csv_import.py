from rest_framework import serializers
from apps.products.services.csv_import import CSVImportService


class CSVUploadSerializer(serializers.Serializer):

    file = serializers.FileField(
        help_text='A UTF-8 encoded CSV file. Maximum size: 10 MB.',
    )
    skip_invalid = serializers.BooleanField(
        required=False,
        default=False,
        help_text=(
            'If true, invalid rows are skipped and the import continues. '
            'If false (default), the import stops at the first error.'
        ),
    )

    def validate_file(self, value):
        if not value.name.lower().endswith('.csv'):
            raise serializers.ValidationError(
                'File must have a .csv extension.'
            )
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                'File is too large. Maximum allowed size is 10 MB.'
            )
        return value


class CSVImportResponseSerializer(serializers.Serializer):

    success       = serializers.BooleanField()
    message       = serializers.CharField()
    created       = serializers.IntegerField()
    updated       = serializers.IntegerField()
    skipped       = serializers.IntegerField()
    errors        = serializers.IntegerField()
    total_rows    = serializers.IntegerField()
    error_details = serializers.ListField(child=serializers.CharField())


class CSVTemplateSerializer(serializers.Serializer):
    model    = serializers.CharField()
    required = serializers.ListField(child=serializers.CharField())
    optional = serializers.ListField(child=serializers.CharField())