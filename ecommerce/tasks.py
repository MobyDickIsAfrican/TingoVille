from celery import shared_task
from .models import Inventory

@shared_task
def OrderMessage(cart_id):
    Cart = ShoppingCartOrder.objects.get(id = cart_id)
    user_id = Cart.Owner.id
    for item in Cart.CartOrder.all():
        obj = item.product
        shop = obj.shop
        inventory = get_object_or_404(Inventory, shop = shop)
        return inventory.Messages(user_id, obj)
