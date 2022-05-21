from django.db.models.signals import pre_delete, post_delete, pre_save, post_save
from django.dispatch import receiver

from app.models import *


# Role:---------------------------------------------------
@receiver(pre_save, sender=RoleModel)
def pre_save_role(sender, instance, *args, **kwargs):
    if not instance.pk:
        _parent = instance.parent
        if _parent:
            instance.order = _parent.order + 1

@receiver(post_save, sender=RoleModel)
def post_save_role(sender, instance=None, created=False, **kwargs):
    pass


@receiver(post_save, sender=UserModel)
def post_save_user(sender, instance=None, created=False, **kwargs):
    if created:
        try:
            _role = RoleModel.objects.get(title='client')
            UserRoleModel.objects.create(user=instance,role=_role)
        except:
            pass
