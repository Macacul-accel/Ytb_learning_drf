from django.db.models import Max
from django.shortcuts import get_object_or_404
from test_api.serializers import ProductSerializer, OrderSerializer, ProductInfoSerializer
from test_api.models import Product, Order
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework import viewsets
from .filters import InStockFilterBackend, ProductFilter, OrderFilter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.decorators import action

# Note that this classes only works with GET request, so read only
class ProductListCreateAPIView(generics.ListCreateAPIView):
    """
    the same as product_list but simplier
    """
    queryset = Product.objects.all().order_by('pk')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend,
    ]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'stock']
    pagination_class = LimitOffsetPagination
    #pagination_class = PageNumberPagination
    #pagination_class.page_size = 2
    #pagination_class.page_query_param = 'pagenum'
    #pagination_class.page_size_query_param = 'size'
    #pagination_class.max_page_size = 6

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

#@api_view(['GET'])
#def product_list(request):
#    products = Product.objects.all()
#    serializer = ProductSerializer(products, many=True)
#    return Response(serializer.data)

# we modified the class ProductList that can create and display the product 
#class ProductCreateAPIView(generics.CreateAPIView):
#    model = Product
#    serializer_class = ProductSerializer
#
#    def create(self, request, *args, **kwargs):
#        print(request.data)
#        return super().create(request, *args, **kwargs)
    
class ProdctDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_id'

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

    @action(
        detail=False,
        methods=['get'],
        url_path='user-orders',
        permission_classes=[IsAuthenticated]
    )
    def user_orders(self, request):
        orders = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

#@api_view(['GET'])
#def product_detail(request, pk):
#    product = get_object_or_404(Product, pk=pk)
#    serializer = ProductSerializer(product)
#    return Response(serializer.data)

# class OrderListAPIView(generics.ListAPIView):
    
#     queryset = Order.objects.prefetch_related('items__product').all()
#     serializer_class = OrderSerializer
    
# class UserOrderListAPIView(generics.ListAPIView):
#     """
#     Overrriding get_queryset to link each order to its users
#     """
#     queryset = Order.objects.prefetch_related('items__product').all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         qs = super().get_queryset()
#         return qs.filter(user=user)
    """
    Or
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filer(user=self.request.user)
    """

#@api_view(['GET'])
#def order_list(request):
#    order = Order.objects.prefetch_related(
#        'items__product'
#    ).all()
#    serializer = OrderSerializer(order, many=True)
#    return Response(serializer.data)

class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price'],
        })
        return Response(serializer.data)

#@api_view(['GET'])
#def product_info(request):
#    products = Product.objects.all()
#    serializer = ProductInfoSerializer({
#        'products': products,
#        'count': len(products),
#        'max_price': products.aggregate(max_price=Max('price'))['max_price'],
#    })
#    return Response(serializer.data)