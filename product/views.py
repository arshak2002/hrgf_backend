# ecommerce_api/viewsets.py
from rest_framework import status
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
import stripe
from django.core.files import File

from .utils import generate_order_receipt_pdf
from product.tasks import send_order_confirmation_email
from .models import Payment, Product, Category, CartItem, Order
from .serializers import (
    ProductSerializer, CategorySerializer,
    CartItemSerializer, OrderSerializer
)
from .permissions import IsOwnerOrAdmin
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile

stripe.api_key = settings.STRIPE_SECRET_KEY

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'], url_path='place-order')
    def place_order(self, request):
        user = request.user
        payment_method_id = request.data.get("payment_method_id")
        items_data = request.data.get("items")  # list of {product, quantity}

        if not payment_method_id:
            return Response({"detail": "payment_method_id is required."}, status=400)

        if not items_data or not isinstance(items_data, list):
            return Response({"detail": "items must be a non-empty list of product and quantity."}, status=400)

        products = []
        total_amount = 0

        for item in items_data:
            product_id = item.get("product")
            quantity = int(item.get("quantity", 0))

            if not product_id or quantity <= 0:
                return Response({"detail": f"Invalid product or quantity in item: {item}"}, status=400)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"detail": f"Product with ID {product_id} not found."}, status=404)

            products.append((product, quantity))
            total_amount += product.price * quantity

        # Stripe expects amount in paise
        amount_in_paise = int(total_amount * 100)

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_in_paise,
                currency="inr",
                payment_method=payment_method_id,
                confirm=True,
                automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            )
            if intent.status != "succeeded":
                return Response({"detail": "Payment failed or requires additional action."}, status=400)
        except stripe.error.CardError as e:
            return Response({"detail": str(e)}, status=400)

        Payment.objects.create(
            user=user,
            amount=total_amount,
            stripe_payment_intent_id=intent.id,
            status=intent.status,
        )

        order = Order.objects.create(
            user=user,
            payment_intent_id=intent.id,
            payment_status=intent.status,
            total_amount=total_amount
        )

        pdf_path = generate_order_receipt_pdf(order)
        with open(pdf_path, 'rb') as f:
            order.receipt.save(f"order_{order.id}.pdf", File(f), save=True)

        for product, quantity in products:
            order.items.create(product=product, quantity=quantity)

        send_order_confirmation_email.delay(user.email, order.id)

        return Response(OrderSerializer(order).data, status=201)

    @action(detail=True, methods=["get"], url_path="download-receipt")
    def download_receipt(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=404)

        html_string = render_to_string("order_receipt.html", {"order": order,"items":order.items.all})
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="order_{order.id}_receipt.pdf"'
        return response
