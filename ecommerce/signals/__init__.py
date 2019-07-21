import django.dispatch

productdocument_generate_post_save = django.dispatch.Signal(providing_args=["ProductDocument"])
shopdocument_generate_post_save = django.dispatch.Signal(providing_args=["ShopDocument"])
categorydocument_generate_post_save = django.dispatch.Signal(providing_args=["CategoryDocument"])
