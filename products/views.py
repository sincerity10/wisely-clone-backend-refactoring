from django.http        import JsonResponse
from django.views       import View

from products.models    import (
    Product,
    ProductOption,
    SkinType
)

class ProductDetail(View):

    def get(self,request,product_id):
        try:
            product         = Product.objects.prefetch_related('productoption_set').get(id=product_id)
            product_options = product.productoption_set.select_related(
                'option__color',
                'option__size',
                'option__skin_type'
            )

            product_info    = [{
                "name"        : product.name,
                "description" : product.description,
                "price"       : product_options.first().price if not product_options.first().option.size else None,
                "color"       : [{
                    "color_name" : color_option.option.color.name,
                    "color_code" : color_option.option.color.code,
                    "image_url"  : color_option.option.color.image_url
                } for color_option in product_options if product_options.first().option.color],
                "size"        : [{
                    "size_name"     : size_option.option.size.name,
                    "description"   : size_option.option.size.description,
                    "price_by_size" : size_option.price,
                    "skin_type"     : [{
                        "skin_type_name" : size_option.option.skin_type.name
                    } for skin_option in range(0,product_options.values('option__skin_type').distinct().count())
                        if product_options.first().option.skin_type]
                } for size_option in product_options.filter(option__skin_type=product_options.first().option.skin_type) 
                    if product_options.first().option.size]
            }]

            return JsonResponse({'Info':product_info},status=200)

        except Product.DoesNotExist:
            return JsonResponse({'message':'INVALID_PRODUCT'},status=400)
