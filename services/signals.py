import os
from django.db.models.signals import pre_save
from django.dispatch import receiver

from services.models import Service, Seller, Category, Product
from users.models import User


@receiver(pre_save, sender=Service)
@receiver(pre_save, sender=Seller)
@receiver(pre_save, sender=Category)
@receiver(pre_save, sender=Product)
def delete_old_image_file(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_image = sender.objects.get(pk=instance.pk).image
        except sender.DoesNotExist:
            return
        else:
            new_image = instance.image
            if old_image and old_image.url != new_image.url:
                img_path = old_image.path
                old_image.delete(save=False)
                
                dirname = os.path.dirname(img_path)
                filename = os.path.basename(img_path)
                thumb_path = os.path.join(dirname, "thumbnail", filename)
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)


# @receiver(pre_save, sender=User)
# def delete_old_avatar_file(sender, instance, **kwargs):
#     if instance.pk:
#         try:
#             old_avatar = User.objects.get(pk=instance.pk).avatar
#         except sender.DoesNotExist:
#             return
#         else:
#             new_avatar = instance.avatar
#             if old_avatar and old_avatar.url != new_avatar.url:
#                 old_avatar.delete(save=False)
