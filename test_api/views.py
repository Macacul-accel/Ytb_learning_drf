from django.db.models import Max
from django.shortcuts import get_object_or_404
from test_api.serializers import ProductSerializer, OrderSerializer, ProductInfoSerializer
from test_api.models import Product, Order
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

# Note that this classes only works with GET request, so read only
class ProductListAPIView(generics.ListAPIView):
    """
    the same as product_list but simplier
    """
    queryset = Product.objects.exclude(stock__gt=0)
    serializer_class = ProductSerializer


#@api_view(['GET'])
#def product_list(request):
#    products = Product.objects.all()
#    serializer = ProductSerializer(products, many=True)
#    return Response(serializer.data)
    
class ProdctDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_id'

#@api_view(['GET'])
#def product_detail(request, pk):
#    product = get_object_or_404(Product, pk=pk)
#    serializer = ProductSerializer(product)
#    return Response(serializer.data)

class OrderListAPIView(generics.ListAPIView):
    
    queryset = Order.objects.prefetch_related('items__product').all()
    serializer_class = OrderSerializer
    
class UserOrderListAPIView(generics.ListAPIView):
    """
    Overrriding get_queryset to link each order to its users
    """
    queryset = Order.objects.prefetch_related('items__product').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        return qs.filter(user=user)
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


@api_view(['GET'])
def product_info(request):
    products = Product.objects.all()
    serializer = ProductInfoSerializer({
        'products': products,
        'count': len(products),
        'max_price': products.aggregate(max_price=Max('price'))['max_price'],
    })
    return Response(serializer.data)