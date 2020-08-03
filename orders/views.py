import json
from datetime       import datetime
from decimal        import Decimal

from django.http    import JsonResponse
from django.views   import View

from products.models    import (
    Product,
    Option,
    ProductOption,
    Size,
    SkinType
)
from orders.models      import (
    Order,
    OrderStatus,
    OrderItem,
)
from utils              import (
    auth_decorator,
    round_up
)

class OrderColorItemView(View):

    @auth_decorator
    def post(self,request):
        data    = json.loads(request.body)

        try:
            user_id    = request.user.id
            item_id    = ProductOption.objects.get(
                product_id = data['product_id'],
                option_id  = Option.objects.get(color_id = data['color_id']).id
            ).id

            if not Order.objects.filter(
                user_id         = user_id,
                order_status_id = OrderStatus.objects.get(name="장바구니").id
            ).exists():
                Order(
                    shipping_price  = 0,
                    list_price      = 0,
                    discount_price  = 0,
                    total_price     = 0,
                    order_status_id = 1,
                    user_id         = user_id
                ).save()

            user_order   = Order.objects.get(
                user_id         = user_id,
                order_status_id = OrderStatus.objects.get(name="장바구니").id
            )

            if OrderItem.objects.filter(
                products_option_id = item_id,
                order_id           = user_order.id
            ).exists():
                color_order_item = OrderItem.objects.get(
                    products_option_id = item_id,
                    order_id           = user_order.id
                )
                color_order_item.quantity += 1
                color_order_item.save()
                user_order.shipping_price   =  0
                user_order.list_price       += ProductOption.objects.get(id=item_id).price
                user_order.save()

            else:
                OrderItem (
                    order_id            = user_order.id,
                    products_option_id  = item_id,
                    quantity            = 1,
                    discount_price      = 0
                ).save()

                user_order.shipping_price   =  0
                user_order.list_price       += ProductOption.objects.get(id=item_id).price
                user_order.save()

            return JsonResponse({'message':'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)

        except Order.DoesNotExist:
            return JsonResponse({'message':'INVALID_ORDER'},status=400)

class OrderBulkItem(View):

    @auth_decorator
    def post(self,request):

        try:
            data           = json.loads(request.body)
            bulk_item_list = data['Info']
            user_id        = request.user.id

            for item in bulk_item_list:
                if not Order.objects.filter(
                    user_id         = user_id,
                    order_status_id = OrderStatus.objects.get(name="장바구니").id
                ).exists():
                    Order(
                        shipping_price  = 2500,
                        list_price      = 0,
                        discount_price  = 0,
                        total_price     = 0,
                        order_status_id = 1,
                        user_id         = user_id
                    ).save()

                user_order   = Order.objects.get(
                    user_id         = user_id,
                    order_status_id = OrderStatus.objects.get(name="장바구니").id
                )

                size_id = Size.objects.get(name=item['size_name']).id if Size.objects.filter(name=item['size_name']).exists() else None
                skin_type_id = SkinType.objects.get(name=item['skin_type_name']).id if SkinType.objects.filter(name=item['skin_type_name']).exists() else None

                option_id       = Option.objects.get(size_id=size_id,skin_type_id=skin_type_id,color_id=None).id
                products_option = ProductOption.objects.get(product_id=item['product_id'],option_id=option_id)

                if not OrderItem.objects.filter(
                    products_option_id = products_option.id,
                    order_id            = user_order.id
                ).exists():
                    OrderItem(
                        products_option_id = products_option.id,
                        order_id           = user_order.id,
                        quantity           = 0,
                        discount_price     = 0
                    ).save()

                order_item  = OrderItem.objects.get(
                    products_option_id = products_option.id,
                    order_id           = user_order.id
                )

                order_item.quantity += item['quantity']
                item_price           = float(products_option.price)

                if order_item.quantity == 2:
                    order_item.discount_price = order_item.quantity * item_price * 0.07
                    order_item.discount_price = round_up(order_item.discount_price,-2)
                if order_item.quantity == 3:
                    order_item.discount_price = order_item.quantity * item_price * 0.15
                    order_item.discount_price = round_up(order_item.discount_price,-2)
                if order_item.quantity >= 4:
                    order_item.discount_price = order_item.quantity * item_price * 0.2
                    order_item.discount_price = round_up(order_item.discount_price,-2)

                order_item.save()
                user_order.list_price     += order_item.quantity * products_option.price
                user_order.discount_price += Decimal(order_item.discount_price)

                if user_order.list_price >= 15000:
                    user_order.shipping_price = 0

                user_order.save()

            return JsonResponse({'message':'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)

        except Order.DoesNotExist:
            return JsonResponse({'message':'INVALID_ORDER'},status=400)

class CartList(View):

    @auth_decorator
    def get(self,request):

        try:
            user_id    = request.user.id
            user_order = Order.objects.get(
                user_id         = user_id,
                order_status_id = 1
            )

            items = OrderItem.objects.select_related(
                'products_option__product',
                'products_option__option__size',
                'products_option__option__color',
                'products_option__option__skin_type'
            ).filter(order_id=user_order.id)

            user_order_item_list = [{
                'item_id'        : item.id,
                'product_id'     : item.products_option.product.id,
                'item_name'      : item.products_option.product.name,
                'item_price'     : item.products_option.price,
                'list_price'     : item.quantity * item.products_option.price,
                'color'          : item.products_option.option.color.name if item.products_option.option.color else None,
                'size'           : item.products_option.option.size.name if item.products_option.option.size else None,
                'discount_price' : item.discount_price,
                'description'    : item.products_option.product.description,
                'image_url'      : item.products_option.image_url,
                'quantity'       : item.quantity
            } for item in items]

            return JsonResponse({'message':user_order_item_list}, status=200)

        except Order.DoesNotExist:
            return JsonResponse({'message':'INVALID_ORDER'},status=400)

class ReviewView(View):
    def get(self, request):
        reviews = Review.objects.all()
        review_result = []

        for review in reviews:
            review_id=Review.objects.get(id=review.id).id
            order_item_id=OrderItem.objects.get(id=review_id).id
            user_id=Order.objects.get(id=order_item_id).id
            name = User.objects.get(id=user_id).name
            birthday = User.objects.get(id=user_id).birthday

            name_l = list(name)
            name_l[1] = '*'
            name2 = "".join(name_l)

            birthyear=birthday.year

            ages = math.floor(int(2020-birthyear))
            ages_s = str(ages)
            ages_s = ages_s + '대'

            writed_at = Review.objects.get(id=review_id).writed_at
            writed_at_year = str(writed_at.year)
            writed_at_month = str(writed_at.month)
            writed_at_day = str(writed_at.day)
            writed_at_date = writed_at_year + '.0' + writed_at_month + '.' + writed_at_day

            for review in reviews:
                review_result_dic = {
                    'rate' : Review.objects.get(id=review.id).rate,
                    'review_text' : Review.objects.get(id=review.id).review_text,
                    'writed_at' : writed_at_date,
                    'name' : name2,
                    'ages' : ages_s
                }
                review_result.append(review_result_dic)

            return JsonResponse ({"review_result" : review_result}, status=200)
