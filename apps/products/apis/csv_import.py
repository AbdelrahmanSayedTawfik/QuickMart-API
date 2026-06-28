import csv          
import io           
from django.http import HttpResponse  
from drf_spectacular.utils import (
    OpenApiParameter,   
    OpenApiResponse,    
    extend_schema,      
)
from rest_framework import generics, status  
from rest_framework.parsers import FormParser, MultiPartParser  
from rest_framework.permissions import IsAuthenticated  
from rest_framework.response import Response  
from rest_framework.views import APIView  
from apps.products.permissions import IsAdminOrSeller  
from apps.products.serializers.csv_import import (
    CSVImportResponseSerializer,  
    CSVTemplateSerializer,        
    CSVUploadSerializer,          
)
from apps.products.services.csv_import import CSVImportService  

class ProductCSVCreateView(generics.CreateAPIView):

    serializer_class = CSVUploadSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSeller]
    parser_classes = [MultiPartParser, FormParser]
    @extend_schema(
        tags=['CSV Import — Products'],
        summary='Create new products from a CSV file',
        description=(
            'Upload a CSV file to bulk-create products. '
            'Rows where the SKU already exists are silently skipped. '
            'The authenticated user is automatically set as the seller '
            'for every product created by this request.\n\n'
            'Required columns : name, sku, price\n'
            'Optional columns : description, original_price, stock_quantity, '
            'category_name, status, is_active, is_featured\n\n'
            'Download a ready-to-use template from GET /import/csv/template/?model=products'
        ),
        request={'multipart/form-data': CSVUploadSerializer},
        responses={
            200: OpenApiResponse(
                response=CSVImportResponseSerializer,
                description='Import completed. Check the "errors" field for row-level failures.',
            ),
            400: OpenApiResponse(description='File validation failed or required columns are missing.'),
            401: OpenApiResponse(description='Authentication required.'),
            403: OpenApiResponse(description='Seller or Admin role required.'),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        self.import_result = CSVImportService.import_from_file(
            model_name='products',           
            uploaded_file=serializer.validated_data['file'],  
            user=self.request.user,          
            skip_invalid=serializer.validated_data.get('skip_invalid', False),
            update_existing=False,           
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        http_status = (
            status.HTTP_200_OK
            if self.import_result.success
            else status.HTTP_400_BAD_REQUEST
        )
        return Response(
            CSVImportResponseSerializer(self.import_result.to_dict()).data,
            status=http_status,
        )

class ProductCSVUpdateView(generics.UpdateAPIView):
    serializer_class = CSVUploadSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSeller]
    parser_classes = [MultiPartParser, FormParser]
    queryset = []
    lookup_field = None

    @extend_schema(
        tags=['CSV Import — Products'],
        summary='Update existing products from a CSV file',
        description=(
            'Upload a CSV file to bulk-update products matched by SKU. '
            'Rows where the SKU does not exist in the database are skipped. '
            'Sellers can only update their own products. '
            'Admins can update any product regardless of seller.\n\n'
            'Required columns : name, sku, price\n'
            'Optional columns : description, original_price, stock_quantity, '
            'category_name, status, is_active, is_featured'
        ),
        request={'multipart/form-data': CSVUploadSerializer},
        responses={
            200: OpenApiResponse(
                response=CSVImportResponseSerializer,
                description='Update completed.',
            ),
            400: OpenApiResponse(description='Validation failed or missing columns.'),
            401: OpenApiResponse(description='Authentication required.'),
            403: OpenApiResponse(description='Seller or Admin role required.'),
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def perform_update(self, serializer):
        self.import_result = CSVImportService.import_from_file(
            model_name='products',
            uploaded_file=serializer.validated_data['file'],
            user=self.request.user,
            skip_invalid=serializer.validated_data.get('skip_invalid', False),
            update_existing=True,  
        )

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        http_status = (
            status.HTTP_200_OK
            if self.import_result.success
            else status.HTTP_400_BAD_REQUEST
        )

        return Response(
            CSVImportResponseSerializer(self.import_result.to_dict()).data,
            status=http_status,
        )

class CategoryCSVCreateView(generics.CreateAPIView):
    serializer_class = CSVUploadSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSeller]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=['CSV Import — Categories'],
        summary='Create new categories from a CSV file',
        description=(
            'Upload a CSV file to bulk-create product categories. '
            'Admin access required. '
            'Rows where the category name already exists are skipped.\n\n'
            'Required columns : name\n'
            'Optional columns : slug, description, parent_name, is_active\n\n'
            'Parent categories must appear before their child rows in the CSV file. '
            'Download a template from GET /import/csv/template/?model=categories'
        ),
        request={'multipart/form-data': CSVUploadSerializer},
        responses={
            200: OpenApiResponse(
                response=CSVImportResponseSerializer,
                description='Import completed.',
            ),
            400: OpenApiResponse(description='Validation failed or missing columns.'),
            401: OpenApiResponse(description='Authentication required.'),
            403: OpenApiResponse(description='Admin access required.'),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        self.import_result = CSVImportService.import_from_file(
            model_name='categories',
            uploaded_file=serializer.validated_data['file'],
            user=self.request.user,
            skip_invalid=serializer.validated_data.get('skip_invalid', False),
            update_existing=False,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        http_status = (
            status.HTTP_200_OK
            if self.import_result.success
            else status.HTTP_400_BAD_REQUEST
        )

        return Response(
            CSVImportResponseSerializer(self.import_result.to_dict()).data,
            status=http_status,
        )

class CategoryCSVUpdateView(generics.UpdateAPIView):
    serializer_class = CSVUploadSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSeller]
    parser_classes = [MultiPartParser, FormParser]
    queryset = []  
    lookup_field = None  

    @extend_schema(
        tags=['CSV Import — Categories'],
        summary='Update existing categories from a CSV file',
        description=(
            'Upload a CSV file to bulk-update categories matched by name. '
            'Admin access required. '
            'Rows where the category name does not exist are skipped.'
        ),
        request={'multipart/form-data': CSVUploadSerializer},
        responses={
            200: OpenApiResponse(
                response=CSVImportResponseSerializer,
                description='Update completed.',
            ),
            400: OpenApiResponse(description='Validation failed or missing columns.'),
            401: OpenApiResponse(description='Authentication required.'),
            403: OpenApiResponse(description='Admin access required.'),
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def perform_update(self, serializer):
        """Identical to ProductCSVUpdateView.perform_update() except model_name"""
        self.import_result = CSVImportService.import_from_file(
            model_name='categories',
            uploaded_file=serializer.validated_data['file'],
            user=self.request.user,
            skip_invalid=serializer.validated_data.get('skip_invalid', False),
            update_existing=True,
        )

    def update(self, request, *args, **kwargs):
        """Identical to ProductCSVUpdateView.update()"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        http_status = (
            status.HTTP_200_OK
            if self.import_result.success
            else status.HTTP_400_BAD_REQUEST
        )

        return Response(
            CSVImportResponseSerializer(self.import_result.to_dict()).data,
            status=http_status,
        )


class CSVTemplateView(APIView):
    permission_classes = []#IsAuthenticated, IsAdminOrSeller]

    @extend_schema(
        tags=['CSV Import — Template'],
        summary='Download a CSV column template',
        description=(
            'Returns a ready-to-fill CSV file for the requested model. '
            'Row 1 contains the column names. '
            'Row 2 marks each column as REQUIRED or optional. '
            'Row 3 is a blank example row.\n\n'
            'Omit the model parameter to receive a JSON overview of all available models.\n'
            'Pass format=json to receive column information as JSON instead of a file download.'
        ),
        parameters=[
            OpenApiParameter(
                name='model',
                location=OpenApiParameter.QUERY,
                description="The model to generate a template for: 'products' or 'categories'.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='format',
                location=OpenApiParameter.QUERY,
                description="Pass 'json' to receive column info as JSON instead of a CSV download.",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: OpenApiResponse(description='CSV file download or JSON column information.'),
            400: OpenApiResponse(description='Unknown model name.'),
            401: OpenApiResponse(description='Authentication required.'),
        },
    )
    def get(self, request):
        # Extract query parameters from URL
        # URL: /import/csv/template/?model=products&format=json
        # request.query_params = {'model': 'products', 'format': 'json'}
        model_name = request.query_params.get('model', '').strip().lower()
        fmt = request.query_params.get('format', '').strip().lower()
        
        if not model_name:
            overview = []
            # Loop through all registered importers
            for name in CSVImportService.get_available_models():
                columns = CSVImportService.get_template_columns(name)
                overview.append({'model': name, **columns})
            return Response(overview, status=status.HTTP_200_OK)

        columns = CSVImportService.get_template_columns(model_name)
        if columns is None:
            available = ', '.join(CSVImportService.get_available_models())
            return Response(
                {'error': f"Unknown model '{model_name}'. Available: {available}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if fmt == 'json':
            return Response(
                CSVTemplateSerializer({
                    'model': model_name,
                    'required': columns['required'],
                    'optional': columns['optional'],
                }).data,
                status=status.HTTP_200_OK,
            )

        return self._build_csv_response(model_name, columns)

    def _build_csv_response(self, model_name: str, columns: dict) -> HttpResponse:
        required_cols = columns['required']   
        optional_cols = columns['optional']   
        all_cols = required_cols + optional_cols  

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(all_cols)

        writer.writerow([
            'REQUIRED' if col in required_cols else 'optional'
            for col in all_cols
        ])

        writer.writerow([''] * len(all_cols))

        response = HttpResponse(output.getvalue(), content_type='text/csv')

        response['Content-Disposition'] = (
            f'attachment; filename="{model_name}_template.csv"'
        )
        
        return response